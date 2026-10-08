"""Wait for the existing full review, then verify the saved source once."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

REPO = Path('/Users/auchan/projects/garden-of-dreams')
SOURCE = Path(json.loads(Path('/tmp/garden-neutral-atlas-full-source.json').read_text())['folder']).resolve()
DISPATCH = json.loads(Path('/tmp/garden-neutral-atlas-review-dispatch.json').read_text())
ROOT = Path(tempfile.mkdtemp(prefix='garden-neutral-atlas-source-verified-')).resolve()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs = ['verify_saved_garden_candidate.py', 'garden_material_palette.py',
          'nunnery_path_layout.py', 'export_garden.py', 'gltf_paint_contract.py',
          'pavilion_tile_lightmap_uv.py', 'imperial_tile_lightmap_uv.py',
          'ouxiang_tile_lightmap_uv.py']
report = {'status': 'waiting_for_existing_native_review', 'folder': str(ROOT),
          'orchestrator_pid': os.getpid(), 'source_root': str(SOURCE),
          'started_at': datetime.now(timezone.utc).isoformat(),
          'canonical_inputs': {name: sha(REPO/'scripts'/name) for name in inputs},
          'scope': 'Single sequential read-only native saved-source check and default reexport. No bake, asset edits or adoption.'}

def save():
    (ROOT/'verification.json').write_text(json.dumps(report, indent=2)+'\n')

def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False

save()
Path('/tmp/garden-neutral-atlas-source-verified.json').write_text(json.dumps(
    {'folder': str(ROOT), 'report': str(ROOT/'verification.json'),
     'orchestrator_pid': os.getpid()}, indent=2)+'\n')
try:
    while True:
        dispatch = json.loads(Path(DISPATCH['report']).read_text())
        if dispatch['status'] == 'failed':
            raise RuntimeError(('Existing native review failed', dispatch.get('error')))
        if dispatch['status'] == 'technical_review_complete_visual_review_pending' and not alive(dispatch['orchestrator_pid']):
            break
        if not alive(dispatch['orchestrator_pid']):
            raise RuntimeError('Existing review exited without successful completion')
        time.sleep(5)
    review_pointer = json.loads(Path('/tmp/garden-neutral-atlas-full-review.json').read_text())
    review_file = Path(review_pointer['report'])
    review = json.loads(review_file.read_text())
    assert review['status'] == 'technical_checks_complete_visual_review_pending'
    assert len(review['phases']) == 42 and all(p['status'] == 'passed' for p in review['phases'])
    assert not alive(review['orchestrator_pid'])
    for name, reason in [('reject-palette-plain', 'Active baked base color differs'),
                         ('reject-palette-atlas', 'Atlas color swatch differs from reviewed palette')]:
        phase = next(p for p in review['phases'] if p['name'] == name)
        assert phase['exit_code'] == 1 and reason in Path(phase['log']).read_text()
    prepared = json.loads((SOURCE/'source-preparation.json').read_text())
    baked = json.loads((SOURCE/'export/full-lighting-refresh.json').read_text())
    assert prepared['status'] == 'complete_source_bake_passed_native_review_pending'
    assert baked['status'] == 'source_complete' and len(baked['phases']) == 6
    assert not alive(prepared['orchestrator_pid']) and not alive(baked['orchestrator_pid'])
    report['source_glb_sha256'] = prepared['source_glb_sha256']
    report['authoring_sha256'] = prepared['authoring_sha256']
    assert sha(SOURCE/'export/garden-of-dreams.glb') == report['source_glb_sha256']
    assert sha(SOURCE/'blender/authoring.blend') == report['authoring_sha256']
    for name, digest in report['canonical_inputs'].items():
        assert sha(REPO/'scripts'/name) == digest, ('Canonical input changed', name)
    report['completed_review_report_sha256'] = sha(review_file)
    report['command'] = ['/Applications/Blender.app/Contents/MacOS/Blender', '--background',
                         str(SOURCE/'blender/authoring.blend'), '--python-exit-code', '1',
                         '--python', str(REPO/'scripts/verify_saved_garden_candidate.py'),
                         '--', '--source-root', str(SOURCE), '--output-root', str(ROOT)]
    report['status'] = 'native_verification_running'
    log = ROOT/'native-source-verification.log'
    with log.open('w') as out:
        child = subprocess.Popen(report['command'], stdout=out, stderr=subprocess.STDOUT)
        report['native_pid'] = child.pid
        save()
        report['exit_code'] = child.wait()
    text = log.read_text(errors='replace')
    assert report['exit_code'] == 0 and 'SAVED_GARDEN_CANDIDATE_PASS' in text, text[-4000:]
    assert not re.search(r'Traceback|^Error:', text, re.M), text[-4000:]
    verified = json.loads((ROOT/'saved-source-verification.json').read_text())
    assert verified['status'] == 'saved_candidate_and_default_exports_verified'
    assert verified['authoring_sha256'] == report['authoring_sha256']
    assert verified['default_export_equality']['garden-of-dreams.glb'] == report['source_glb_sha256']
    assert len(verified['default_export_equality']) == 16
    report['native_log_sha256'] = sha(log)
    report['native_report_sha256'] = sha(ROOT/'saved-source-verification.json')
    report['default_export_equality'] = verified['default_export_equality']
    report['status'] = 'saved_source_and_default_export_passed_visual_adoption_pending'
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    save()
    print('NEUTRAL_ATLAS_SOURCE_VERIFICATION_PASS', ROOT, flush=True)
except BaseException as error:
    report['status'] = 'failed'
    report['error'] = str(error)
    save()
    raise
