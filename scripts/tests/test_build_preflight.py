"""Pointer-only inputs must fail before outputs or native staging are created."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

class BuildPreflightTests(unittest.TestCase):
    def test_pointer_checkout_stops_each_build_entry_before_native_work(self):
        source=Path(__file__).resolve().parents[1]
        for entry in ('verify_assets.py','verify_godot_reimport.py','build_android_profile.py'):
            with self.subTest(entry=entry),tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                shutil.copytree(source,root/'scripts',ignore=shutil.ignore_patterns('__pycache__','tests'))
                subprocess.run(['git','init','-b','main'],cwd=root,check=True,capture_output=True)
                subprocess.run(['git','config','user.name','Preflight test'],cwd=root,check=True)
                subprocess.run(['git','config','user.email','test@localhost.invalid'],cwd=root,check=True)
                asset=root/'godot/assets/source.bin';asset.parent.mkdir(parents=True)
                oid=hashlib.sha256(b'asset').hexdigest()
                asset.write_text(f'version https://git-lfs.github.com/spec/v1\noid sha256:{oid}\nsize 5\n')
                (root/'.gitattributes').write_text('*.bin filter=lfs diff=lfs merge=lfs -text\n')
                subprocess.run(['git','add','.gitattributes','godot'],cwd=root,check=True,capture_output=True)
                subprocess.run(['git','commit','-m','pointer'],cwd=root,check=True,capture_output=True)
                temporary=root/'native-temp';temporary.mkdir()
                result=subprocess.run([sys.executable,str(root/'scripts'/entry)],cwd=root,env=dict(os.environ,TMPDIR=str(temporary)),capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,1)
                self.assertIn('ASSET_CHECKOUT_FAIL: pointer godot/assets/source.bin',result.stderr)
                self.assertFalse((root/'build').exists())
                self.assertFalse((root/'export').exists())
                self.assertEqual(list(temporary.iterdir()),[])

if __name__=='__main__':unittest.main()
