"""Scoped credentials must omit the parent secret and carry enforceable claims."""
import base64
import hashlib
import hmac
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
try:
 from mint_r2_reader import mint
except ImportError:mint=None


class ReaderTests(unittest.TestCase):
 def setUp(self):
  self.assertIsNotNone(mint,'Scoped-reader minting helper is missing')
  self.values={'R2_MEDIA_ACCOUNT_ID':'account','R2_MEDIA_BUCKET':'bucket',
               'R2_MEDIA_ACCESS_KEY_ID':'parent-id','R2_MEDIA_SECRET_ACCESS_KEY':'parent-secret'}

 def test_scoped_signed_reader_and_derived_secret(self):
  result=mint(self.values,ttl=900,now=1000)
  jwt=base64.b64decode(result['R2_ASSETS_SESSION_TOKEN']).decode().removeprefix('jwt/')
  header,payload,signature=jwt.split('.')
  claims=json.loads(base64.urlsafe_b64decode(payload+'='*(-len(payload)%4)))
  self.assertEqual(claims['scope'],'object-read-only')
  self.assertEqual(claims['paths'],{'prefixPaths':['garden-of-dreams-lfs/'],'objectPaths':[]})
  self.assertEqual((claims['iat'],claims['exp']),(1000,1900))
  self.assertEqual(result['R2_ASSETS_SECRET_ACCESS_KEY'],hashlib.sha256(jwt.encode()).hexdigest())
  expected=base64.urlsafe_b64encode(hmac.new(b'parent-secret',(header+'.'+payload).encode(),hashlib.sha256).digest()).rstrip(b'=').decode()
  self.assertEqual(signature,expected)
  self.assertNotIn('parent-secret',json.dumps(result))

 def test_cli_creates_private_file_and_refuses_overwrite(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);env=root/'credentials.env';output=root/'reader.json'
   env.write_text(''.join(key+'='+value+'\n' for key,value in self.values.items()))
   command=[sys.executable,str(Path(__file__).resolve().parents[1]/'mint_r2_reader.py'),'--env-file',str(env),'--output',str(output)]
   first=subprocess.run(command,capture_output=True,text=True)
   self.assertEqual(first.returncode,0,first.stderr)
   self.assertEqual(output.stat().st_mode&0o777,0o600)
   before=output.read_bytes()
   self.assertNotIn('parent-secret',first.stdout+first.stderr)
   self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
   self.assertEqual(output.read_bytes(),before)

 def test_explicit_short_lifetime_and_complete_parent_required(self):
  for ttl in (0,True,2592001):
   with self.assertRaises(ValueError):mint(self.values,ttl=ttl,now=1000)
  with self.assertRaises(ValueError):mint({},ttl=900,now=1000)


if __name__=='__main__':unittest.main()
