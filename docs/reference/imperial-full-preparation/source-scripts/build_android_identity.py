"""Compile the Android identity bridge using the installed Godot template ABI.

Does not import Godot scenes, install an app, request credentials or contact the
Garden services. Gradle may download pinned public build dependencies.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--template', type=Path, default=Path.home() / 'Library/Application Support/Godot/export_templates/4.7.2.stable/android_source.zip')
parser.add_argument('--java-home', type=Path, default=Path('/Applications/Android Studio.app/Contents/jbr/Contents/Home'))
parser.add_argument('--sdk', type=Path, default=Path.home() / 'Library/Android/sdk')
parser.add_argument('--device-tests', action='store_true', help='Build the dedicated storage test APK; does not install or run it')
parser.add_argument('--report', type=Path, default=ROOT / 'export/android-identity-build.json')
args = parser.parse_args()
fixture = Path(tempfile.mkdtemp(prefix='garden-identity-build-'))
shutil.copytree(ROOT / 'native/android', fixture, dirs_exist_ok=True)
(fixture / 'sdk').mkdir()
with zipfile.ZipFile(args.template) as template:
    for name in ['gradlew', 'gradle/wrapper/gradle-wrapper.jar', 'gradle/wrapper/gradle-wrapper.properties']:
        path = fixture / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(template.read(name))
    with zipfile.ZipFile(io.BytesIO(template.read('libs/debug/godot-lib.template_debug.aar'))) as aar:
        (fixture / 'sdk/godot-classes.jar').write_bytes(aar.read('classes.jar'))
(fixture / 'gradlew').chmod(0o755)
environment = os.environ.copy()
environment['JAVA_HOME'] = str(args.java_home)
environment['ANDROID_HOME'] = str(args.sdk)
command = [str(fixture / 'gradlew'), '--no-daemon', '--console=plain', ':identity:assembleDebug', ':identity:assembleRelease']
if args.device_tests: command.append(':identity:assembleDebugAndroidTest')
report = {'status': 'running', 'fixture': str(fixture), 'command': command,
          'template_sha256': hashlib.sha256(args.template.read_bytes()).hexdigest(),
          'godot_classes_sha256': hashlib.sha256((fixture / 'sdk/godot-classes.jar').read_bytes()).hexdigest(),
          'source_files_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sorted((ROOT / 'native/android').rglob('*')) if p.is_file()},
          'scope': 'Actual Android library compile against installed Godot ABI. No plugin registration/device/sign-in/keystore/server/history acceptance.'}
args.report.parent.mkdir(parents=True, exist_ok=True)
def save(): args.report.write_text(json.dumps(report, indent=2) + '\n')
save()
with (fixture / 'build.log').open('w') as log:
    result = subprocess.run(command, cwd=fixture, env=environment, stdout=log, stderr=subprocess.STDOUT)
report['exit_code'] = result.returncode
report['status'] = 'compiled' if result.returncode == 0 else 'failed'
if result.returncode == 0:
    report['artifacts'] = {}
    for build in ['debug', 'release']:
        source = fixture / f'identity/build/outputs/aar/identity-{build}.aar'
        destination = ROOT / f'godot/addons/garden_identity/bin/{build}/garden-identity.aar'
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        report['artifacts'][str(destination.relative_to(ROOT))] = hashlib.sha256(source.read_bytes()).hexdigest()
    if args.device_tests:
        apk = fixture / 'identity/build/outputs/apk/androidTest/debug/identity-debug-androidTest.apk'
        report['device_test_apk'] = {'path': str(apk), 'sha256': hashlib.sha256(apk.read_bytes()).hexdigest(), 'package': 'ai.eightbitoracle.garden.identity.tests'}
save()
print(json.dumps(report, indent=2))
if result.returncode: print((fixture / 'build.log').read_text()[-5000:])
raise SystemExit(result.returncode)
