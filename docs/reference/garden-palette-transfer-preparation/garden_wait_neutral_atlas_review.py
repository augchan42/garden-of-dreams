"""Wait for the existing atlas source job before running its separate review."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

pointer = json.loads(Path('/tmp/garden-neutral-atlas-full-source.json').read_text())
source = Path(pointer['folder']).resolve()
folder = source.parent/'review-dispatch'
folder.mkdir(exist_ok=False)
report_path = folder/'dispatch.json'
script = folder/'garden_review_neutral_atlas_full.py'
script.write_bytes(Path('/tmp/garden_review_neutral_atlas_full.py').read_bytes())
report = {'status':'waiting_for_existing_atlas_source', 'orchestrator_pid':os.getpid(),
          'source_root':str(source), 'source_report':pointer['report'],
          'review_script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
          'started_at':datetime.now(timezone.utc).isoformat(),
          'scope':'Sequential separate review dispatch. No native process starts before the existing complete atlas bake and source orchestration processes exit successfully. No production adoption.'}
def save():
    tmp = report_path.with_suffix('.tmp')
    tmp.write_text(json.dumps(report, indent=2)+'\n')
    tmp.replace(report_path)
save()
Path('/tmp/garden-neutral-atlas-review-dispatch.json').write_text(json.dumps({'folder':str(folder),'report':str(report_path),'orchestrator_pid':os.getpid()},indent=2)+'\n')


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


try:
    while True:
        prepared = json.loads(Path(pointer['report']).read_text())
        assert prepared['status'] != 'failed', ('Existing atlas preparation failed', prepared.get('error'))
        if prepared['status'] == 'complete_source_bake_passed_native_review_pending':
            baked = json.loads((source/'export/full-lighting-refresh.json').read_text())
            assert baked['status'] == 'source_complete' and len(baked['phases']) == 6
            assert all(p['status'] == 'passed' and p['exit_code'] == 0 for p in baked['phases'])
            if not alive(prepared['orchestrator_pid']) and not alive(baked['orchestrator_pid']):
                break
        elif not alive(prepared['orchestrator_pid']):
            raise RuntimeError('Existing source job exited without successful completion')
        time.sleep(5)
    report['source_glb_sha256'] = prepared['source_glb_sha256']
    report['authoring_sha256'] = prepared['authoring_sha256']
    assert hashlib.sha256((source/'export/garden-of-dreams.glb').read_bytes()).hexdigest() == report['source_glb_sha256']
    assert hashlib.sha256((source/'blender/authoring.blend').read_bytes()).hexdigest() == report['authoring_sha256']
    assert hashlib.sha256(script.read_bytes()).hexdigest() == report['review_script_sha256']
    report['status'] = 'running_native_review'
    save()
    log = folder/'review.log'
    with log.open('w') as out:
        child = subprocess.Popen([sys.executable, str(script)], stdout=out, stderr=subprocess.STDOUT)
        report['review_pid'] = child.pid
        save()
        report['exit_code'] = child.wait()
    report['review_log_sha256'] = hashlib.sha256(log.read_bytes()).hexdigest()
    assert report['exit_code'] == 0, log.read_text(errors='replace')[-4000:]
    review_pointer = json.loads(Path('/tmp/garden-neutral-atlas-full-review.json').read_text())
    reviewed = json.loads(Path(review_pointer['report']).read_text())
    assert reviewed['status'] == 'technical_checks_complete_visual_review_pending'
    assert len(reviewed['phases']) == 42 and all(p['status'] == 'passed' for p in reviewed['phases'])
    report['status'] = 'technical_review_complete_visual_review_pending'
    report['native_review_report'] = review_pointer['report']
    save()
    print('NEUTRAL_ATLAS_REVIEW_DISPATCH_COMPLETE', review_pointer['report'], flush=True)
except BaseException as error:
    report['status'] = 'failed'
    report['error'] = str(error)
    save()
    raise
