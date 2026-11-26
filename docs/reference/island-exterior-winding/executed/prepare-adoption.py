"""Prepare or install the reviewed island repair with reversible file backups."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/island-face-source'
source = work / 'candidate'
review = work / 'lit-native-review'
adoption = work / 'adoption'
stage = adoption / 'stage'
backup = adoption / 'backup'
baseline = '7a9fc523bc1517941cc248c040877b86f9cd00a11654c6c31e40f3acc089632f'
candidate = '73267e2b17c52531ad6bc1e9df1279634564e93e3ef04519b2f27ade26ec178e'
old_author = '074ab2014d9122e207783d9e7c7992f9dfc9197a6f380a2d6f5e8c0c05e31978'
new_author = '2b07ce48ffa3011f9a2da01535a3fc84171bdc00b2ced2abad0ce8f338fd49ed'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
load = lambda path: json.loads(Path(path).read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def snapshot(path):
    if not path.exists():
        return None
    assert not path.is_symlink(), path
    if path.is_file():
        return {'file': sha(path)}
    return {str(p.relative_to(path)): sha(p) for p in sorted(path.rglob('*'))
            if p.is_file() and not p.name.endswith(('.blend1', '.blend2'))}


def preflight():
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=repo,
                                   text=True).strip() == 'codex/island-exterior-winding'
    assert sha(repo / 'export/garden-of-dreams.glb') == baseline
    assert sha(repo / 'godot/assets/garden-of-dreams.glb') == baseline
    assert sha(repo / 'blender/authoring.blend') == old_author
    result = load(review / 'review-pipeline.json')
    assert result['status'] == 'focused_technical_review_complete_direct_lit_visual_review_pending'
    assert result['candidate_glb_sha256'] == sha(source / 'export/garden-of-dreams.glb') == candidate
    assert result['authoring_sha256'] == sha(source / 'blender/authoring.blend') == new_author
    assert len(result['phases']) == len({p['name'] for p in result['phases']}) == 25
    for phase in result['phases']:
        assert phase['status'] == 'passed' and phase['exit_code'] == 0
        assert sha(phase['log']) == phase['log_sha256']
    bake = load(source / 'export/full-lighting-refresh.json')
    preparation = load(source / 'lighting-preparation.json')
    assert bake['status'] == 'source_complete'
    assert preparation['status'] == 'complete_source_lighting_passed_native_review_pending'
    assert len(bake['phases']) == 6
    pids = [result['pid'], preparation['orchestrator_pid'], bake['orchestrator_pid']]
    pids += [p['pid'] for p in bake['phases']] + [p['pid'] for p in result['phases']]
    for pid in pids:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            continue
        raise AssertionError(('Managed native process remains alive', pid))
    frozen = load(source / 'full-lighting-inputs.json')['files']
    assert len(frozen) == 258
    for name, digest in frozen.items():
        assert sha(source / name) == digest, name
    assert len(result['source_engine_png_sha256']) == 141
    for name, digest in result['source_engine_png_sha256'].items():
        assert sha(source / 'export/lightmaps' / name) == digest
        assert sha(review / 'godot/lightmaps' / name) == digest
    native = load(review / 'native-import-contract.json')
    assert native['passed'] and native['cameras_checked'] == 42
    assert native['colliders_checked'] == native['physics_rays_passed'] == 454
    assert native['marker_metadata_checked'] == 71 and native['render_meshes_snapshotted'] == 167
    saved = load(work / 'saved-source-reproduction/saved-source-verification.json')
    assert saved['status'] == 'saved_candidate_and_default_exports_verified'
    assert saved['authoring_sha256'] == new_author and len(saved['default_export_equality']) == 16
    for name, digest in saved['default_export_equality'].items():
        assert sha(source / 'export' / name) == digest
        assert sha(work / 'saved-source-reproduction/export' / name) == digest
    visual = load(review / 'direct-original-visual-review.json')
    assert visual['status'] == 'island_winding_repair_accepted_final_site_art_open'
    assert len(visual['directly_reviewed_originals_sha256']) >= 6
    for name, digest in visual['directly_reviewed_originals_sha256'].items():
        assert sha(review / name) == digest
    assert sha(repo / 'godot/runtime/entry_route.gd') == sha(review / 'godot/runtime/entry_route.gd')
    return {'candidate_glb_sha256': candidate, 'authoring_sha256': new_author,
            'native_review_sha256': sha(review / 'review-pipeline.json'),
            'direct_visual_review_sha256': sha(review / 'direct-original-visual-review.json'),
            'frozen_inputs_checked': len(frozen), 'source_phases': 6, 'native_phases': 25}


def prepare():
    verification = preflight()
    assert not adoption.exists(), 'Preserve earlier attempts; prepare explicit continuation'
    stage.mkdir(parents=True)
    backup.mkdir()
    pairs = [(name, source / name) for name in [
        'blender/authoring.blend', 'blender/master.blend', 'blender/sites',
        'export/garden-of-dreams.glb', 'export/sites', 'export/lightmaps',
        'scripts/refine_western_sites.py', 'scripts/test_saved_island_shell.py',
        'export/manifest.json', 'export/candidate-libraries.json',
        'export/full-lighting-refresh.json', 'export/lightmap-pixels.json',
        'export/lightmaps-coverage.json', 'export/terminal-spill-pixels.json']]
    pairs += [(name, review / name) for name in [
        'godot/assets/garden-of-dreams.glb', 'godot/assets/garden-source.json',
        'godot/lightmaps', 'godot/tests/source-contract.json', 'export/site-source-audit.json']]
    pairs += [('export/full-lighting-inputs.json', source / 'full-lighting-inputs.json')]
    guards = {}
    # These tests and static JSON contracts bind to the complete assembly digest.
    # Retain every assertion and subject; update only that literal digest.
    for path in sorted((repo / 'godot/tests').rglob('*')):
        if not path.is_file() or path.suffix not in ('.gd', '.json'):
            continue
        text = path.read_text()
        if baseline not in text or path.name == 'source-contract.json':
            continue
        name = str(path.relative_to(repo))
        destination = stage / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text.replace(baseline, candidate))
        guards[name] = {'original_sha256': sha(path), 'candidate_sha256': sha(destination),
                        'digest_occurrences': text.count(baseline)}
    plan = {'status': 'prepared_not_applied', 'verification': verification, 'items': [],
            'digest_only_guard_changes': guards,
            'scope': '24 exterior island quads reverse winding; shape/material/camera/collision/runtime retained. Fresh matching lighting. Final site art, phones and services remain open.'}
    for name, path in pairs:
        assert path.exists(), ('Missing staged source', name)
        if snapshot(repo / name) == snapshot(path):
            continue
        out = stage / name
        out.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, out, ignore=shutil.ignore_patterns('*.blend1', '*.blend2'))
        else:
            shutil.copyfile(path, out)
        assert snapshot(out) == snapshot(path)
        plan['items'].append({'target': name, 'original': snapshot(repo / name), 'staged': snapshot(out)})
    for name, guard in guards.items():
        plan['items'].append({'target': name, 'original': snapshot(repo / name), 'staged': snapshot(stage / name)})
    write(adoption / 'plan.json', plan)
    shutil.copyfile(__file__, adoption / 'executed-adoption.py')
    print('ISLAND_ADOPTION_PREPARED', len(plan['items']), flush=True)


def apply():
    preflight()
    plan = load(adoption / 'plan.json')
    assert plan['status'] == 'prepared_not_applied' and not any(backup.rglob('*'))
    for item in plan['items']:
        assert snapshot(repo / item['target']) == item['original']
        assert snapshot(stage / item['target']) == item['staged']
    report = {'status': 'installing', 'candidate_glb_sha256': candidate, 'authoring_sha256': new_author,
              'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'checks': []}
    write(adoption / 'application.json', report)
    processed = []
    try:
        for item in plan['items']:
            target = repo / item['target']
            saved = backup / item['target']
            saved.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                os.replace(target, saved)
            processed.append((item['target'], False))
            os.replace(stage / item['target'], target)
            processed[-1] = (item['target'], True)
        godot = '/Applications/Godot.app/Contents/MacOS/Godot'
        head = [godot, '--headless', '--path', str(repo / 'godot')]
        native = [godot, '--path', str(repo / 'godot'), '--windowed', '--resolution', '1410x600']
        commands = [('installed-import', head + ['--editor', '--import'], 'Godot Engine')]
        for phase in load(review / 'review-pipeline.json')['phases']:
            if phase['name'] in ['native-source-contract', 'full-lighting', 'wash-normal',
                                 'wash-demo', 'spill-normal', 'spill-demo', 'western-supported-route']:
                markers = {'native-source-contract': 'IMPORT_SOURCE_CONTRACT_PASS',
                           'full-lighting': 'FULL_SCENE_LIGHTING_PASS', 'wash-normal': 'BAKED_BACKDROP_WASH_PASS',
                           'wash-demo': 'BAKED_BACKDROP_WASH_PASS', 'spill-normal': 'TERMINAL_SPILL_PASS',
                           'spill-demo': 'TERMINAL_SPILL_PASS', 'western-supported-route': 'WESTERN_ROUTE_PASS'}
                args = [arg.replace(str(review), str(repo)) for arg in phase['command']]
                if phase['name'] == 'native-source-contract':
                    args[-1] = str(adoption / 'installed-import-contract.json')
                commands.append(('installed-' + phase['name'], args, markers[phase['name']]))
        commands += [('installed-surface-materials', head + ['--script', 'res://tests/test_surface_materials.gd'], 'SURFACE_MATERIAL_PASS')]
        for mode, flags in [('normal', []), ('demo', ['--demo'])]:
            commands.append(('installed-palette-' + mode, native + ['--script', 'res://tests/test_garden_palette_transfer.gd', '--',
                             '--output=' + str(adoption / ('installed-palette-' + mode + '.json')), *flags], 'GARDEN_PALETTE_TRANSFER_PASS'))
        commands.append(('installed-ziling', native + ['--script', 'res://tests/test_ziling_framing.gd', '--',
                         '--output=' + str(adoption / 'installed-ziling')], 'ZILING_FRAMING_RESULT 13 originals; 0 failures'))
        commands.append(('installed-lit-originals', native + ['--script', str(work / 'render-water-edge-lit.gd'), '--',
                         '--output=' + str(adoption / 'installed-lit-originals'), '--candidate'], 'WATER_EDGE_COMPARISON_RESULT 6 originals; 0 failures'))
        for name, command, marker in commands:
            print('ISLAND_INSTALLED_START', name, flush=True)
            log = adoption / (name + '.log')
            phase = {'name': name, 'command': command, 'status': 'running', 'log': str(log)}
            report['checks'].append(phase)
            write(adoption / 'application.json', report)
            with log.open('w') as out:
                child = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT)
                phase['pid'] = child.pid
                write(adoption / 'application.json', report)
                try:
                    phase['exit_code'] = child.wait(timeout=300)
                except subprocess.TimeoutExpired:
                    child.terminate()
                    child.wait(timeout=30)
                    phase['exit_code'] = 124
            text = log.read_text(errors='replace')
            okay = phase['exit_code'] == 0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)', text)
            phase.update(status='passed' if okay else 'failed', log_sha256=sha(log))
            write(adoption / 'application.json', report)
            assert okay, (name, text[-3000:])
            print('ISLAND_INSTALLED_PASS', name, flush=True)
        for item in plan['items']:
            assert snapshot(repo / item['target']) == item['staged']
        report.update(status='working_island_source_adopted_installed_checks_passed',
                      finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        write(adoption / 'application.json', report)
        plan['status'] = 'applied'
        write(adoption / 'plan.json', plan)
        print('ISLAND_WORKING_SOURCE_ADOPTION_PASS', flush=True)
    except BaseException as error:
        report.update(status='rolling_back', error=str(error))
        write(adoption / 'application.json', report)
        for name, installed in reversed(processed):
            if installed and (repo / name).exists():
                os.replace(repo / name, stage / name)
            if (backup / name).exists():
                os.replace(backup / name, repo / name)
        report['status'] = 'rolled_back'
        write(adoption / 'application.json', report)
        raise


if __name__ == '__main__':
    apply() if '--apply' in sys.argv else prepare()
