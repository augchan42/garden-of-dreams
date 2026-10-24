"""Preflight detects unusable assets without overwriting legitimate local work."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE=Path(__file__).resolve().parents[1]/'check_asset_checkout.py'
if MODULE.exists():
    spec=importlib.util.spec_from_file_location('checkout',MODULE)
    checkout=importlib.util.module_from_spec(spec);spec.loader.exec_module(checkout)
else:checkout=None


class CheckoutTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(checkout,'Asset preflight implementation is missing')
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.repo=Path(self.temp.name)
        self.git('init','-b','main');self.git('config','user.name','Checkout test');self.git('config','user.email','test@localhost.invalid')
        (self.repo/'.gitattributes').write_text('*.bin filter=lfs diff=lfs merge=lfs -text\n')
        self.git('add','.gitattributes')
        self.body=b'local source asset'
        self.oid=hashlib.sha256(self.body).hexdigest()
        self.asset=self.repo/'blender/source.bin';self.asset.parent.mkdir()
        self.pointer=f'version https://git-lfs.github.com/spec/v1\noid sha256:{self.oid}\nsize {len(self.body)}\n'
        self.asset.write_text(self.pointer);self.git('add','blender/source.bin');self.git('commit','-m','asset')

    def git(self,*args):
        return subprocess.check_output(['git',*args],cwd=self.repo,stderr=subprocess.DEVNULL)

    def test_missing_asset(self):
        self.asset.unlink();report=checkout.check(self.repo)
        self.assertEqual(report['status'],'failed');self.assertEqual(report['errors'][0]['path'],'blender/source.bin')
        self.assertEqual(report['errors'][0]['reason'],'missing')

    def test_pointer_stub(self):
        self.assertEqual(checkout.check(self.repo)['errors'][0]['reason'],'pointer')
        self.assertEqual(self.asset.read_text(),self.pointer)

    def test_dirty_asset_allowed(self):
        self.asset.write_bytes(b'edited locally')
        self.assertEqual(checkout.check(self.repo)['status'],'passed')
        self.assertEqual(self.asset.read_bytes(),b'edited locally')

    def test_strict_hash_mismatch(self):
        self.asset.write_bytes(b'edited locally')
        report=checkout.check(self.repo,strict=True)
        self.assertEqual(report['status'],'failed');self.assertEqual(report['errors'][0]['reason'],'hash_mismatch')

    def test_clean_strict_checkout(self):
        self.asset.write_bytes(self.body)
        self.assertEqual(checkout.check(self.repo,strict=True)['status'],'passed')

    def test_selective_checkout(self):
        docs=self.repo/'docs/reference.bin';docs.parent.mkdir();docs.write_text(self.pointer)
        self.git('add','docs/reference.bin');self.git('commit','-m','reference')
        self.asset.write_bytes(self.body)
        self.assertEqual(checkout.check(self.repo,profile='active')['status'],'passed')
        self.assertEqual(checkout.check(self.repo,profile='all')['status'],'failed')


if __name__=='__main__':unittest.main()
