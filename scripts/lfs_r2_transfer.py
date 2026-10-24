#!/usr/bin/env python3
"""Git LFS standalone transfers with immutable, verified R2 object storage.

Only protocol JSON is emitted on stdout. Credentials are loaded from an explicit
private environment file or process environment; no GitHub fallback exists.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile

RCLONE_VERSION = 'v1.75.0'
OID = re.compile(r'[0-9a-f]{64}')


class TransferError(Exception):pass
class MissingObject(TransferError):pass


def read_environment(path=None):
    values = dict(os.environ)
    filename = path or values.get('R2_LFS_ENV_FILE')
    if filename:
        try:
            for line in Path(filename).read_text().splitlines():
                text = line.strip().removeprefix('export ').strip()
                if not text or text.startswith('#') or '=' not in text:continue
                key, raw = text.split('=', 1);key = key.strip()
                if key.startswith(('CF_', 'R2_')):
                    # Parse values as data. Never source shell code or expand it.
                    values.setdefault(key, ' '.join(shlex.split(raw, comments=True)))
        except (OSError, ValueError):raise TransferError('Cannot read private R2 configuration') from None
    return values


def checked_file(path, oid, size):
    try:
        with Path(path).open('rb') as stream:digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if Path(path).stat().st_size != size or digest != oid:raise TransferError('Object size or SHA-256 mismatch')
    except OSError:raise TransferError('Object file unavailable') from None


class Store:
    def __init__(self, values=None):
        self.env = dict(values if values is not None else read_environment())
        self.rclone = self.env.get('R2_LFS_RCLONE') or shutil.which('rclone')
        if not self.rclone:raise TransferError('Pinned rclone executable unavailable; run bootstrap')
        self.remote = self.env.get('R2_LFS_REMOTE')
        if not self.remote:
            group = 'R2_ASSETS_' if self.env.get('R2_ASSETS_BUCKET') else 'R2_MEDIA_'
            required = ['ACCOUNT_ID', 'BUCKET', 'ACCESS_KEY_ID', 'SECRET_ACCESS_KEY']
            if any(not self.env.get(group+x) for x in required):raise TransferError('R2 credential configuration unavailable')
            account = self.env[group+'ACCOUNT_ID']
            self.env.update({'RCLONE_CONFIG_GARDENASSETS_TYPE': 's3',
                'RCLONE_CONFIG_GARDENASSETS_PROVIDER': 'Cloudflare',
                'RCLONE_CONFIG_GARDENASSETS_ACCESS_KEY_ID': self.env[group+'ACCESS_KEY_ID'],
                'RCLONE_CONFIG_GARDENASSETS_SECRET_ACCESS_KEY': self.env[group+'SECRET_ACCESS_KEY'],
                'RCLONE_CONFIG_GARDENASSETS_ENDPOINT': 'https://'+account+'.r2.cloudflarestorage.com',
                'RCLONE_CONFIG_GARDENASSETS_REGION': 'auto',
                'RCLONE_CONFIG_GARDENASSETS_NO_CHECK_BUCKET': 'true'})
            if self.env.get(group+'SESSION_TOKEN'):
                self.env['RCLONE_CONFIG_GARDENASSETS_SESSION_TOKEN']=self.env[group+'SESSION_TOKEN']
            prefix=self.env.get('R2_LFS_PREFIX','').strip('/')
            if not re.fullmatch(r'[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*',prefix):
                raise TransferError('Explicit safe object-storage prefix required')
            self.remote = 'gardenassets:'+self.env[group+'BUCKET']+'/'+prefix
        if (not re.fullmatch(r'[A-Za-z0-9_-]+:[^\s]+/[^\s]+', self.remote)
                or any(part in ('.', '..') for part in self.remote.split('/'))):
            raise TransferError('Explicit safe object-storage prefix required')
        self.remote = self.remote.rstrip('/')
        self._version_checked = False

    def version(self):
        if not self._version_checked:
            try:p = subprocess.run([self.rclone, 'version'], env=self.env, capture_output=True, timeout=15)
            except (OSError, subprocess.TimeoutExpired):raise TransferError('Rclone executable unavailable') from None
            if p.returncode or p.stdout.decode(errors='replace').splitlines()[0] != 'rclone '+RCLONE_VERSION:
                raise TransferError('Unsupported rclone version; run bootstrap for the pinned version')
            self._version_checked = True

    def run(self, args, output=None, transfers=1, wall_timeout=1200):
        self.version()
        command = [self.rclone, *args, '--retries', '3', '--low-level-retries', '3',
                   '--contimeout', '15s', '--timeout', '120s', '--transfers', str(min(max(transfers,1),4)), '--checkers', '4', '--retries-sleep', '1s',
                   '--s3-upload-cutoff', '64Mi', '--s3-chunk-size', '16Mi', '--s3-upload-concurrency', '2',
                   '--s3-leave-parts-on-error=false']
        try:
            process = subprocess.Popen(command, env=self.env, stdin=subprocess.DEVNULL,
                        stdout=output if output is not None else subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, start_new_session=True)
        except OSError:raise TransferError('Storage transport unavailable') from None
        try:return process.wait(timeout=wall_timeout)
        except BaseException:
            # Give rclone time to abort multipart work on interruption.
            os.killpg(process.pid, signal.SIGINT)
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL);process.wait()
            raise TransferError('Storage transfer interrupted') from None

    def key(self, oid):
        if not isinstance(oid, str) or OID.fullmatch(oid) is None:raise TransferError('Invalid SHA-256 object identifier')
        return self.remote+'/objects/sha256/'+oid[:2]+'/'+oid

    def fetch(self, oid, size):
        remote = self.key(oid)
        descriptor, filename = tempfile.mkstemp(prefix='garden-lfs-')
        try:
            with os.fdopen(descriptor, 'wb') as output:code = self.run(['lsjson', remote, '--stat'], output)
            if code in (3, 4):raise MissingObject('Object absent from R2')
            if code:raise TransferError('Object metadata unavailable; check access')
            try:metadata = json.loads(Path(filename).read_text())
            except (ValueError, OSError):raise TransferError('Invalid object metadata') from None
            if isinstance(metadata, dict) and metadata.get('IsDir') is True:raise MissingObject('Exact object absent from R2')
            if not isinstance(metadata, dict) or metadata.get('IsDir') is not False:raise TransferError('Invalid object metadata')
            if self.run(['copyto', remote, filename, '--ignore-times']):raise TransferError('Object download failed')
            checked_file(filename, oid, size)
            return Path(filename)
        except BaseException:
            Path(filename).unlink(missing_ok=True)
            raise

    def upload(self, source, oid, size):
        checked_file(source, oid, size)
        remote = self.key(oid)
        try:existing = self.fetch(oid, size)
        except MissingObject:existing = None
        if existing is not None:
            existing.unlink();return
        if self.run(['copyto', str(source), remote, '--immutable']):raise TransferError('Object upload failed')
        verified = self.fetch(oid, size)
        verified.unlink()


def validate_request(request):
    oid, size = request.get('oid'), request.get('size')
    if not isinstance(oid, str) or OID.fullmatch(oid) is None:raise TransferError('Invalid SHA-256 object identifier')
    if type(size) is not int or size < 0:raise TransferError('Invalid object size')
    return oid, size


def emit(value):print(json.dumps(value, separators=(',', ':')), flush=True)


def protocol(values):
    operation, store = None, None
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if not isinstance(request, dict):raise ValueError()
        except ValueError:
            emit({'error': {'code': 1, 'message': 'Invalid protocol JSON'}});return 1
        event = request.get('event')
        if event == 'terminate':return 0
        if event == 'init':
            if operation is not None or request.get('operation') not in ('upload', 'download'):
                emit({'error': {'code': 1, 'message': 'Invalid transfer initialization'}});return 1
            operation = request['operation'];emit({});continue
        result = {'event': 'complete', 'oid': request.get('oid')}
        try:
            if operation is None or event != operation:raise TransferError('Operation does not match initialization')
            oid, size = validate_request(request)
            if store is None:store = Store(values)
            if operation == 'upload':
                source = request.get('path')
                if not isinstance(source, str):raise TransferError('Upload source required')
                store.upload(source, oid, size)
            else:result['path'] = str(store.fetch(oid, size))
        except TransferError as error:result['error'] = {'code': 1, 'message': str(error)}
        except Exception:result['error'] = {'code': 1, 'message': 'Transfer failed; configuration and credentials suppressed'}
        emit(result)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file')
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(InterruptedError()))
    try:return protocol(read_environment(args.env_file))
    except TransferError as error:
        emit({'error': {'code': 1, 'message': str(error)}});return 1


if __name__=='__main__':raise SystemExit(main())
