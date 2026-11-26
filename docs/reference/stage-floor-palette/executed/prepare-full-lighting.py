"""Package the selected canvas candidate and bake complete matching source lighting."""
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
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette'
root = work / 'candidate'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
assert load(root / 'export-preservation.json')['status'] == 'canvas_palette_export_preservation_passed'
assert load(work / 'canvas-red.json')['status'] == 'saved_canvas_palette_rejected'
assert load(work / 'canvas-green.json')['status'] == 'saved_canvas_palette_passed'
assert load(work / 'unbaked-native-probe/direct-original-review.json')['status'] == 'unbaked_canvas_proposal_selected_fresh_lighting_required'
native = load(work / 'unbaked-native-probe/pipeline.json')
assert native['status'] == 'unbaked_canvas_native_comparison_complete_direct_review_pending'
for pid in [native['pid'], *[p['pid'] for p in native['phases']]]:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        continue
    raise AssertionError(('Prior native worker is still alive', pid))
assert not (root / 'scripts').exists()
shutil.copytree(repo / 'scripts', root / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(work / 'test_saved_canvas_palette.py', root / 'scripts/test_saved_canvas_palette.py')
constructor = root / 'scripts/complete_garden.py'
old = "C=sites['stage'];ground=mat('MAT_stage_canvas',(.055,.095,.037))"
new = "C=sites['stage'];ground=mat('MAT_stage_canvas',(.065,.060,.055))"
assert constructor.read_text().count(old) == 1
constructor.write_text(constructor.read_text().replace(old, new))
(root / 'export/lightmaps').mkdir()
(root / 'blender/sites').mkdir()
(root / 'blender/kits').mkdir()
(root / 'lighting-preparation-logs').mkdir()
shutil.copyfile(repo / 'blender/kits/KIT_water.blend', root / 'blender/kits/KIT_water.blend')
shutil.copytree(repo / 'export/kits/water', root / 'export/kits/water')
shutil.copyfile(repo / 'export/site-wash-rig.json', root / 'export/site-wash-rig.json')
library_helper = root / 'scripts/prepare_candidate_libraries.py'
old_guard = "assert root!=repo and repo not in root.parents,'Use a separate candidate tree'"
new_guard = "assert root==repo and root==Path('/Users/auchan/projects/garden-of-dreams/.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette/candidate'), 'This frozen isolated source only'"
assert library_helper.read_text().count(old_guard) == 1
helper_original = sha(library_helper)
library_helper.write_text(library_helper.read_text().replace(old_guard, new_guard))
report = {'status': 'preparing', 'root': str(root), 'orchestrator_pid': os.getpid(),
          'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'source_glb_sha256': sha(root / 'export/garden-of-dreams.glb'),
          'authoring_sha256': sha(root / 'blender/authoring.blend'),
          'library_helper_original_sha256': helper_original,
          'library_helper_frozen_sha256': sha(library_helper), 'phases': [],
          'scope': 'Selected warm gray canvas base color only; all4467objects/other47materials/cameras/COL/markers retained. Complete portable15libraries and fresh six-phase source lighting. No canonical adoption, matched-lit/14site appearance, phone or service acceptance.'}


def save():
    (root / 'lighting-preparation.json').write_text(json.dumps(report, indent=2) + '\n')


def run(name, command, marker):
    log = root / 'lighting-preparation-logs' / (name + '.log')
    phase = {'name': name, 'command': command, 'status': 'running', 'log': str(log)}
    report['phases'].append(phase)
    save()
    print('CANVAS_SOURCE_START', name, flush=True)
    with log.open('w') as out:
        child = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT)
        phase['pid'] = child.pid
        save()
        phase['exit_code'] = child.wait()
    text = log.read_text(errors='replace')
    assert phase['exit_code'] == 0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:', text), text[-3000:]
    phase.update(status='passed', log_sha256=sha(log))
    save()
    print('CANVAS_SOURCE_PASS', name, flush=True)


try:
    save()
    run('water-contract', [sys.executable, str(root / 'scripts/verify_water_kit.py')], 'WATER_EXPORT_PASS')
    blender = ['/Applications/Blender.app/Contents/MacOS/Blender', '--background', '--threads', '8', '--python-exit-code', '1', '--python']
    run('site-libraries', blender + [str(library_helper), '--', '--root', str(root)], 'CANDIDATE_LIBRARIES_PREPARED')
    run('shared-wash-receivers', blender + [str(root / 'scripts/package_site_washes.py'), '--', '--portable-master'], 'SITE_WASH')
    assert sha(root / 'blender/authoring.blend') == report['authoring_sha256']
    assert sha(root / 'export/garden-of-dreams.glb') == report['source_glb_sha256']
    assert len(list((root / 'blender/sites').glob('SITE_*.blend'))) == 15
    frozen = {str(p.relative_to(root)): sha(p)
              for folder in ['blender', 'scripts', 'export/sites', 'export/kits/water']
              for p in sorted((root / folder).rglob('*'))
              if p.is_file() and '__pycache__' not in str(p)}
    for name in ['export/garden-of-dreams.glb', 'export/site-wash-rig.json']:
        frozen[name] = sha(root / name)
    assert not any((root / 'export/lightmaps').iterdir())
    (root / 'full-lighting-inputs.json').write_text(json.dumps({'files': frozen, 'empty_lightmaps_before_refresh': True,
        'scope': 'Selected saved canvas candidate/libraries/master, current unchanged water kit, all exports and executed helpers frozen before complete fresh lighting.'}, indent=2) + '\n')
    report['status'] = 'full_source_bake_running'
    save()
    run('full-lighting', [sys.executable, str(root / 'scripts/refresh_full_lighting.py'), '--samples', '128', '--size', '1024'], 'FULL_SOURCE_LIGHTING_REFRESH_PASS')
    for name, digest in frozen.items():
        assert sha(root / name) == digest, name
    report.update(status='complete_source_lighting_passed_native_review_pending',
                  finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('CANVAS_COMPLETE_SOURCE_LIGHTING_PASS', flush=True)
except BaseException as error:
    report.update(status='failed', error=str(error))
    save()
    raise
