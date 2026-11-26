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
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/island-face-source'
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
assert bake['status'] == 'source_complete', 'Wait for existing session74569; never start a second source bake'
assert preparation['status'] == 'complete_source_lighting_passed_native_review_pending'
for pid in [bake['orchestrator_pid'], preparation['orchestrator_pid'], *[p['pid'] for p in bake['phases']]]:
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
report = {'status': 'running', 'pid': os.getpid(), 'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'candidate_glb_sha256': expected, 'baseline_glb_sha256': baseline, 'authoring_sha256': prep['authoring_sha256'], 'frozen_inputs_verified': len(frozen), 'phases': [], 'scope': 'Focused isolated island source review. Current baseline and repaired candidate use their matching complete lightmaps and unchanged game runtime/cameras. Existing PR15 full tours are previous-source evidence. No new all-site art, phone, sustained, service or production acceptance.'}

def save():
    (review / 'review-pipeline.json').write_text(json.dumps(report, indent=2) + '\n')

def run(name, args, marker, timeout=180):
    assert sha(source / 'export/garden-of-dreams.glb') == expected
    assert sha(source / 'blender/authoring.blend') == prep['authoring_sha256']
    log = logs / (name + '.log')
    phase = {'name': name, 'status': 'running', 'command': args, 'log': str(log)}
    report['phases'].append(phase)
    save()
    print('ISLAND_LIT_REVIEW_START', name, flush=True)
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
    print('ISLAND_LIT_REVIEW_PASS', name, flush=True)

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
    captures = review / 'review-captures'
    captures.mkdir()
    base_game = review / 'baseline-godot'
    assert sha(base_game / 'assets/garden-of-dreams.glb') == baseline
    run('baseline-cold-import', [godot, '--headless', '--path', str(base_game), '--editor', '--import'], 'Godot Engine', 300)
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
    run('texture-memory-normal', native + ['--script', 'res://tests/audit_runtime_textures.gd', '--', '--output=' + str(review / 'texture-memory-normal.json')], 'RUNTIME_TEXTURE_INVENTORY_PASS', 160)
    for name, digest in frozen.items():
        assert sha(source / name) == digest, name
    assert sha(game / 'runtime/entry_route.gd') == sha(repo / 'godot/runtime/entry_route.gd') == prep['runtime_sha256']
    report.update(status='focused_technical_review_complete_direct_lit_visual_review_pending', finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('ISLAND_LIT_TECHNICAL_REVIEW_COMPLETE', flush=True)
except BaseException as error:
    report.update(status='failed', error=str(error))
    save()
    raise
