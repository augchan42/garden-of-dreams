"""Run sequential native review only after the existing source worker exits."""
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
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette'
source = work / 'candidate'
review = work / 'lit-native-review'
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
assert bake['status'] == 'source_complete', 'Wait for existing session48984; never start a second source bake'
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
assert not (review / 'review-pipeline.json').exists(), 'Use an explicit continuation for a failed review; do not replay completed phases'
logs = review / 'review-logs'
logs.mkdir()
report = {'status': 'running', 'pid': os.getpid(), 'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'candidate_glb_sha256': expected, 'baseline_glb_sha256': baseline, 'authoring_sha256': prep['authoring_sha256'], 'frozen_inputs_verified': len(frozen), 'phases': [], 'scope': 'Complete isolated warm gray canvas source review. Source-matched full lighting, actual normal/demo palette transfer including canvas, expected original-source rejection and corrupt-canvas control, all14 desktop/portrait arrivals and both continuous full tours. Matching current baseline/candidate lit originals and unchanged runtime/cameras. Technical completion requires separate direct all-room/moving-view inspection; no final14site art, phone/sustained/release/service or production acceptance.'}

def save():
    (review / 'review-pipeline.json').write_text(json.dumps(report, indent=2) + '\n')

def run(name, args, marker, timeout=180):
    assert sha(source / 'export/garden-of-dreams.glb') == expected
    assert sha(source / 'blender/authoring.blend') == prep['authoring_sha256']
    log = logs / (name + '.log')
    phase = {'name': name, 'status': 'running', 'command': args, 'log': str(log)}
    report['phases'].append(phase)
    save()
    print('CANVAS_LIT_REVIEW_START', name, flush=True)
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
    print('CANVAS_LIT_REVIEW_PASS', name, flush=True)

def run_expected_rejection(name, args, expected_error):
    log = logs / (name + '.log')
    phase = {'name': name, 'status': 'running', 'command': args, 'log': str(log), 'expected_exit_code': 1, 'expected_error': expected_error}
    report['phases'].append(phase)
    save()
    print('CANVAS_LIT_NEGATIVE_START', name, flush=True)
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
    print('CANVAS_LIT_NEGATIVE_PASS', name, flush=True)


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
    shutil.copyfile(__file__, review / 'executed-review-pipeline.py')
    source_logs = review / 'source-phase-logs'
    source_logs.mkdir()
    log_hashes = {}
    for phase in bake['phases']:
        p = Path(phase['log'])
        destination = source_logs / p.name
        shutil.copyfile(p, destination)
        assert sha(destination) == sha(p)
        log_hashes[phase['name']] = sha(destination)
    report['completed_source_phase_log_sha256'] = log_hashes
    shutil.copytree(source / 'export/lightmaps', review / 'export/lightmaps')
    for name in ['full-lighting-refresh.json', 'lightmaps-coverage.json', 'lightmap-pixels.json', 'terminal-spill-pixels.json']:
        shutil.copyfile(source / 'export' / name, review / 'export' / name)
    commands = [
        ('coverage', ['verify_lightmaps.py', '--current', '--require-all'], 'BAKE_COVERAGE 124 / 124'),
        ('sync-full', ['sync_full_lightmaps.py'], 'FULL_LIGHTMAP_CATALOG_PASS'),
        ('sync-demo', ['sync_lightmaps.py', '--demo'], 'Synced'),
        ('sync-priority2', ['sync_priority2_lightmaps.py'], 'PRIORITY2_LIGHTMAPS_PASS'),
        ('sync-wash', ['sync_backdrop_wash.py'], 'BACKDROP_WASH_CATALOG_PASS'),
        ('sync-spill', ['sync_terminal_spill.py'], 'TERMINAL_SPILL_CATALOG_PASS'),
    ]
    for label, args, marker in commands:
        run(label, [sys.executable, str(review / 'scripts' / args[0]), *args[1:]], marker)
    pngs = {}
    for name, count in {'full-index.json': 124, 'demo-index.json': 33, 'priority2-index.json': 29, 'backdrop-wash-index.json': 6, 'terminal-spill-index.json': 7}.items():
        data = json.loads((game / 'lightmaps' / name).read_text())
        assert len(data) == count
        assert {p['source_glb_sha256'] for p in data.values()} == {expected}
        for record in data.values():
            for side in record.get('sides', {'front': record}).values():
                texture = side['texture']
                assert sha(review / 'export/lightmaps' / texture) == sha(game / 'lightmaps' / texture)
                pngs[texture] = sha(game / 'lightmaps' / texture)
    assert len(pngs) == 141
    report['source_engine_png_sha256'] = pngs
    save()
    godot = '/Applications/Godot.app/Contents/MacOS/Godot'
    head = [godot, '--headless', '--path', str(game)]
    native = [godot, '--path', str(game), '--windowed', '--resolution', '1410x600']
    run('candidate-cold-import', head + ['--editor', '--import'], 'Godot Engine', 300)
    run('configure-lightmap-caps', [sys.executable, str(review / 'scripts/configure_lightmap_imports.py'), '--size-limit', '256', '--imperial-lossless512', '--ouxiang-lossless512'], 'Configured')
    run('candidate-configured-import', head + ['--editor', '--import'], 'Godot Engine', 300)
    run('native-source-contract', head + ['--script', 'res://tests/test_import_source_contract.gd', '--', 'res://assets/garden-of-dreams.glb', 'res://tests/source-contract.json', str(review / 'native-import-contract.json')], 'IMPORT_SOURCE_CONTRACT_PASS')
    run('full-lighting', head + ['--script', 'res://tests/test_full_scene_lighting.gd', '--', '--imperial-lossless512', '--ouxiang-lossless512'], 'FULL_SCENE_LIGHTING_PASS')
    for label, script, marker in [('wash', 'test_baked_backdrop_wash.gd', 'BAKED_BACKDROP_WASH_PASS'), ('spill', 'test_terminal_spill.gd', 'TERMINAL_SPILL_PASS')]:
        for mode, args in [('normal', []), ('demo', ['--demo'])]:
            run(label + '-' + mode, head + ['--script', 'res://tests/' + script, '--', *args], marker)
    blender = ['/Applications/Blender.app/Contents/MacOS/Blender', '--background', '--threads', '8', '--python-exit-code', '1', '--python']
    reexport = work / 'saved-source-reproduction'
    assert not reexport.exists()
    run('default-sixteen-reexports', ['/Applications/Blender.app/Contents/MacOS/Blender', '--background', str(review / 'blender/authoring.blend'), '--threads', '8', '--python-exit-code', '1', '--python', str(review / 'scripts/verify_saved_garden_candidate.py'), '--', '--source-root', str(review), '--output-root', str(reexport)], 'SAVED_GARDEN_CANDIDATE_PASS', 300)
    run('site-source-audit', blender + [str(review / 'scripts/audit_site_sources.py')], 'SITE_SOURCE_AUDIT_RECORDED', 240)
    sites = json.loads((review / 'export/site-source-audit.json').read_text())['sites']
    assert len(sites) == 14
    for name, site in sites.items():
        assert not site['structural_differences_from_authoring'] and site['signs_match_authoring'] and not site['missing_current_bakes'] and not site['triggers_without_room_id'], name
    run('western-supported-route', head + ['--script', 'res://tests/test_western_route.gd'], 'WESTERN_ROUTE_PASS')
    for mode, args in [('normal', []), ('demo', ['--demo'])]:
        run('palette-transfer-' + mode, native + ['--script', 'res://tests/test_garden_palette_transfer.gd', '--', '--output=' + str(review / ('palette-transfer-' + mode + '.json')), *args], 'GARDEN_PALETTE_TRANSFER_PASS', 160)
    run_expected_rejection('candidate-corrupt-canvas', native + ['--script', 'res://tests/test_garden_palette_transfer.gd', '--', '--contract=res://tests/canvas-palette-contract.json', '--corrupt-plain', '--output=' + str(review / 'corrupt-canvas-unexpected-success.json')], 'GARDEN_PALETTE_TRANSFER_REJECTED: Active baked base color differs: MAT_stage_canvas')
    captures = review / 'review-captures'
    captures.mkdir()
    base_game = review / 'baseline-godot'
    assert sha(base_game / 'assets/garden-of-dreams.glb') == baseline
    run('baseline-cold-import', [godot, '--headless', '--path', str(base_game), '--editor', '--import'], 'Godot Engine', 300)
    run_expected_rejection('baseline-canvas-palette-red', [godot, '--path', str(base_game), '--windowed', '--resolution', '1410x600', '--script', 'res://tests/test_garden_palette_transfer.gd', '--', '--contract=res://tests/canvas-red-contract.json', '--output=' + str(review / 'baseline-canvas-unexpected-success.json')], 'GARDEN_PALETTE_TRANSFER_REJECTED: Imported base color differs: MAT_stage_canvas')
    for mode, root, digest in [('baseline', base_game, baseline), ('candidate', game, expected)]:
        output = captures / mode
        run(mode + '-lit-originals', [godot, '--path', str(root), '--windowed', '--resolution', '1410x600', '--script', str(work / 'render-water-edge-lit.gd'), '--', '--output=' + str(output), '--candidate'], 'WATER_EDGE_COMPARISON_RESULT 6 originals; 0 failures', 180)
        data = verify_captures(output, digest, 6)
        assert len(data['bank_top_ray_hits']) == 54
        assert all(row['site_bakes_enabled'] and not row['camera_transition_running'] for row in data['rows'])
    for mode, args, count in [('normal', [], 13), ('touch', ['--touch'], 12), ('density', ['--density'], 10)]:
        output = captures / ('ziling-' + mode)
        run('ziling-' + mode, native + ['--script', 'res://tests/test_ziling_framing.gd', '--', '--output=' + str(output), *args], 'ZILING_FRAMING_RESULT ' + str(count) + ' originals; 0 failures', 160)
        verify_captures(output, expected, count)
    for label, script, marker in [('ouxiang', 'test_oux_portrait_framing.gd', 'OUXIANG_FRAMING_PASS'), ('architecture', 'test_portrait_architecture.gd', 'PORTRAIT_ARCHITECTURE_RESULT'), ('hengwu', 'test_hengwu_detail_framing.gd', 'HENGWU_DETAIL_FRAMING_RESULT'), ('tubi', 'test_tubi_framing.gd', 'TUBI_FRAMING_RESULT'), ('qiushuang', 'test_qiushuang_framing.gd', 'QIUSHUANG_FRAMING_RESULT'), ('pond', 'test_pond_view.gd', 'POND_VIEW_PASS')]:
        run('adjacent-' + label, native + ['--script', 'res://tests/' + script, '--', '--output=' + str(captures / label)], marker, 160)
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
    assert len(report['phases']) == len({p['name'] for p in report['phases']}) == 40
    assert sum(p['status'] == 'passed' and p['exit_code'] == 0 for p in report['phases']) == 38
    assert sum(p['status'] == 'passed_expected_rejection' and p['exit_code'] == 1 for p in report['phases']) == 2

    for name, digest in frozen.items():
        assert sha(source / name) == digest, name
    assert sha(game / 'runtime/entry_route.gd') == sha(repo / 'godot/runtime/entry_route.gd') == prep['runtime_sha256']
    report.update(status='complete_canvas_technical_review_direct_allroom_and_moving_visual_review_pending', finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('CANVAS_LIT_TECHNICAL_REVIEW_COMPLETE', flush=True)
except BaseException as error:
    report.update(status='failed', error=str(error))
    save()
    raise
