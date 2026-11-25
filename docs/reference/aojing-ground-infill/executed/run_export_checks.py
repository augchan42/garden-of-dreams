"""Run source contracts and canonical export in one isolated candidate root."""
from pathlib import Path
import datetime, hashlib, json, os, re, subprocess, sys

r = Path(__file__).resolve().parent
roof = Path('/tmp/garden-corridor-roof-full-20261011')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source_sha = '9b6c83259f79aeb56bbdc67b1fd939b2e9ff69977bcb941cb8141b2ce329b66e'
assert sha(r/'blender/authoring.blend') == source_sha
assert not (r/'export-pipeline.json').exists(), 'Inspect the existing job instead of restarting it'
report = {'status': 'running', 'pid': os.getpid(), 'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'authoring_sha256': source_sha, 'phases': [], 'scope': 'Separate source/export/UV checks only. No lighting, native import, adoption, user-editor or device action.'}

def save():
    p = r/'export-pipeline.json'; t = p.with_suffix('.new'); t.write_text(json.dumps(report, indent=2)+'\n'); t.replace(p)

def run(name, command, marker):
    phase = {'name': name, 'status': 'running', 'command': command, 'log': str(r/(name+'.log'))}
    report['phases'].append(phase); save()
    with Path(phase['log']).open('w') as stream:
        child = subprocess.Popen(command, cwd=r, stdout=stream, stderr=subprocess.STDOUT)
        phase['pid'] = child.pid; save(); phase['exit_code'] = child.wait()
    text = Path(phase['log']).read_text(errors='replace')
    assert phase['exit_code'] == 0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:', text), text[-3000:]
    assert sha(r/'blender/authoring.blend') == source_sha, 'Export or fixture changed source'
    phase.update(status='passed', log_sha256=sha(Path(phase['log']))); save()
    print('AOJING_EXPORT_PHASE_PASS', name, flush=True)

blender = ['/Applications/Blender.app/Contents/MacOS/Blender', '--background', '--threads', '1', '--python-exit-code', '1', str(r/'blender/authoring.blend'), '--python']
try:
    save()
    inputs = {str(p.relative_to(r)): sha(p) for p in (r/'scripts').glob('*.py')}
    inputs['blender/authoring.blend'] = source_sha
    (r/'export-inputs.json').write_text(json.dumps({'files': inputs, 'comparison_source_glb_sha256': sha(roof/'export/garden-of-dreams.glb')}, indent=2)+'\n')
    run('source-contract-green', blender+[str(r/'scripts/test_aojing_ground.py'), '--', '--report', str(r/'export/aojing-ground-contract.json')], 'AOJING_GROUND_CONTRACT')
    run('palette-users-green', blender+[str(r/'scripts/test_saved_canvas_palette.py'), '--', '--report', str(r/'export/canvas-palette-contract.json')], 'SAVED_CANVAS_PALETTE_RESULT 0 failures')
    run('canonical-export', blender+[str(r/'scripts/export_garden.py'), '--', '--output-root', str(r)], '"total_triangles": 264985')
    run('export-preservation', [sys.executable, str(r/'verify_ground_export.py'), '--before', str(roof/'export/garden-of-dreams.glb'), '--after', str(r/'export/garden-of-dreams.glb'), '--output', str(r/'export/export-preservation.json')], 'AOJING_GROUND_EXPORT_PRESERVATION_PASS')
    run('uv2-validation', [sys.executable, str(r/'scripts/verify_uv2.py')], 'UV2_MESHES 167 OVERLAPPING {}')
    run('corridor-roof-uv', [sys.executable, str(r/'scripts/verify_corridor_roof_uv.py')], 'CORRIDOR_ROOF_UV_PASS 784')
    changed = [p.name for p in sorted((roof/'export/sites').glob('*.glb')) if sha(p) != sha(r/'export/sites'/p.name)]
    assert changed == ['SITE_stage.glb'], changed
    for n, digest in inputs.items(): assert sha(r/n) == digest, n
    report.update(status='source_export_uv_passed_lighting_native_review_pending', source_glb_sha256=sha(r/'export/garden-of-dreams.glb'),
                  unchanged_other_site_files=14, changed_site_files=changed)
    save(); print('AOJING_GROUND_EXPORT_PIPELINE_PASS', flush=True)
except BaseException as error:
    report.update(status='failed', error=str(error)); save(); raise
