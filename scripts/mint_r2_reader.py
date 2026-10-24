#!/usr/bin/env python3
"""Issue a prefix-scoped R2 reader without sharing the parent writer secret."""
import argparse
import base64
from datetime import datetime,timezone
import hashlib
import hmac
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from lfs_r2_transfer import read_environment,TransferError


def encode(value):return base64.urlsafe_b64encode(value).rstrip(b'=').decode()


def mint(values,ttl=86400,now=None):
    if type(ttl) is not int or not 1<=ttl<=2592000:raise ValueError('Reader TTL must be 1–2592000 seconds')
    group='R2_ASSETS_' if values.get('R2_ASSETS_BUCKET') else 'R2_MEDIA_'
    required=['ACCOUNT_ID','BUCKET','ACCESS_KEY_ID','SECRET_ACCESS_KEY']
    if any(not values.get(group+key) for key in required):raise ValueError('Parent R2 credentials unavailable')
    if values.get(group+'SESSION_TOKEN'):raise ValueError('Mint from parent credentials, not an existing session')
    now=int(time.time()) if now is None else now
    account=values[group+'ACCOUNT_ID'];parent=values[group+'ACCESS_KEY_ID']
    prefix=values.get('R2_LFS_PREFIX','').strip('/')
    if not re.fullmatch(r'[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*',prefix):raise ValueError('Explicit safe prefix required')
    claims={'bucket':values[group+'BUCKET'],'scope':'object-read-only',
            'paths':{'prefixPaths':[prefix+'/'],'objectPaths':[]},'iss':parent,'sub':account,
            'aud':account+'.r2.cloudflarestorage.com','iat':now,'exp':now+ttl}
    header=encode(json.dumps({'alg':'HS256','typ':'JWT'},separators=(',',':')).encode())
    unsigned=header+'.'+encode(json.dumps(claims,separators=(',',':')).encode())
    jwt=unsigned+'.'+encode(hmac.new(values[group+'SECRET_ACCESS_KEY'].encode(),unsigned.encode(),hashlib.sha256).digest())
    return {'R2_ASSETS_ACCOUNT_ID':account,'R2_ASSETS_BUCKET':values[group+'BUCKET'],
            'R2_ASSETS_ACCESS_KEY_ID':parent,'R2_ASSETS_SECRET_ACCESS_KEY':hashlib.sha256(jwt.encode()).hexdigest(),
            'R2_ASSETS_SESSION_TOKEN':base64.b64encode(('jwt/'+jwt).encode()).decode(),'R2_LFS_PREFIX':prefix}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file',type=Path,required=True)
    parser.add_argument('--ttl-seconds',type=int,default=86400)
    target=parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--output',type=Path)
    target.add_argument('--github-repository')
    args=parser.parse_args()
    try:
        now=int(time.time());credentials=mint(read_environment(args.env_file),args.ttl_seconds,now)
        payload=json.dumps(credentials)
        if args.output:
            # Exclusive creation avoids replacing a user's existing credentials.
            with open(args.output,'x',opener=lambda p,flags:__import__('os').open(p,flags,0o600)) as stream:stream.write(payload+'\n')
        else:
            if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',args.github_repository):raise ValueError('Invalid GitHub repository')
            subprocess.run(['gh','secret','set','R2_LFS_READER','--repo',args.github_repository],
                           input=payload,text=True,check=True,capture_output=True)
        print(json.dumps({'status':'issued','scope':'prefix read-only','expires_at':datetime.fromtimestamp(now+args.ttl_seconds,timezone.utc).isoformat()}))
    except (ValueError,OSError,TransferError,subprocess.CalledProcessError):
        print('Reader issuance failed; credential values suppressed.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
