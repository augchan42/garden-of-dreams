"""Trusted checker reads Git objects, including assets deleted before PR tip."""
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pointer_format_fixtures import pointer_cases
from test_lfs_storage_audit import GitFixture
from lfs_r2_transfer import Store
try:
 import check_r2_history as checker
except ImportError:checker=None


class HistoryTests(GitFixture):
 def setUp(self):
  super().setUp()
  self.assertIsNotNone(checker,'Trusted history checker is missing')
  self.git('commit','--allow-empty','-m','base')
  self.base=self.git('rev-parse','HEAD')
  config=self.root/'rclone.conf';config.write_text('[fixture]\ntype = local\n')
  self.store=Store(dict(os.environ,RCLONE_CONFIG=str(config),R2_LFS_REMOTE='fixture:'+str(self.root/'remote/project')))

 def test_intermediate_deleted_object_is_checked(self):
  oid,source=self.pointer('removed.bin')
  self.store.upload(source,oid,5)
  self.git('rm','removed.bin');self.git('commit','-m','remove')
  report=checker.verify(self.repo,self.base,self.git('rev-parse','HEAD'),self.store)
  self.assertEqual(report['status'],'passed')
  self.assertEqual([x['oid'] for x in report['objects']],[oid])

 def test_all_valid_pointer_formats_in_removed_history_are_checked(self):
  for index,(label,_) in enumerate(pointer_cases('0'*64,1)):
   with self.subTest(format=label):
    body=('history '+label).encode();oid=hashlib.sha256(body).hexdigest()
    pointer=dict(pointer_cases(oid,len(body)))[label]
    self.assertEqual(__import__('subprocess').run(['git','lfs','pointer','--check','--stdin'],input=pointer,capture_output=True).returncode,0)
    name=f'format-{index}.bin';(self.repo/name).write_bytes(pointer)
    self.git('add',name);self.git('commit','-m',label);self.git('rm',name);self.git('commit','-m','remove '+label)
    report=checker.verify(self.repo,self.base,'HEAD',self.store)
    self.assertIn(oid,{x['oid'] for x in report['objects'] if x['status']=='error'})

 def test_missing_crlf_intermediate_pointer_is_checked(self):
  oid=hashlib.sha256(b'crlf asset').hexdigest()
  pointer=f'version https://git-lfs.github.com/spec/v1\r\noid sha256:{oid}\r\nsize 10\r\n'.encode()
  (self.repo/'crlf.bin').write_bytes(pointer)
  self.git('add','crlf.bin');self.git('commit','-m','CRLF intermediate')
  self.git('rm','crlf.bin');self.git('commit','-m','remove CRLF pointer')
  result=checker.verify(self.repo,self.base,'HEAD',self.store)
  self.assertEqual(result['status'],'failed')
  self.assertEqual(result['counts'],{'ok':0,'error':1})
  self.assertEqual(result['objects'][0]['oid'],oid)

 def test_missing_intermediate_object_fails(self):
  self.pointer('removed.bin');self.git('rm','removed.bin');self.git('commit','-m','remove')
  report=checker.verify(self.repo,self.base,self.git('rev-parse','HEAD'),self.store)
  self.assertEqual(report['status'],'failed')
  self.assertEqual(report['counts'],{'ok':0,'error':1})

 def test_corrupt_object_fails(self):
  oid,_=self.pointer('bad.bin')
  path=self.root/'remote/project/objects/sha256'/oid[:2]/oid
  path.parent.mkdir(parents=True);path.write_bytes(b'bad')
  self.assertEqual(checker.verify(self.repo,self.base,'HEAD',self.store)['status'],'failed')

 def test_baseline_history_excluded_and_new_oids_deduplicated(self):
  self.pointer('old.bin');self.base=self.git('rev-parse','HEAD')
  oid,source=self.pointer('new.bin',b'new');self.pointer('duplicate.bin',b'new')
  self.store.upload(source,oid,3)
  report=checker.verify(self.repo,self.base,'HEAD',self.store)
  self.assertEqual(report['status'],'passed');self.assertEqual(report['counts']['ok'],1)

 def test_empty_revision_range_checks_zero_assets(self):
  report=checker.verify(self.repo,self.base,self.base,self.store)
  self.assertEqual(report['status'],'passed');self.assertEqual(report['counts'],{'ok':0,'error':0})

 def test_untrusted_checker_file_never_executed(self):
  script=self.repo/'malicious.py';script.write_text('raise RuntimeError("must not execute")')
  self.git('add','.');self.git('commit','-m','untrusted code')
  self.assertEqual(checker.verify(self.repo,self.base,'HEAD',self.store)['counts']['ok'],0)


if __name__=='__main__':unittest.main()
