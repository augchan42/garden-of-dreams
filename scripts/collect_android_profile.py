"""Collect only the dedicated Garden profiling app's files and process log."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import re
import math
import time
from android_profile_modes import verify as verify_profile_scripts
from android_texture_provenance import verify_texture_inputs
from configure_runtime_texture_caps import verify_manifest_caps, SIZES

ROOT = Path(__file__).resolve().parents[1]
ADB = Path.home() / 'Library/Android/sdk/platform-tools/adb'
PACKAGE = 'org.godotengine.gardendreams.profile'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_device_caps(proof, mode="demo"):
    assert mode in ["demo", "normal"], "Unknown Android cap mode"
    assert isinstance(proof, dict) and proof.get('status') == 'passed' and proof.get('errors') == [], 'Actual Android cap proof missing or failed'
    assert proof.get('modes') == [mode], 'Actual Android cap ' + mode + ' binding proof missing'
    textures = proof.get('textures', {})
    assert set(textures) == set(SIZES), 'Actual Android cap texture set differs'
    for name, (width, height, footprint, formats, count) in SIZES.items():
        record = textures[name]
        assert record.get('loaded_size') == [width, height] and record.get('mipmaps') is True, 'Actual Android cap size or mips differ: ' + name
        assert record.get('stored_format') in formats and record.get('stored_mip_bytes') == footprint, 'Actual Android cap format or footprint differs: ' + name
        assert record.get('bindings') == {mode: count}, 'Actual Android cap active material bindings differ: ' + name


def verify_profile_build(build, adb):
    assert build['status'] == 'built'
    assert all(p['status'] == 'passed' and not p.get('engine_diagnostics') for p in build['phases'])
    assert digest(Path(build['apk']).read_bytes()) == build['apk_sha256']
    fixture_record = json.loads((Path(build['fixture']) / 'phone-profile-build.json').read_text())
    assert fixture_record.get('texture_provenance_version') == 1, 'APK lacks finalized texture provenance; rebuild the profiler'
    verify_texture_inputs(ROOT / 'godot', fixture_record['production_texture_inputs'], 'Production')
    verify_texture_inputs(Path(build['fixture']), fixture_record['staged_texture_inputs'], 'Staged')
    assert digest((Path(build['fixture']) / 'phone-profile-build.json').read_bytes()) == build['phone_profile_build_sha256']
    mode = verify_profile_scripts(ROOT / 'godot', Path(build['fixture']), fixture_record)
    assert build.get('profile_mode', 'demo') == mode, 'Profile mode differs from staged manifest'
    if 'inventory_script_sha256' in fixture_record:
        assert fixture_record['inventory_script_sha256'] == digest((ROOT / 'godot/tests/texture_binding_inventory.gd').read_bytes())
    assert fixture_record.get('moon_runtime_import'), 'APK lacks loaded moon provenance; rebuild the profiler'
    moon = fixture_record['moon_runtime_import']
    assert moon['status'] == 'passed' and not moon['errors']
    assert moon['loaded_size'] == [512, 512] and moon['image_bytes'] <= 1398100
    assert moon['source_glb_sha256'] == build['source_glb_sha256']
    assert moon['source_png_sha256'] == digest((ROOT / 'godot/assets/garden-of-dreams_moon-paint.png').read_bytes())
    assert fixture_record['moon_check_script_sha256'] == digest((ROOT / 'godot/tests/test_moon_runtime_import.gd').read_bytes())
    assert fixture_record['moon_paint_atlas_sha256'] == digest((ROOT / 'godot/tests/moon-paint-atlas.json').read_bytes())
    assert fixture_record.get('report_store_script_sha256'), 'APK lacks report writer provenance; rebuild the profiler'
    writer = 'tests/profile_report_store.gd'
    assert fixture_record['report_store_script_sha256'] == digest((ROOT / 'godot' / writer).read_bytes()), 'Production report writer changed after APK build'
    assert fixture_record['report_store_script_sha256'] == digest((Path(build['fixture']) / writer).read_bytes()), 'Staged report writer changed after APK build'
    verify_manifest_caps(ROOT / 'godot', Path(build['fixture']), fixture_record)
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


def verify_full_report(report):
    assert report.get('profile_mode') == 'full' and report.get('status') == 'complete', 'Full profile is incomplete'
    assert report.get('error') == '', 'Full profile reports a failure'
    assert report.get('physics_ticks_per_second') == 60 and report.get('time_scale') == 1.0 and report.get('fps_cap') == 60, 'Full profile simulation changed'
    assert math.isfinite(report['timed_seconds']) and report['timed_seconds'] >= 600 and report['minimum_timed_seconds'] == 600, 'Full profile is too short'
    tours = report['completed_tours']
    assert isinstance(tours, int) and not isinstance(tours, bool) and tours >= 2, 'Full profile requires at least two complete tours'
    source = (ROOT / 'godot/tests/test_full_garden_traversal.gd').read_text()
    # This canonical route constant is JSON-compatible; no eval of GDScript.
    tour = json.loads(source.split('const TOUR = ', 1)[1].split('\nvar route', 1)[0])
    assert len(tour) == 26, 'Canonical full route differs'
    assert len(report['legs']) == tours * len(tour), 'Incomplete full profile legs'
    expected_samples = {'start-terminal_room'}
    expected_captures = {'start-terminal_room': 'terminal_room'}
    expected_arrivals = []
    for number in range(tours):
        origin = 'terminal_room'
        for index, (command, target) in enumerate(tour):
            leg = report['legs'][number * len(tour) + index]
            assert (leg['tour'], leg['from'], leg['command'], leg['to']) == (number, origin, command, target), 'Full profile route order differs'
            assert leg['physics_frames'] > 0 and leg['walking_distance_m'] > 0 and leg['min_y'] >= -.95 and leg['longest_air_frames'] <= 24, 'Full profile movement failed'
            assert leg['grounded_ray_samples'] > 0 and leg['supported_ray_samples'] == leg['grounded_ray_samples'], 'Full profile floor support failed'
            assert re.fullmatch(r'[0-9a-f]{64}', leg['trace_sha256']), 'Missing full profile movement trace'
            height = 4.0 if target == 'tubi_tang' else -.65 if target == 'aojing_guan' else 0.0
            assert len(leg['end_position']) == 3 and abs(leg['end_position'][1] - height) <= .2, 'Full profile arrival height differs'
            expected_samples.add(f'{number:02d}-{index:02d}-{origin}-to-{target}')
            label = f'{number:02d}-{index:02d}-{target}'
            expected_samples.add(label)
            expected_captures[label] = target
            expected_arrivals.append(target)
            origin = target
    assert report['arrival_signals'] == expected_arrivals, 'Full profile arrival signals differ'
    assert set(report['visited_rooms']) == set(expected_arrivals) and len(report['visited_rooms']) == 14, 'Incomplete full profile rooms'
    assert set(report['samples']) == expected_samples and set(report['budget_results']) == expected_samples, 'Incomplete full profile samples'
    assert set(report['captures']) == set(expected_captures), 'Incomplete full profile captures'
    for label, sample in report['samples'].items():
        assert sample['frames'] > 0 and sample['visible_draw_calls_max'] > 0 and sample['visible_primitives_max'] > 0 and sample['texture_memory_bytes'] > 0, 'Empty full profile sample'
        for field in ['frame_interval_median_ms', 'frame_interval_p95_ms']:
            assert math.isfinite(sample[field]) and sample[field] > 0, 'Invalid full profile frame timing'
        budgets = {'texture': sample['texture_memory_bytes'] <= 64*1024*1024,
                   'draw_calls': sample['visible_draw_calls_max'] <= 150,
                   'primitives': sample['visible_primitives_max'] <= 300000,
                   'practicals': sample['active_practicals_max'] <= 4,
                   'p95_60fps': sample['frame_interval_p95_ms'] <= 1000/60}
        assert report['budget_results'][label] == budgets, 'False full profile budget result'
    for label, room in expected_captures.items():
        capture = report['captures'][label]
        assert capture['file'] == 'garden-full-' + label + '.png', 'Unsafe or mismatched full profile capture filename'
        assert capture['room'] == room and capture['camera_settled'] is True, 'Full profile camera or room differs'
        assert re.fullmatch(r'[0-9a-f]{64}', capture['sha256']), 'Full profile capture hash missing'
        assert len(capture['image_size']) == 2 and all(isinstance(n, int) and n > 0 for n in capture['image_size']), 'Invalid full profile capture dimensions'


def parse_profile_publication(raw):
    # Only this explicit remote file-absence marker permits a startup retry.
    # Empty, partial or diagnostic text is invalid JSON and must still fail.
    if raw == b'GARDEN_PROFILE_NOT_PUBLISHED\n': return None
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--build-report', type=Path, default=ROOT / 'export/android-profile-build.json')
    parser.add_argument('--wait-timeout', type=int, default=0,
                        help='Full mode only: wait for complete atomic reports, with a 20-second startup deadline.')
    args = parser.parse_args()
    assert 0 <= args.wait_timeout <= 3600, 'Invalid profile wait timeout'

    def adb(*command):
        return subprocess.check_output([str(ADB), '-s', args.device, *command])

    def own_file(name):
        return adb('exec-out', 'run-as', PACKAGE, 'cat', 'files/' + name)

    build_path = args.build_report
    build = json.loads(build_path.read_text())
    fixture_record, installed_sha = verify_profile_build(build, adb)
    mode = fixture_record.get('profile_mode', 'demo')
    assert not args.wait_timeout or mode == 'full', 'Waiting is supported only for full mode'
    def profile_publication():
        command = ('if test -f files/garden-phone-profile.json; then cat files/garden-phone-profile.json; '
                   'else printf "GARDEN_PROFILE_NOT_PUBLISHED\\n"; fi')
        return adb('exec-out', 'run-as', PACKAGE, 'sh', '-c', command)

    started = time.monotonic()
    reads = 0
    while True:
        raw = profile_publication()
        report = parse_profile_publication(raw)
        if report is None:
            assert args.wait_timeout and reads == 0 and time.monotonic() - started < 20, 'Full profile startup did not publish within20seconds'
            time.sleep(2)
            continue
        reads += 1
        assert report['source_glb_sha256'] == build['source_glb_sha256']
        assert report['build'] == fixture_record, 'Actual phone report differs from pinned build'
        assert report['status'] != 'failed', report.get('error', 'Phone profile failed')
        if mode != 'full' or report['status'] == 'complete' or not args.wait_timeout: break
        assert time.monotonic() - started < args.wait_timeout, 'Full phone profile timed out'
        # Atomic host publication permits safe progress inspection while this tool runs.
        progress = args.destination.with_name(args.destination.name + '-progress.json')
        progress.parent.mkdir(parents=True, exist_ok=True)
        temporary = progress.with_suffix('.json.tmp')
        temporary.write_bytes(raw)
        temporary.replace(progress)
        time.sleep(2)
    verify_device_caps(report.get('runtime_texture_caps'), mode='normal' if mode == 'full' else 'demo')
    if mode == 'full':
        verify_full_report(report)
        captures = list(report['captures'].values())
    else:
        assert report['status'] == 'ready_for_taps', report['status']
        assert set(report['samples']) == {'cell', 'cell_to_gate', 'gate', 'gate_to_pavilion', 'pavilion'}
        assert all(s['frames'] > 0 and s['visible_draw_calls_max'] > 0 for s in report['samples'].values())
        names = ['cell', 'gate', 'pavilion'] + (['after-touch'] if report['touch_events'] else [])
        captures = [{'file': 'garden-phone-' + name + '.png'} for name in names]
    payloads = {'garden-phone-profile.json': raw, 'build.json': build_path.read_bytes()}
    images = {}
    for capture in captures:
        filename = capture['file']
        assert re.fullmatch(r'garden-(?:full|phone)-[A-Za-z0-9_-]+\.png', filename), 'Unsafe capture filename'
        data = own_file(filename)
        assert len(data) >= 24 and data[:8] == b'\x89PNG\r\n\x1a\n'
        width, height = struct.unpack('>II', data[16:24])
        assert width > 0 and height > 0
        if mode == 'full':
            assert capture['image_size'] == [width, height] and digest(data) == capture['sha256'], 'Actual full phone capture differs'
        payloads[filename] = data
        images[filename] = {'width': width, 'height': height, 'sha256': digest(data)}
    pid = adb('shell', 'pidof', PACKAGE).decode().strip()
    assert pid.isdigit(), pid
    payloads['app.log'] = adb('logcat', '-d', '--pid=' + pid, '-s', 'godot:V', 'GodotActivity:D')
    assert own_file('garden-phone-profile.json') == raw, 'Profile changed during collection; collect again after taps settle'
    verify_profile_build(build, adb)  # Recheck source/cache/installed identity after the sustained wait.
    args.destination.mkdir(parents=True, exist_ok=False)
    for name, data in payloads.items():
        (args.destination / name).write_bytes(data)
    evidence = {'status': 'collected', 'profile_mode': mode, 'scope': report['scope'], 'apk_sha256': build['apk_sha256'],
                'installed_apk_sha256': installed_sha, 'complete_json_reads': reads, 'incomplete_json_reads': 0,
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
