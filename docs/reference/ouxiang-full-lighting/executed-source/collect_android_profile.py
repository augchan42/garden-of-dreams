"""Collect only the dedicated Garden profiling app's files and process log."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import re
from android_texture_provenance import verify_texture_inputs

ROOT = Path(__file__).resolve().parents[1]
ADB = Path.home() / 'Library/Android/sdk/platform-tools/adb'
PACKAGE = 'org.godotengine.gardendreams.profile'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_profile_build(build, adb):
    assert build['status'] == 'built'
    assert all(p['status'] == 'passed' and not p.get('engine_diagnostics') for p in build['phases'])
    assert digest(Path(build['apk']).read_bytes()) == build['apk_sha256']
    fixture_record = json.loads((Path(build['fixture']) / 'phone-profile-build.json').read_text())
    assert fixture_record.get('texture_provenance_version') == 1, 'APK lacks finalized texture provenance; rebuild the profiler'
    verify_texture_inputs(ROOT / 'godot', fixture_record['production_texture_inputs'], 'Production')
    verify_texture_inputs(Path(build['fixture']), fixture_record['staged_texture_inputs'], 'Staged')
    assert digest((Path(build['fixture']) / 'phone-profile-build.json').read_bytes()) == build['phone_profile_build_sha256']
    assert fixture_record['profile_script_sha256'] == digest((ROOT / 'godot/tests/profile_android.gd').read_bytes())
    if 'inventory_script_sha256' in fixture_record:
        assert fixture_record['inventory_script_sha256'] == digest((ROOT / 'godot/tests/texture_binding_inventory.gd').read_bytes())
    production_runtime = fixture_record.get('production_runtime_script_sha256',
                                            fixture_record.get('runtime_script_sha256', {}))
    for name, expected in production_runtime.items():
        assert digest((ROOT / 'godot/runtime' / name).read_bytes()) == expected, 'Runtime changed after APK build: ' + name
    for name, expected in fixture_record.get('runtime_script_sha256', {}).items():
        assert digest((Path(build['fixture']) / 'runtime' / name).read_bytes()) == expected, 'Staged runtime changed after APK build: ' + name
    for name, expected in fixture_record.get('renderer_files_sha256', {}).items():
        assert digest((ROOT / 'godot' / name).read_bytes()) == expected, 'Renderer changed after APK build: ' + name
        assert digest((Path(build['fixture']) / name).read_bytes()) == expected, 'Staged renderer changed after APK build: ' + name
    package_path = adb('shell', 'pm', 'path', PACKAGE).decode().strip()
    match = re.fullmatch(r'package:(/data/app/[A-Za-z0-9_./+=~\-]+/base\.apk)', package_path)
    assert match, 'Expected one installed dedicated profiling APK'
    installed_sha = adb('shell', 'sha256sum', match.group(1)).decode().split()[0]
    assert installed_sha == build['apk_sha256'], 'Installed profiling APK differs from the build report'
    return fixture_record, installed_sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--build-report', type=Path, default=ROOT / 'export/android-profile-build.json')
    args = parser.parse_args()

    def adb(*command):
        return subprocess.check_output([str(ADB), '-s', args.device, *command])

    def own_file(name):
        return adb('exec-out', 'run-as', PACKAGE, 'cat', 'files/' + name)

    build_path = args.build_report
    build = json.loads(build_path.read_text())
    fixture_record, installed_sha = verify_profile_build(build, adb)
    raw = own_file('garden-phone-profile.json')
    report = json.loads(raw)
    assert report['status'] == 'ready_for_taps', report['status']
    assert report['source_glb_sha256'] == build['source_glb_sha256']
    assert report['build'] == fixture_record
    assert set(report['samples']) == {'cell', 'cell_to_gate', 'gate', 'gate_to_pavilion', 'pavilion'}
    assert all(s['frames'] > 0 and s['visible_draw_calls_max'] > 0 for s in report['samples'].values())
    payloads = {'garden-phone-profile.json': raw, 'build.json': build_path.read_bytes()}
    images = {}
    names = ['cell', 'gate', 'pavilion']
    if report['touch_events']:
        names.append('after-touch')
    for name in names:
        filename = 'garden-phone-' + name + '.png'
        data = own_file(filename)
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        width, height = struct.unpack('>II', data[16:24])
        assert width > 0 and height > 0
        payloads[filename] = data
        images[filename] = {'width': width, 'height': height, 'sha256': digest(data)}
    pid = adb('shell', 'pidof', PACKAGE).decode().strip()
    assert pid.isdigit(), pid
    payloads['app.log'] = adb('logcat', '-d', '--pid=' + pid, '-s', 'godot:V', 'GodotActivity:D')
    assert own_file('garden-phone-profile.json') == raw, 'Profile changed during collection; collect again after taps settle'
    args.destination.mkdir(parents=True, exist_ok=False)
    for name, data in payloads.items():
        (args.destination / name).write_bytes(data)
    evidence = {'status': 'collected', 'scope': report['scope'], 'apk_sha256': build['apk_sha256'],
                'installed_apk_sha256': installed_sha,
                'source_glb_sha256': report['source_glb_sha256'], 'images': images,
                'files': {name: digest(data) for name, data in payloads.items()},
                'device_model': report['device_model'], 'touch_event_count': len(report['touch_events'])}
    (args.destination / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    build['device_tested'] = True
    build['device_profile_evidence'] = str(args.destination)
    build['device_profile_budget_results'] = report['budget_results']
    build_path.write_text(json.dumps(build, indent=2) + '\n')
    print('ANDROID_PROFILE_COLLECTED', args.destination)


if __name__ == '__main__':
    main()
