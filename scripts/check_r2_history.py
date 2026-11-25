#!/usr/bin/env python3
"""Verify new historical LFS pointer blobs using trusted code and reader access."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import sys

from audit_lfs_storage import git,pointer_objects,save
from lfs_r2_transfer import Store,TransferError,read_environment


def commit(repo,revision):
    # Resolve first, so no caller-controlled Git options reach rev-list.
    if not isinstance(revision,str) or re.fullmatch(r'[A-Za-z0-9_./-]+',revision) is None or revision.startswith('-'):
        raise ValueError('Invalid commit reference')
    return git(repo,'rev-parse','--verify',revision+'^{commit}').decode().strip()


def verify(repo,base,head,store):
    base,head=commit(repo,base),commit(repo,head)
    objects=pointer_objects(repo,head,'--not',base)
    def check(item):
        oid,size=item
        try:
            temporary=store.fetch(oid,size);temporary.unlink()
            return {'oid':oid,'size':size,'status':'ok','readback_sha256_verified':True}
        except TransferError as error:
            return {'oid':oid,'size':size,'status':'error','error':str(error)}
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,sorted(objects.items())))
    counts={key:sum(x['status']==key for x in rows) for key in ('ok','error')}
    return {'schema_version':1,'status':'passed' if counts['error']==0 else 'failed',
            'base':base,'head':head,'counts':counts,'objects':rows,
            'verified_bytes':sum(x['size'] for x in rows if x['status']=='ok')}


def reader_environment():
    if not os.environ.get('R2_LFS_READER'):return read_environment()
    data=json.loads(os.environ['R2_LFS_READER'])
    allowed={'R2_ASSETS_ACCOUNT_ID','R2_ASSETS_BUCKET','R2_ASSETS_ACCESS_KEY_ID',
             'R2_ASSETS_SECRET_ACCESS_KEY','R2_ASSETS_SESSION_TOKEN','R2_LFS_PREFIX'}
    if not isinstance(data,dict) or set(data)!=allowed or any(not isinstance(v,str) or not v for v in data.values()):
        raise ValueError('Invalid scoped reader configuration')
    return dict(os.environ,**data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path.cwd())
    parser.add_argument('--base',required=True);parser.add_argument('--head',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:report=verify(args.repo,args.base,args.head,Store(reader_environment()))
    except (ValueError,OSError,TransferError):
        print('Asset integrity failed; check refs and scoped reader access. Credentials suppressed.',file=sys.stderr);return 1
    save(args.output,report)
    print(json.dumps({k:report[k] for k in ('status','counts','verified_bytes')}))
    return 0 if report['status']=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
