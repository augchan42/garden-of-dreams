#!/usr/bin/env python3
"""Audit retained Git LFS history and create verified recovery copies."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

OID = re.compile(r'[0-9a-f]{64}')
HEADER = b'version https://git-lfs.github.com/spec/v1\n'


def git(repo, *args, input=None):
    result = subprocess.run(['git', *args], cwd=repo, input=input, capture_output=True)
    if result.returncode:
        raise ValueError('Git operation failed: ' + ' '.join(args[:2]))
    return result.stdout


def captured_refs(repo):
    refs = {}
    for line in git(repo, 'for-each-ref', '--format=%(refname) %(objectname)').decode().splitlines():
        name, oid = line.split()
        # App diff checkpoints are transient, not collaborator publishing refs.
        if not name.startswith('refs/codex/'):
            refs[name] = oid
    refs['HEAD'] = git(repo, 'rev-parse', 'HEAD').decode().strip()
    for index, line in enumerate(git(repo, 'worktree', 'list', '--porcelain').decode().splitlines()):
        if line.startswith('HEAD '):refs[f'worktree-head:{index}'] = line[5:]
    return refs


def cache_root(repo):
    for line in git(repo, 'lfs', 'env').decode().splitlines():
        if line.startswith('LocalMediaDir='):return Path(line.split('=', 1)[1]).resolve()
    raise ValueError('Git LFS cache location unavailable')


def object_path(cache, oid):
    if not isinstance(oid, str) or OID.fullmatch(oid) is None:
        raise ValueError('Invalid LFS OID')
    return Path(cache) / oid[:2] / oid[2:4] / oid


def pointer_objects(repo, *revisions):
    """Read pointer blobs from Git without checking out or executing revision code."""
    listed = git(repo, 'rev-list', '--objects', *revisions).splitlines()
    ids = sorted({line.split(b' ', 1)[0] for line in listed})
    metadata = git(repo, 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)',
                   input=b'\n'.join(ids)+b'\n').splitlines()
    small = []
    for line in metadata:
        parts = line.split()
        if len(parts) != 3:raise ValueError('Incomplete Git object enumeration')
        if parts[1] == b'blob' and int(parts[2]) <= 1024:small.append(parts[0])
    content = git(repo, 'cat-file', '--batch', input=b'\n'.join(small)+b'\n') if small else b''
    offset = 0
    objects = {}
    for expected in small:
        end = content.find(b'\n', offset)
        if end < 0:raise ValueError('Incomplete Git pointer read')
        header = content[offset:end].split()
        if len(header) != 3 or header[0] != expected or header[1] != b'blob':
            raise ValueError('Unexpected Git pointer response')
        size = int(header[2]);offset = end+1
        body = content[offset:offset+size];offset += size+1
        if len(body) != size:raise ValueError('Truncated Git pointer')
        if not body.startswith(HEADER):continue
        match = re.search(rb'^oid sha256:([0-9a-f]{64})$', body, re.M)
        length = re.search(rb'^size ([0-9]+)$', body, re.M)
        if match is None or length is None:raise ValueError('Malformed LFS pointer')
        oid, count = match[1].decode(), int(length[1])
        if oid in objects and objects[oid] != count:raise ValueError('Inconsistent LFS object size')
        objects[oid] = count
    return objects


def inventory(repo):
    repo = Path(repo).resolve()
    refs = captured_refs(repo)
    commits = sorted(set(refs.values()))
    objects = pointer_objects(repo, *commits)
    if captured_refs(repo) != refs:raise ValueError('Refs changed during inventory; capture again')
    cache = cache_root(repo)
    cached = {p.name for p in cache.glob('*/*/*') if p.is_file() and OID.fullmatch(p.name)}
    return {'schema_version': 1, 'complete': True, 'captured_at': datetime.now(timezone.utc).isoformat(),
            'repo': str(repo), 'cache': str(cache), 'refs': refs,
            'transient_ref_policy': 'refs/codex diff checkpoints excluded; cache-only bytes retained in recovery',
            'objects': [{'oid': oid, 'size': objects[oid]} for oid in sorted(objects)],
            'object_count': len(objects), 'object_bytes': sum(objects.values()),
            'cache_only_oids': sorted(cached - objects.keys())}


def validate_report(report):
    if report.get('schema_version') != 1 or report.get('complete') is not True or not report.get('refs'):
        raise ValueError('Complete schema-1 inventory required')
    seen = set()
    for item in report.get('objects', []):
        oid, size = item.get('oid'), item.get('size')
        object_path(report['cache'], oid)
        if type(size) is not int or size < 0 or oid in seen:raise ValueError('Invalid inventory object')
        seen.add(oid)
    if len(seen) != report.get('object_count') or sum(x['size'] for x in report['objects']) != report.get('object_bytes'):
        raise ValueError('Incomplete inventory totals')


def inspect(path, oid, size):
    try:
        with path.open('rb') as stream:digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if path.stat().st_size != size or digest != oid:return {'oid': oid, 'status': 'corrupt'}
        return {'oid': oid, 'status': 'ok', 'size': size}
    except FileNotFoundError:return {'oid': oid, 'status': 'missing'}
    except OSError:return {'oid': oid, 'status': 'error'}


def verify_local(report, jobs=2):
    validate_report(report)
    def check(item):return inspect(object_path(report['cache'], item['oid']), item['oid'], item['size'])
    with ThreadPoolExecutor(max_workers=min(max(jobs, 1), 4)) as pool:
        rows = list(pool.map(check, report['objects']))
    counts = {key: sum(x['status'] == key for x in rows) for key in ('ok', 'missing', 'corrupt', 'error')}
    return {'schema_version': 1, 'status': 'passed' if counts['ok'] == len(rows) else 'failed',
            'counts': counts, 'verified_bytes': sum(x.get('size', 0) for x in rows), 'objects': rows}


def save(path, value):
    path = Path(path);path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n')


def backup(report, destination):
    validate_report(report)
    repo, cache, destination = Path(report['repo']), Path(report['cache']), Path(destination).resolve()
    if captured_refs(repo) != report['refs']:raise ValueError('Refs changed before backup')
    if destination == cache or cache in destination.parents or destination in cache.parents:
        raise ValueError('Recovery destination must be separate from live cache')
    destination.mkdir(parents=True, exist_ok=True)
    bundle = destination/'refs.bundle'
    # Each snapshot has one immutable refs capture; a changed capture uses a new directory.
    saved = destination/'inventory.json'
    if saved.exists() and json.loads(saved.read_text())['refs'] != report['refs']:
        raise ValueError('Recovery destination belongs to another refs capture')
    save(saved, report)
    if not bundle.exists():git(repo, 'bundle', 'create', str(bundle), '--all')
    git(repo, 'bundle', 'verify', str(bundle))
    bundled = {line.split()[1]: line.split()[0] for line in git(repo, 'bundle', 'list-heads', str(bundle)).decode().splitlines()}
    for ref, oid in report['refs'].items():
        if ref.startswith('refs/') and bundled.get(ref) != oid:raise ValueError('Backup bundle omits retained ref')
    items = {x['oid']: x['size'] for x in report['objects']}
    for oid in report['cache_only_oids']:
        source = object_path(cache, oid)
        if not source.is_file():raise ValueError('Cache-only object disappeared')
        items.setdefault(oid, source.stat().st_size)
    records = []
    for oid, size in sorted(items.items()):
        source, target = object_path(cache, oid), object_path(destination/'objects', oid)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_suffix('.partial')
            shutil.copyfile(source, temporary)
            if inspect(temporary, oid, size)['status'] != 'ok':
                temporary.unlink(missing_ok=True)
                raise ValueError('Recovery copy failed integrity verification')
            temporary.replace(target)
        result = inspect(target, oid, size)
        if result['status'] != 'ok':raise ValueError('Existing recovery copy failed verification')
        records.append(result)
    if captured_refs(repo) != report['refs']:raise ValueError('Refs changed during backup; capture final delta')
    result = {'schema_version': 1, 'status': 'passed', 'objects_copied': len(records),
              'bytes_verified': sum(items.values()), 'objects': records,
              'bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
              'failure_domain': 'Independent copied bytes outside production R2; local destination may share workstation/disk with source'}
    save(destination/'recovery.json', result)
    return result


def remote_operation(report, store, verify_only=False, jobs=4, journal=None):
    validate_report(report)
    if captured_refs(report['repo']) != report['refs']:
        raise ValueError('Refs changed before remote operation; capture explicit delta')
    rows = []
    provider = hashlib.sha256(store.remote.encode()).hexdigest()
    def work(item):
        oid,size=item['oid'],item['size']
        try:
            if verify_only:
                temporary=store.fetch(oid,size)
                temporary.unlink()
            else:
                store.upload(object_path(report['cache'],oid),oid,size)
            return {'oid':oid,'size':size,'status':'ok','readback_sha256_verified':True}
        except Exception as error:
            return {'oid':oid,'size':size,'status':'error','error_type':type(error).__name__}
    stream=None
    if journal is not None:
        journal=Path(journal);journal.parent.mkdir(parents=True,exist_ok=True)
        stream=journal.open('a')
    try:
        with ThreadPoolExecutor(max_workers=min(max(jobs,1),4)) as pool:
            futures=[pool.submit(work,item) for item in report['objects']]
            for future in as_completed(futures):
                row=future.result();rows.append(row)
                if stream:
                    stream.write(json.dumps(dict(row,provider_id=provider))+'\n');stream.flush()
                if len(rows)%100==0:
                    print(json.dumps({'remote_operation':'verify' if verify_only else 'copy',
                                      'processed':len(rows),'total':len(report['objects']),
                                      'errors':sum(x['status']=='error' for x in rows)}),flush=True)
    finally:
        if stream:stream.close()
    errors=sum(x['status']=='error' for x in rows)
    changed=captured_refs(report['repo']) != report['refs']
    return {'schema_version':1,'status':'failed' if errors else ('needs_delta' if changed else 'passed'),
            'provider_id':provider,'source_refs':report['refs'],'refs_changed':changed,
            'counts':{'ok':len(rows)-errors,'error':errors},
            'verified_bytes':sum(x['size'] for x in rows if x['status']=='ok'),
            'objects':sorted(rows,key=lambda x:x['oid'])}


def copy_objects(report, store, jobs=4, journal=None):
    return remote_operation(report,store,False,jobs,journal)


def verify_remote(report, store, jobs=4, journal=None):
    return remote_operation(report,store,True,jobs,journal)


def bulk_copy_objects(report, store, workspace):
    """Persistent bounded S3 sessions; success requires complete downloaded SHA256s."""
    from lfs_r2_transfer import checked_file
    validate_report(report)
    if captured_refs(report['repo']) != report['refs']:
        raise ValueError('Refs changed before bulk copy; capture explicit delta')
    workspace=Path(workspace).resolve();workspace.mkdir(parents=True,exist_ok=True)
    stage,download=workspace/'upload',workspace/'readback'
    stage.mkdir(exist_ok=True);download.mkdir(exist_ok=True)
    names=[];local=[]
    for item in report['objects']:
        oid,size=item['oid'],item['size'];source=object_path(report['cache'],oid)
        try:checked_file(source,oid,size)
        except Exception as error:
            local.append({'oid':oid,'size':size,'status':'error','error_type':type(error).__name__})
            continue
        name=oid[:2]+'/'+oid;names.append(name);target=stage/name
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            try:checked_file(target,oid,size)
            except Exception:target.unlink()
        if not target.exists():
            try:
                import os
                os.link(source,target)
            except OSError:shutil.copyfile(source,target)
    if local:
        return {'schema_version':1,'status':'failed','counts':{'ok':0,'error':len(local)},'objects':local}
    listing=workspace/'files.txt';listing.write_text(''.join(x+'\n' for x in names))
    save(workspace/'phase.json',{'phase':'upload','expected_objects':len(names),'expected_bytes':report['object_bytes']})
    upload_log=workspace/'upload.log';upload_log.touch(mode=0o600,exist_ok=True)
    upload_code=store.run(['copy',str(stage),store.remote+'/objects/sha256','--files-from-raw',str(listing),
                           '--immutable','--log-file',str(upload_log),'--use-json-log',
                           '--stats','30s','--stats-log-level','NOTICE'],transfers=4,wall_timeout=43200)
    save(workspace/'phase.json',{'phase':'readback','upload_exit_code':upload_code,'expected_objects':len(names)})
    download_log=workspace/'readback.log';download_log.touch(mode=0o600,exist_ok=True)
    download_code=store.run(['copy',store.remote+'/objects/sha256',str(download),'--files-from-raw',str(listing),
                             '--ignore-times','--log-file',str(download_log),'--use-json-log',
                             '--stats','30s','--stats-log-level','NOTICE'],transfers=4,wall_timeout=43200)
    rows=[]
    for item in report['objects']:
        oid,size=item['oid'],item['size'];path=download/oid[:2]/oid
        row=inspect(path,oid,size)
        row.update(size=size,readback_sha256_verified=row['status']=='ok');rows.append(row)
    errors=sum(row['status']!='ok' for row in rows)
    changed=captured_refs(report['repo']) != report['refs']
    result={'schema_version':1,'status':'failed' if errors or upload_code or download_code else ('needs_delta' if changed else 'passed'),
            'provider_id':hashlib.sha256(store.remote.encode()).hexdigest(),'source_refs':report['refs'],
            'refs_changed':changed,'upload_exit_code':upload_code,'download_exit_code':download_code,
            'counts':{'ok':len(rows)-errors,'error':errors},
            'verified_bytes':sum(x['size'] for x in rows if x['status']=='ok'),'objects':rows}
    save(workspace/'phase.json',{'phase':'complete','status':result['status'],'counts':result['counts']})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['inventory', 'verify-local', 'backup', 'copy', 'verify-remote'])
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--refs', choices=['all'], default='all')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--bulk', action='store_true')
    args = parser.parse_args()
    if args.operation == 'inventory':result = inventory(args.repo)
    else:
        if args.report is None:parser.error('--report required')
        report = json.loads(args.report.read_text())
        if args.operation == 'verify-local':result = verify_local(report)
        elif args.operation == 'backup':
            if args.destination is None:parser.error('--destination required')
            result = backup(report, args.destination)
        else:
            from lfs_r2_transfer import Store, read_environment
            store=Store(read_environment(args.env_file))
            operation=copy_objects if args.operation == 'copy' else verify_remote
            if args.bulk and args.operation == 'copy':
                result=bulk_copy_objects(report,store,args.output.with_suffix('.work'))
            else:
                result=operation(report,store,journal=args.output.with_suffix('.jsonl'))
    save(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k in ('status', 'complete', 'object_count', 'object_bytes', 'counts', 'objects_copied', 'bytes_verified')}))
    if result.get('status') == 'failed':sys.exit(1)
    if result.get('status') == 'needs_delta':sys.exit(2)


if __name__ == '__main__':main()
