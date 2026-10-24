"""Real Git/LFS operations verify profiles, old revisions and dirty-file safety."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap_lfs_r2 import install
from check_asset_checkout import check


class GitWorkflowTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
  config=self.root/'rclone.conf';config.write_text('[fixture]\ntype = local\n')
  self.env=dict(os.environ,RCLONE_CONFIG=str(config))
  self.private=self.root/'private.env'
  self.private.write_text('R2_LFS_REMOTE='+shlex.quote('fixture:'+str(self.root/'storage/project'))+'\n')
  self.writer=self.root/'writer';self.writer.mkdir()
  self.git(self.writer,'init','-b','main')
  self.git(self.writer,'config','user.name','Migration workflow tests')
  self.git(self.writer,'config','user.email','tests@localhost.invalid')
  install(self.writer,install_root=self.root/'installed',env_file=self.private)
  self.origin=self.root/'origin.git';self.git(self.root,'init','--bare',str(self.origin))
  self.git(self.writer,'remote','add','origin',str(self.origin))
  (self.writer/'.gitattributes').write_text('*.blend filter=lfs diff=lfs merge=lfs -text\n*.png filter=lfs diff=lfs merge=lfs -text\n')
  for name,body in {'blender/scene.blend':b'old blend','textures/color.png':b'old png','docs/ref.png':b'reference png'}.items():
   path=self.writer/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
  self.git(self.writer,'add','.');self.git(self.writer,'commit','-m','old assets')
  self.old=self.git(self.writer,'rev-parse','HEAD').stdout.strip()
  (self.writer/'blender/scene.blend').write_bytes(b'new blend')
  (self.writer/'textures/color.png').write_bytes(b'new png')
  self.git(self.writer,'add','.');self.git(self.writer,'commit','-m','new assets')
  self.git(self.writer,'push','-u','origin','main')
  self.reader=self.root/'reader'
  self.git(self.root,'clone','--no-checkout','--branch','main',str(self.origin),str(self.reader),skip=True)
  self.settings=install(self.reader,install_root=self.root/'installed',env_file=self.private)
  self.git(self.reader,'checkout','main',skip=True)
  self.assertFalse(any((self.reader/'.git/lfs/objects').glob('*/*/*')))
  self.git(self.reader,'lfs','pull')

 def git(self,repo,*args,skip=False,check_code=True):
  env=dict(self.env)
  if skip:env['GIT_LFS_SKIP_SMUDGE']='1'
  result=subprocess.run(['git',*args],cwd=repo,env=env,text=True,capture_output=True,timeout=60)
  if check_code:self.assertEqual(result.returncode,0,result.stderr)
  return result

 def test_selective_then_full_profile(self):
  self.assertEqual((self.reader/'blender/scene.blend').read_bytes(),b'new blend')
  reference=self.reader/'docs/ref.png'
  self.assertTrue(reference.read_bytes().startswith(b'version https://git-lfs.github.com/spec/v1\n'))
  self.assertEqual(check(self.reader,'active',True)['status'],'passed')
  self.assertEqual(check(self.reader,'all',True)['status'],'failed')
  install(self.reader,profile='all',install_root=self.root/'installed',env_file=self.private)
  self.git(self.reader,'lfs','pull')
  self.assertEqual(reference.read_bytes(),b'reference png')
  self.assertEqual(check(self.reader,'all',True)['status'],'passed')

 def test_dirty_blender_and_png_prevent_branch_switch(self):
  for name in ('blender/scene.blend','textures/color.png'):
   with self.subTest(name=name):
    path=self.reader/name;original=path.read_bytes();path.write_bytes(b'local unsaved work')
    result=self.git(self.reader,'checkout','--detach',self.old,check_code=False)
    self.assertNotEqual(result.returncode,0)
    self.assertEqual(path.read_bytes(),b'local unsaved work')
    path.write_bytes(original)

 def test_installed_adapter_survives_old_revision(self):
  self.assertFalse((self.reader/'scripts/lfs_r2_transfer.py').exists())
  self.git(self.reader,'checkout','--detach',self.old)
  self.assertEqual((self.reader/'blender/scene.blend').read_bytes(),b'old blend')
  self.assertEqual((self.reader/'textures/color.png').read_bytes(),b'old png')
  self.assertTrue(Path(self.settings['adapter']).is_file())
  self.assertEqual(check(self.reader,'active',True)['status'],'passed')


if __name__=='__main__':unittest.main()
