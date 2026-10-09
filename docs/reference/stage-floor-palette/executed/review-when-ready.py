"""Observe the existing bake, then dispatch the prepared review without overlap."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

work = Path('/Users/auchan/projects/garden-of-dreams/.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette')
source = work / 'candidate'
report_path = work / 'review-queue.json'
assert not report_path.exists(), 'Do not start another observer for this source'
script = work / 'run-lit-review.py'
expected_script = hashlib.sha256(script.read_bytes()).hexdigest()
record = {'status': 'waiting_for_existing_source_worker', 'observer_pid': os.getpid(), 'source_session_id': 48984, 'review_script_sha256': expected_script, 'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'scope': 'This observer runs no native application while any source parent or child remains alive. On complete source reports and absent processes, launch exactly one sequential prepared review. A failure stops the queue. No restart, adoption or visual acceptance.'}

def save():
    report_path.write_text(json.dumps(record, indent=2) + '\n')

def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False

try:
    save()
    deadline = time.monotonic() + 10800
    while True:
        bake = json.loads((source / 'export/full-lighting-refresh.json').read_text())
        prep = json.loads((source / 'lighting-preparation.json').read_text())
        assert bake['status'] != 'failed' and prep['status'] != 'failed', 'Existing bake failed; do not retry it'
        assert bake['source_glb_sha256'] == 'c9d4fb308730733af2175c424449f8a63b731674d2527df2168a260cc0f5013e'
        pids = sorted({bake['orchestrator_pid'], prep['orchestrator_pid'], *[p['pid'] for p in bake['phases']], *[p['pid'] for p in prep['phases']]})
        active = [pid for pid in pids if alive(pid)]
        complete = bake['status'] == 'source_complete' and prep['status'] == 'complete_source_lighting_passed_native_review_pending'
        assert active or complete, 'Source worker exited without complete reports'
        if complete and not active:
            record.update(source_processes_verified_absent=pids, source_finished_at=bake['finished_at'], status='dispatching_prepared_review')
            save()
            break
        assert time.monotonic() < deadline, 'Observation deadline; preserve existing source worker'
        time.sleep(15)
    assert hashlib.sha256(script.read_bytes()).hexdigest() == expected_script
    log = work / 'queued-review-output.log'
    with log.open('w') as out:
        child = subprocess.Popen([sys.executable, str(script)], stdout=out, stderr=subprocess.STDOUT)
        record.update(status='sequential_native_review_running', review_pid=child.pid, review_log=str(log))
        save()
        print('CANVAS_QUEUED_REVIEW_START', child.pid, flush=True)
        record['review_exit_code'] = child.wait()
    record['review_log_sha256'] = hashlib.sha256(log.read_bytes()).hexdigest()
    assert record['review_exit_code'] == 0, log.read_text(errors='replace')[-4000:]
    record.update(status='prepared_review_terminal_direct_visual_review_required', finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('CANVAS_QUEUED_REVIEW_COMPLETE_DIRECT_VISUAL_REVIEW_REQUIRED', flush=True)
except BaseException as error:
    record.update(status='failed', error=str(error))
    save()
    raise
