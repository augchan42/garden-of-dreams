"""Review the complete paving source after the sole fresh-lighting worker exits."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/paving-site-joins'
source = Path('/tmp/garden-paving-joins-20261010-v4')
review = Path('/tmp/garden-paving-review-20261010-v4')
game = review / 'godot'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
prep = json.loads((review / 'fixture-preparation.json').read_text())
expected = prep['candidate_glb_sha256']
baseline = prep['baseline_glb_sha256']
assert sha(repo / 'export/garden-of-dreams.glb') == baseline
assert sha(source / 'export/garden-of-dreams.glb') == expected
assert sha(source / 'blender/authoring.blend') == prep['authoring_sha256']
bake = json.loads((source / 'export/full-lighting-refresh.json').read_text())
preparation = json.loads((source / 'lighting-preparation.json').read_text())
assert bake['status'] == 'source_complete', 'Wait for existing session16116; never start a second source bake'
assert preparation['status'] == 'complete_source_lighting_passed_native_review_pending'
for pid in [bake['orchestrator_pid'], preparation['orchestrator_pid'], *[p['pid'] for p in bake['phases']], *[p['pid'] for p in preparation['phases']]]:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        continue
    raise AssertionError(('Source process still alive; no native review allowed', pid))
assert [p['name'] for p in bake['phases']] == ['ordinary', 'backdrop-wash', 'terminal-spill', 'terminal-spill-pixels', 'native-pixels', 'coverage']
assert all(p['status'] == 'passed' and p['exit_code'] == 0 for p in bake['phases'])
frozen = json.loads((source / 'full-lighting-inputs.json').read_text())['files']
for name, digest in frozen.items():
    assert sha(source / name) == digest, name
assert (review / 'review-pipeline-failed-floor-plane-tolerance.json').exists()
logs = review / 'review-logs'
assert logs.is_dir()
report = json.loads((review / 'review-pipeline-failed-floor-plane-tolerance.json').read_text())
assert report['status'] == 'failed' and report['phases'][-1]['name'] == 'baseline-paving-red'
assert len(report['phases']) == 22 and all(p['status'] == 'passed' and p['exit_code'] == 0 for p in report['phases'][:-1])
for phase in report['phases']:
    assert sha(phase['log']) == phase['log_sha256']
assert json.loads((review / 'review-pipeline.json').read_text()) == report, 'Never replay a started continuation'
report['prior_failure_report'] = 'review-pipeline-failed-floor-plane-tolerance.json'
report['prior_pipeline_pid'] = report['pid']
report['phases'] = report['phases'][:-1]
report.pop('error')
report['status'] = 'running'
report['pid'] = os.getpid()
report['continued_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
report['floor_filter_tolerance_m'] = .0001
report['floor_regression_sha256'] = prep['paving_native_regression_sha256']


def save():
    (review / 'review-pipeline.json').write_text(json.dumps(report, indent=2) + '\n')

def run(name, args, marker, timeout=180):
    assert sha(source / 'export/garden-of-dreams.glb') == expected
    assert sha(source / 'blender/authoring.blend') == prep['authoring_sha256']
    log = logs / (name + '.log')
    phase = {'name': name, 'status': 'running', 'command': args, 'log': str(log)}
    report['phases'].append(phase)
    save()
    print('PAVING_LIT_REVIEW_START', name, flush=True)
    with log.open('w') as out:
        child = subprocess.Popen(args, stdout=out, stderr=subprocess.STDOUT)
        phase['pid'] = child.pid
        save()
        try:
            phase['exit_code'] = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            child.terminate()
            child.wait(timeout=30)
            phase['exit_code'] = 124
    text = log.read_text(errors='replace')
    okay = phase['exit_code'] == 0 and marker in text and not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)', text)
    phase.update(status='passed' if okay else 'failed', log_sha256=sha(log))
    save()
    assert okay, (name, phase['exit_code'], text[-4000:])
    print('PAVING_LIT_REVIEW_PASS', name, flush=True)

def run_expected_rejection(name, args, expected_error):
    log = logs / (name + '.log')
    phase = {'name': name, 'status': 'running', 'command': args, 'log': str(log), 'expected_exit_code': 1, 'expected_error': expected_error}
    report['phases'].append(phase)
    save()
    print('PAVING_LIT_NEGATIVE_START', name, flush=True)
    with log.open('w') as out:
        child = subprocess.Popen(args, stdout=out, stderr=subprocess.STDOUT)
        phase['pid'] = child.pid
        save()
        try:
            phase['exit_code'] = child.wait(timeout=160)
        except subprocess.TimeoutExpired:
            child.terminate()
            child.wait(timeout=30)
            phase['exit_code'] = 124
    text = log.read_text(errors='replace')
    errors = [line for line in text.splitlines() if line.startswith(('ERROR:', 'SCRIPT ERROR:'))]
    okay = phase['exit_code'] == 1 and len(errors) == 1 and errors[0] == 'ERROR: ' + expected_error
    phase.update(status='passed_expected_rejection' if okay else 'failed', log_sha256=sha(log))
    save()
    assert okay, (name, phase['exit_code'], text[-3000:])
    print('PAVING_LIT_NEGATIVE_PASS', name, flush=True)


def verify_captures(path, digest, count):
    data = json.loads((path / 'report.json').read_text())
    assert data.get('source_sha256', data.get('source_glb_sha256')) == digest
    assert not data['errors'] and len(data['rows']) == count
    for row in data['rows']:
        p = Path(row['capture'])
        assert sha(p) == row['sha256']
        assert list(struct.unpack('>II', p.read_bytes()[16:24])) == row['pixels']
    return data

try:
    save()
    shutil.copyfile(__file__, review / 'executed-review-continuation.py')
    captures = review / 'review-captures'
    assert captures.is_dir()
    base_game = review / 'baseline-godot'
    assert sha(base_game / 'assets/garden-of-dreams.glb') == baseline
    # Run the same floor-owner regression against both actual sources. The old
    # floor must reject; retain its original lit/ID/hide images and full report.
    floor_baseline = captures / 'paving-baseline-red-v2'
    log = logs / 'baseline-paving-red-v2.log'
    phase = {'name': 'baseline-paving-red', 'status': 'running', 'log': str(log),
             'command': [godot, '--path', str(base_game), '--windowed', '--resolution', '390x844', '--script', 'res://tests/test_paving_surface_transfer.gd', '--', '--output=' + str(floor_baseline)],
             'expected_exit_code': 1}
    report['phases'].append(phase); save()
    with log.open('w') as out:
        child = subprocess.Popen(phase['command'], stdout=out, stderr=subprocess.STDOUT)
        phase['pid'] = child.pid; save()
        try: phase['exit_code'] = child.wait(timeout=160)
        except subprocess.TimeoutExpired:
            child.terminate(); child.wait(timeout=30); phase['exit_code'] = 124
    text = log.read_text(errors='replace')
    data = json.loads((floor_baseline / 'report.json').read_text())
    duplicate_errors = {'Duplicate connecting floor survives at pixel ' + p for p in ['(210, 440)', '(235, 455)', '(310, 464)']}
    allowed_errors = duplicate_errors | {'Connecting floor still owns shared pixel ' + p for p in ['(210, 440)', '(235, 455)', '(310, 464)']}
    # Coplanar draw ownership can vary with render sorting. All three hidden-site
    # duplicate tops must remain visible in the baseline; any other failure rejects.
    actual_errors = set(data['errors'])
    okay = phase['exit_code'] == 1 and data['status'] == 'rejected' and data['source_glb_sha256'] == baseline and duplicate_errors <= actual_errors <= allowed_errors and len(data['errors']) == len(actual_errors) and len(data['rows']) == 4 and data['fixed_clock'] == 3.0 and data['settle_seconds'] == 1.8 and data['identity_height_tolerance'] == .0001 and 'Parse Error:' not in text and 'SCRIPT ERROR:' not in text
    phase.update(status='passed_expected_rejection' if okay else 'failed', log_sha256=sha(log), native_report_sha256=sha(floor_baseline / 'report.json'))
    save(); assert okay, ('Expected floor duplicate rejection failed', data.get('errors'), text[-2500:])
    for row in data['rows']:
        p = Path(row['capture']); assert sha(p) == row['sha256'] and list(struct.unpack('>II', p.read_bytes()[16:24])) == row['pixels'] == [390,844]
    floor_candidate = captures / 'paving-candidate-green'
    run('candidate-paving-green', native + ['--script', 'res://tests/test_paving_surface_transfer.gd', '--', '--output=' + str(floor_candidate)], 'PAVING_NATIVE_TRANSFER_RESULT 4 originals; 0 failures', 160)
    data = verify_captures(floor_candidate, expected, 4)
    assert data['fixed_clock'] == 3.0 and data['settle_seconds'] == 1.8 and data['identity_height_tolerance'] == .0001
    assert all(row['site_bakes_enabled'] and not row['camera_transition_running'] for row in data['rows'])
    for mode, args, count in [('normal', [], 13), ('touch', ['--touch'], 12), ('density', ['--density'], 10)]:
        output = captures / ('ziling-' + mode)
        run('ziling-' + mode, native + ['--script', 'res://tests/test_ziling_framing.gd', '--', '--output=' + str(output), *args], 'ZILING_FRAMING_RESULT ' + str(count) + ' originals; 0 failures', 160)
        verify_captures(output, expected, count)
    for label, script, marker in [('ouxiang', 'test_oux_portrait_framing.gd', 'OUXIANG_FRAMING_PASS'), ('hengwu', 'test_hengwu_detail_framing.gd', 'HENGWU_DETAIL_FRAMING_RESULT'), ('tubi', 'test_tubi_framing.gd', 'TUBI_FRAMING_RESULT'), ('qiushuang', 'test_qiushuang_framing.gd', 'QIUSHUANG_FRAMING_RESULT'), ('pond', 'test_pond_view.gd', 'POND_VIEW_PASS')]:
        run('adjacent-' + label, native + ['--script', 'res://tests/' + script, '--', '--output=' + str(captures / label)], marker, 160)
    for mode, flags in [('normal', []), ('touch', ['--touch']), ('density', ['--density'])]:
        for label, script, marker, extra in [('yihong', 'test_yihong_framing.gd', 'YIHONG_FRAMING_RESULT', []), ('architecture', 'test_portrait_architecture.gd', 'PORTRAIT_ARCHITECTURE_RESULT', [] if mode=='normal' else ['--room=daguan_lou'])]:
            run(label+'-'+mode, native+['--script','res://tests/'+script,'--','--output='+str(captures/(label+'-'+mode)),*flags,*extra], marker, 160)
    run('entry-route', head+['--script','res://tests/test_entry_route.gd'], 'ENTRY_ROUTE_PASS')
    run('first-reading-demo', head+['--script','res://tests/test_first_reading_demo.gd'], 'FIRST_READING_DEMO_PASS')
    for mode, args in [('normal', []), ('demo', ['--demo'])]:
        run('texture-memory-' + mode, native + ['--script', 'res://tests/audit_runtime_textures.gd', '--', '--output=' + str(review / ('texture-memory-' + mode + '.json')), *args], 'RUNTIME_TEXTURE_INVENTORY_PASS', 160)
    rooms = {'terminal_room', 'rockery_gate', 'qinfang_ting', 'ouxiang_xie', 'ziling_zhou', 'qiushuang_zhai', 'tubi_tang', 'hengwu_yuan', 'daguan_lou', 'yihong_yuan', 'xiaoxiang_guan', 'longcui_an', 'aojing_guan', 'daoxiang_cun'}
    report['arrivals'] = {}
    for mode, args, dimensions in [('desktop', [], [1410, 600]), ('portrait', ['--mobile'], [390, 844])]:
        output = captures / ('arrivals-' + mode)
        run('arrivals-' + mode, native + ['--script', 'res://tests/render_entry_route.gd', '--', '--views-only', '--fixed-clock', '--output-directory=' + str(output), *args], 'ROUTE_RENDER_SAVED', 160)
        path = output / ('route-' + mode + '-report.json')
        data = json.loads(path.read_text())
        assert data['source_glb_sha256'] == expected and data['fixed_clock'] == 3.0
        assert len(data['captures']) == 14 and {row['room_id'] for row in data['captures'].values()} == rooms
        for label, row in data['captures'].items():
            image = output / ('route-' + label + '.png')
            assert sha(image) == row['sha256']
            assert row['image_size'] == list(struct.unpack('>II', image.read_bytes()[16:24])) == dimensions
        assert len(list(output.glob('*.png'))) == 14
        report['arrivals'][mode] = {'report_sha256': sha(path), 'originals': 14, 'dimensions': dimensions}
        save()
    report['walks'] = {}
    for mode, args, dimensions in [('desktop', [], [1410, 600]), ('portrait', ['--portrait'], [540, 960])]:
        output = captures / ('tour-' + mode)
        output.mkdir()
        run('full-tour-' + mode, native + ['--script', 'res://tests/render_full_garden_traversal.gd', '--', '--capture-directory=' + str(output), '--output=' + str(output / 'report.json'), *args], 'FULL_GARDEN_TRAVERSAL_PASS rooms=14 legs=26', 900)
        path = output / 'report.json'
        data = json.loads(path.read_text())
        assert data['status'] == 'passed' and not data['error'] and not data['floor_failures']
        assert data['source_glb_sha256'] == expected and set(data['visited_rooms']) == rooms
        assert len(data['legs']) == len(data['arrival_signals']) == len(data['settled_arrivals']) == 26
        assert data['time_scale'] == 1 and data['physics_ticks_per_second'] == 60 and data['maximum_practicals'] <= 4
        assert len(data['captures']) == len(list(output.glob('*.png'))) >= 52
        for leg in data['legs']:
            assert leg['grounded_ray_samples'] > 0 and leg['supported_ray_samples'] == leg['grounded_ray_samples'] and not leg['centre_ray_misses']
        for row in data['captures']:
            image = output / row['file']
            assert sha(image) == row['sha256']
            assert list(struct.unpack('>II', image.read_bytes()[16:24])) == dimensions
        report['walks'][mode] = {'report_sha256': sha(path), 'originals': len(data['captures']), 'dimensions': dimensions, 'supported_ray_samples': sum(leg['supported_ray_samples'] for leg in data['legs']), 'maximum_practicals': data['maximum_practicals']}
        save()
    assert len(report['phases']) == len({p['name'] for p in report['phases']}) == 45
    assert sum(p['status'] == 'passed' and p['exit_code'] == 0 for p in report['phases']) == 44
    assert sum(p['status'] == 'passed_expected_rejection' and p['exit_code'] == 1 for p in report['phases']) == 1

    for name, digest in frozen.items():
        assert sha(source / name) == digest, name
    assert sha(game / 'runtime/entry_route.gd') == sha(repo / 'godot/runtime/entry_route.gd') == prep['runtime_sha256']
    report.update(status='complete_paving_technical_review_direct_allroom_and_moving_visual_review_pending', finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('PAVING_LIT_TECHNICAL_REVIEW_COMPLETE', flush=True)
except BaseException as error:
    report.update(status='failed', error=str(error))
    save()
    raise
