"""Offline APK/producer proof. Stop before the first device call."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('--project', type=Path, required=True)
parser.add_argument('--build', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.project / 'scripts'))
import collect_android_profile as collector
from android_profile_modes import packaged_payloads
collector.ROOT = args.project
build = json.loads(args.build.read_text())
staged = Path(build['fixture'])
manifest = json.loads((staged / 'phone-profile-build.json').read_text())
class BeforeDeviceCall(Exception): pass
def no_device(*arguments):
    assert arguments == ('shell', 'pm', 'path', collector.PACKAGE)
    raise BeforeDeviceCall()
try:
    collector.verify_profile_build(build, no_device)
except BeforeDeviceCall:
    pass
else:
    raise AssertionError('Offline preflight did not reach the device boundary')
sha = lambda data: hashlib.sha256(data).hexdigest()
with zipfile.ZipFile(build['apk']) as package:
    proof = packaged_payloads(package, staged, manifest)
    textures = {}
    for name in package.namelist():
        if not name.endswith('.import'): continue
        exported = package.read(name).decode().rstrip('\0').strip()
        if 'importer="texture"' not in exported: continue
        source = (staged / name.removeprefix('assets/')).read_text().split('\n[deps]\n')[0].strip()
        # Android export drops the desktop S3TC variant from each remap.
        source = re.sub(r'^path\.s3tc=.*\n', '', source, flags=re.MULTILINE)
        assert exported == source, 'Texture remap differs: ' + name
        paths = re.findall(r'^path(?:\.[^=\n]+)?="res://([^"\n]+)"$', exported, re.MULTILINE)
        assert paths, 'Missing texture payload: ' + name
        for path in paths:
            data = package.read('assets/' + path)
            assert sha(data) == sha((staged / path).read_bytes()), 'Texture cache differs: ' + path
            textures['assets/' + path] = sha(data)
    previous = json.loads((args.project / 'docs/reference/lossless-backdrop-wash/android/android-payload-verification.json').read_text())
    assert all(textures.get(name) == digest for name, digest in previous['payload_sha256'].items()), 'Prior normal bound texture payload changed'
proof.update({'status':'offline_preflight_and_packaged_payloads_passed', 'scope':'Current/staged provenance verified up to the first device-call boundary without calling ADB. Actual compiled dependency remaps, scene cache and all exported texture caches inspected. Prior 177 normal bound texture payloads remain byte-identical. No installation or physical-device acceptance.', 'apk_sha256':build['apk_sha256'], 'apk_bytes':build['apk_bytes'], 'profile_mode':manifest['profile_mode'], 'producer_sha256':manifest['profile_script_sha256'], 'texture_payload_sha256':textures, 'texture_payload_count':len(textures), 'prior_normal_bound_payload_count':len(previous['payload_sha256'])})
args.output.write_text(json.dumps(proof,indent=2)+'\n')
print('OFFLINE_APK_PREFLIGHT_PASS', len(textures), len(proof['compiled_profile_script_sha256']), build['apk_sha256'])
