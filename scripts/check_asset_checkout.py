#!/usr/bin/env python3
"""Read-only offline preflight for required materialized Git LFS assets."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from lfs_pointer_format import normalize_pointer

ROOT=Path(__file__).resolve().parents[1]
ACTIVE=('blender/','export/','godot/','textures/')


def check(repo,profile='active',strict=False):
    if profile not in ('active','all'):raise ValueError('Unknown asset profile')
    repo=Path(repo).resolve()
    result=subprocess.run(['git','lfs','ls-files','--json','HEAD'],cwd=repo,capture_output=True)
    if result.returncode:raise ValueError('Cannot enumerate assets; install Git LFS and check repository setup')
    data=json.loads(result.stdout)
    if not isinstance(data,dict) or not isinstance(data.get('files'),list):raise ValueError('Unexpected Git LFS inventory format')
    errors=[];count=0
    for item in data['files']:
        name=item['name']
        if profile=='active' and not name.startswith(ACTIVE):continue
        count+=1;path=repo/name
        if not path.is_file():errors.append({'path':name,'reason':'missing'});continue
        try:
            with path.open('rb') as stream:prefix=stream.read(1024)
            if normalize_pointer(prefix) is not None:errors.append({'path':name,'reason':'pointer'});continue
            if strict:
                with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
                if path.stat().st_size!=item['size'] or digest!=item['oid']:
                    errors.append({'path':name,'reason':'hash_mismatch'})
        except OSError:errors.append({'path':name,'reason':'unreadable'})
    return {'status':'failed' if errors else 'passed','profile':profile,'strict':strict,
            'checked_assets':count,'errors':errors}


def require_assets(repo=ROOT,profile='active'):
    try:report=check(repo,profile)
    except (ValueError,OSError) as error:
        print('ASSET_CHECKOUT_FAIL: '+str(error),file=sys.stderr);raise SystemExit(1)
    if report['status']!='passed':
        for item in report['errors'][:20]:print('ASSET_CHECKOUT_FAIL: '+item['reason']+' '+item['path'],file=sys.stderr)
        print('Install/configure the R2 adapter, then run git lfs pull. Preflight never overwrites edited files.',file=sys.stderr)
        raise SystemExit(1)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=ROOT)
    parser.add_argument('--profile',choices=['active','all'],default='active')
    parser.add_argument('--strict',action='store_true')
    args=parser.parse_args()
    try:report=check(args.repo,args.profile,args.strict)
    except (ValueError,OSError) as error:
        print(str(error),file=sys.stderr);return 1
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
