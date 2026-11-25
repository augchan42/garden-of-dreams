#!/usr/bin/env python3
"""Install a pinned standalone adapter outside checkout; preserve clone settings."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

PROVIDER_URL = 'https://github.com/augchan42/garden-of-dreams/blob/main/docs/asset-storage.md'
HOOKS = ('pre-push', 'post-checkout', 'post-commit', 'post-merge')
SOURCE = Path(__file__).with_name('lfs_r2_transfer.py')


def git(repo, *args, allow_missing=False):
    p = subprocess.run(['git', *args], cwd=repo, capture_output=True)
    if p.returncode:
        if allow_missing and p.returncode == 1:return b''
        raise ValueError('Git setup operation failed: '+args[0])
    return p.stdout


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def private_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n');path.chmod(0o600)


def templates():
    with tempfile.TemporaryDirectory(prefix='garden-lfs-hooks-') as directory:
        repo = Path(directory)
        git(repo, 'init')
        git(repo, 'lfs', 'install', '--local')
        return {name: (repo/'.git/hooks'/name).read_bytes() for name in HOOKS}


def install(repo, profile='active', install_root=None, env_file=None, provider_url=PROVIDER_URL):
    repo = Path(repo).resolve()
    if profile not in ('active', 'all'):raise ValueError('Unknown asset profile')
    if not (3, 11) <= sys.version_info[:2] < (3, 15):raise ValueError('Python3.11–3.14 required')
    gitdir = Path(git(repo, 'rev-parse', '--absolute-git-dir').decode().strip())
    common = Path(git(repo, 'rev-parse', '--git-common-dir').decode().strip())
    if not common.is_absolute():common = (repo/common).resolve()
    if gitdir.resolve() != common.resolve():raise ValueError('Linked worktrees share configuration; install in a standalone clone at cutover')
    if git(repo, 'config', '--get', 'core.hooksPath', allow_missing=True).strip():
        raise ValueError('Custom core.hooksPath preserved; integrate LFS hooks manually before bootstrap')
    expected = templates()
    hooks = gitdir/'hooks'
    before_hooks = {}
    for name in HOOKS:
        path = hooks/name
        if path.exists():
            content = path.read_bytes()
            if content != expected[name]:raise ValueError('Existing custom '+name+' hook preserved; integrate LFS manually')
            before_hooks[name] = base64.b64encode(content).decode()
        else:before_hooks[name] = None
    if env_file:
        env_file = Path(env_file).resolve()
        if not env_file.is_file():raise ValueError('Private credential file unavailable')
    root = Path(install_root or Path.home()/'.local/share/garden-lfs').resolve()
    if root == repo or repo in root.parents:raise ValueError('Install adapter outside checkout')
    body = SOURCE.read_bytes();identity = hashlib.sha256(body).hexdigest()
    versioned = root/('adapter-'+identity[:16]);versioned.mkdir(parents=True, exist_ok=True)
    installed = versioned/'lfs_r2_transfer.py'
    if installed.exists() and installed.read_bytes() != body:raise ValueError('Installed adapter identity collision')
    installed.write_bytes(body)
    config = gitdir/'config'
    before_config = config.read_bytes()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    state = root/'settings'/hashlib.sha256(str(repo).encode()).hexdigest()[:16]/(stamp+'.json')
    snapshot = {'schema_version': 1, 'repo': str(repo), 'gitdir': str(gitdir),
                'config_before_base64': base64.b64encode(before_config).decode(),
                'hooks_before_base64': before_hooks}
    try:
        git(repo, 'lfs', 'install', '--local')
        args = shlex.quote(str(installed))
        if env_file:args += ' --env-file '+shlex.quote(str(env_file))
        values = {'lfs.standalonetransferagent': 'garden-r2',
                  'lfs.customtransfer.garden-r2.path': sys.executable,
                  'lfs.customtransfer.garden-r2.args': args,
                  'lfs.customtransfer.garden-r2.concurrent': 'true',
                  'lfs.concurrenttransfers': '4', 'lfs.locksverify': 'false',
                  'lfs.url': provider_url, 'lfs.fetchexclude': '',
                  'lfs.fetchinclude': 'blender/**,export/**,godot/**,textures/**' if profile == 'active' else ''}
        for key, value in values.items():git(repo, 'config', '--local', key, value)
        snapshot['config_after_sha256'] = digest(config)
        snapshot['hooks_after_sha256'] = {name:digest(hooks/name) for name in HOOKS}
        private_json(state, snapshot)
    except BaseException:
        config.write_bytes(before_config)
        for name, old in before_hooks.items():
            path = hooks/name
            if old is None:path.unlink(missing_ok=True)
            else:path.write_bytes(base64.b64decode(old))
        raise
    return {'status': 'installed', 'adapter': str(installed), 'adapter_sha256': identity,
            'snapshot': str(state), 'profile': profile}


def restore(snapshot_path):
    state = json.loads(Path(snapshot_path).read_text())
    if state.get('schema_version') != 1:raise ValueError('Unknown settings snapshot')
    gitdir = Path(state['gitdir']);config = gitdir/'config';hooks = gitdir/'hooks'
    if digest(config) != state['config_after_sha256']:raise ValueError('Clone settings changed since install; preserve user edits')
    for name, expected in state['hooks_after_sha256'].items():
        path = hooks/name
        if not path.is_file() or digest(path) != expected:raise ValueError('Hook changed since install; preserve user edits')
    config.write_bytes(base64.b64decode(state['config_before_base64']))
    for name, value in state['hooks_before_base64'].items():
        path = hooks/name
        if value is None:path.unlink()
        else:path.write_bytes(base64.b64decode(value))
    return {'status': 'restored'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--profile', choices=['active', 'all'], default='active')
    parser.add_argument('--install-root', type=Path)
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--restore', type=Path)
    args = parser.parse_args()
    try:
        result = restore(args.restore) if args.restore else install(args.repo,args.profile,args.install_root,args.env_file)
        print(json.dumps(result))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr);return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
