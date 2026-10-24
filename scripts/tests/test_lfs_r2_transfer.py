"""Transfer integrity tests use real rclone/local storage, not a fake S3 protocol."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'lfs_r2_transfer.py'
if MODULE.exists():
    spec = importlib.util.spec_from_file_location('transfer', MODULE)
    transfer = importlib.util.module_from_spec(spec);spec.loader.exec_module(transfer)
else:transfer = None


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(transfer, 'Production transfer adapter is missing')
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root/'rclone.conf';self.config.write_text('[fixture]\ntype = local\n')
        self.env = dict(os.environ, RCLONE_CONFIG=str(self.config),
                        R2_LFS_REMOTE='fixture:'+str(self.root/'remote/project'),
                        R2_LFS_RCLONE=shutil.which('rclone') or '/opt/homebrew/bin/rclone')
        self.body = b'asset payload\x00\xff'
        self.oid = hashlib.sha256(self.body).hexdigest()
        self.source = self.root/'source.bin';self.source.write_bytes(self.body)
        self.object = self.root/'remote/project/objects/sha256'/self.oid[:2]/self.oid

    def protocol(self, operation, body=None, env=None, **overrides):
        request = {'event':operation,'oid':self.oid,'size':len(self.body),'path':str(self.source)}
        request.update(overrides)
        messages = [{'event':'init','operation':operation,'concurrent':False},request,{'event':'terminate'}]
        p = subprocess.run([sys.executable,str(MODULE)],input=''.join(json.dumps(x)+'\n' for x in messages),
                           env=env or self.env,text=True,capture_output=True,timeout=30)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(p.stderr,'')
        lines=[json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual(lines[0],{})
        return lines[-1]

    def test_upload_download_and_idempotence(self):
        self.assertNotIn('error',self.protocol('upload'))
        self.assertEqual(self.object.read_bytes(),self.body)
        self.assertNotIn('error',self.protocol('upload'))
        result=self.protocol('download');self.assertNotIn('error',result)
        downloaded=Path(result['path']);self.addCleanup(downloaded.unlink,missing_ok=True)
        self.assertEqual(downloaded.read_bytes(),self.body)

    def test_zero_byte_object(self):
        self.body=b'';self.oid=hashlib.sha256(b'').hexdigest();self.source.write_bytes(b'')
        self.assertNotIn('error',self.protocol('upload'))
        result=self.protocol('download');self.assertNotIn('error',result)
        downloaded=Path(result['path']);self.addCleanup(downloaded.unlink,missing_ok=True)
        self.assertEqual(downloaded.read_bytes(),b'')

    def test_corrupt_upload_source_rejected(self):
        self.source.write_bytes(b'wrong')
        self.assertIn('error',self.protocol('upload'))
        self.assertFalse(self.object.exists())

    def test_corrupt_remote_not_overwritten(self):
        self.object.parent.mkdir(parents=True);self.object.write_bytes(b'wrong')
        self.assertIn('error',self.protocol('upload'))
        self.assertEqual(self.object.read_bytes(),b'wrong')
        self.assertIn('error',self.protocol('download'))

    def test_missing_download_never_returns_usable_path(self):
        result=self.protocol('download')
        self.assertIn('error',result);self.assertNotIn('path',result)

    def test_malformed_oid_and_size_rejected(self):
        for data in ({'oid':'../escape'},{'size':True},{'size':-1}):
            self.assertIn('error',self.protocol('upload',**data))
        self.assertFalse(self.object.exists())

    def test_unavailable_transport_blocks_success(self):
        env=dict(self.env,R2_LFS_RCLONE=str(self.root/'missing-executable'))
        result=self.protocol('upload',env=env)
        self.assertIn('error',result);self.assertNotIn('path',result)
        self.assertNotIn(str(self.root),json.dumps(result))

    def test_private_reader_json_is_loaded_as_data(self):
        from unittest.mock import patch
        values={'R2_ASSETS_BUCKET':'reader-bucket','R2_LFS_PREFIX':'private/random-folder',
                'R2_ASSETS_SECRET_ACCESS_KEY':'literal-$(no-shell-execution)'}
        path=self.root/'reader.json';path.write_text(json.dumps(values))
        with patch.dict(os.environ,{'R2_LFS_PREFIX':'process/override'}):
            loaded=transfer.read_environment(path)
        self.assertEqual(loaded['R2_ASSETS_BUCKET'],values['R2_ASSETS_BUCKET'])
        self.assertEqual(loaded['R2_ASSETS_SECRET_ACCESS_KEY'],values['R2_ASSETS_SECRET_ACCESS_KEY'])
        self.assertEqual(loaded['R2_LFS_PREFIX'],'process/override')

    def test_invalid_private_reader_json_is_rejected(self):
        path=self.root/'reader.json'
        for body in ('{invalid-json','[]','{"R2_LFS_PREFIX":7}','{"PATH":"untrusted"}'):
            path.write_text(body)
            with self.assertRaises(transfer.TransferError):transfer.read_environment(path)

    def test_production_requires_explicit_prefix(self):
        values={'R2_MEDIA_ACCOUNT_ID':'account','R2_MEDIA_BUCKET':'bucket',
                'R2_MEDIA_ACCESS_KEY_ID':'key','R2_MEDIA_SECRET_ACCESS_KEY':'secret',
                'R2_LFS_RCLONE':self.env['R2_LFS_RCLONE']}
        for prefix in (None,'','/','../other','project/../other'):
            supplied=dict(values)
            if prefix is not None:supplied['R2_LFS_PREFIX']=prefix
            with self.assertRaises(transfer.TransferError):transfer.Store(supplied)
        supplied=dict(values,R2_LFS_PREFIX='project/test-random-namespace')
        self.assertEqual(transfer.Store(supplied).remote,'gardenassets:bucket/project/test-random-namespace')

    def test_unsafe_prefix_rejected(self):
        env=dict(self.env,R2_LFS_REMOTE='fixture:'+str(self.root/'remote/../unsafe'))
        self.assertIn('error',self.protocol('upload',env=env))

    def test_duplicate_concurrent_uploads(self):
        from concurrent.futures import ThreadPoolExecutor
        def upload(_):return transfer.Store(self.env).upload(self.source,self.oid,len(self.body))
        with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(upload,range(2)))
        self.assertEqual(self.object.read_bytes(),self.body)

    def test_directory_at_object_key_is_missing(self):
        self.object.mkdir(parents=True)
        result=self.protocol('download')
        self.assertIn('error',result);self.assertNotIn('path',result)

    def test_malformed_protocol_json_is_rejected(self):
        p=subprocess.run([sys.executable,str(MODULE)],input='{invalid-json\n',env=self.env,text=True,capture_output=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('error',json.loads(p.stdout));self.assertEqual(p.stderr,'')

    def test_invalid_initialization(self):
        p=subprocess.run([sys.executable,str(MODULE)],input='{"event":"init","operation":"delete"}\n',
                         env=self.env,text=True,capture_output=True,timeout=10)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('error',json.loads(p.stdout.strip()))



BOOTSTRAP = MODULE.with_name('bootstrap_lfs_r2.py')
if BOOTSTRAP.exists():
    spec = importlib.util.spec_from_file_location('bootstrap', BOOTSTRAP)
    bootstrap = importlib.util.module_from_spec(spec);spec.loader.exec_module(bootstrap)
else:bootstrap = None


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(bootstrap, 'Safe adapter bootstrap is missing')
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.repo=self.root/'repo';self.repo.mkdir()
        subprocess.run(['git','init',str(self.repo)],check=True,capture_output=True)
        self.config=self.repo/'.git/config'
        self.install_root=self.root/'installed'

    def test_install_outside_checkout_and_restore(self):
        before=self.config.read_bytes()
        result=bootstrap.install(self.repo,install_root=self.install_root)
        adapter=Path(result['adapter'])
        self.assertTrue(adapter.is_file());self.assertNotIn(self.repo,adapter.parents)
        p=subprocess.run([sys.executable,str(adapter)],input='{"event":"init","operation":"download"}\n{"event":"terminate"}\n',text=True,capture_output=True)
        self.assertEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout.strip()),{})
        bootstrap.restore(result['snapshot'])
        self.assertEqual(self.config.read_bytes(),before)

    def test_existing_custom_hook_untouched(self):
        hook=self.repo/'.git/hooks/pre-push';body=b'#!/bin/sh\nexit 17\n';hook.write_bytes(body);hook.chmod(0o755)
        before=self.config.read_bytes()
        with self.assertRaises(ValueError):bootstrap.install(self.repo,install_root=self.install_root)
        self.assertEqual(hook.read_bytes(),body);self.assertEqual(self.config.read_bytes(),before)

    def test_existing_custom_hookspath_untouched(self):
        custom=self.root/'custom-hooks';custom.mkdir()
        subprocess.run(['git','config','--local','core.hooksPath',str(custom)],cwd=self.repo,check=True)
        before=self.config.read_bytes()
        with self.assertRaises(ValueError):bootstrap.install(self.repo,install_root=self.install_root)
        self.assertEqual(self.config.read_bytes(),before)

    def test_restore_refuses_later_user_configuration_edits(self):
        result=bootstrap.install(self.repo,install_root=self.install_root)
        subprocess.run(['git','config','--local','user.name','Later user choice'],cwd=self.repo,check=True)
        before=self.config.read_bytes()
        with self.assertRaises(ValueError):bootstrap.restore(result['snapshot'])
        self.assertEqual(self.config.read_bytes(),before)

if __name__=='__main__':unittest.main()
