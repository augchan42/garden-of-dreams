"""Collect only the dedicated Garden profiling app's files and process log."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ADB = Path.home() / 'Library/Android/sdk/platform-tools/adb'
PACKAGE = 'org.godotengine.gardendreams.profile'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()

    def adb(*command):
        return subprocess.check_output([str(ADB), '-s', args.device, *command])

    def own_file(name):
        return adb('exec-out', 'run-as', PACKAGE, 'cat', 'files/' + name)

    build_path = ROOT / 'export/android-profile-build.json'
    build = json.loads(build_path.read_text())
    assert build['status'] == 'built'
    assert all(p['status'] == 'passed' and not p.get('engine_diagnostics') for p in build['phases'])
    assert digest(Path(build['apk']).read_bytes()) == build['apk_sha256']
    raw = own_file('garden-phone-profile.json')
    report = json.loads(raw)
    assert report['status'] == 'ready_for_taps', report['status']
    assert report['source_glb_sha256'] == build['source_glb_sha256']
    fixture_record = json.loads((Path(build['fixture']) / 'phone-profile-build.json').read_text())
    assert report['build'] == fixture_record
    assert fixture_record['profile_script_sha256'] == digest((ROOT / 'godot/tests/profile_android.gd').read_bytes())
    for name, expected in fixture_record.get('runtime_script_sha256', {}).items():
        assert digest((ROOT / 'godot/runtime' / name).read_bytes()) == expected, 'Runtime changed after APK build: ' + name
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
