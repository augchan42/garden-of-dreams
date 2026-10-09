"""Repeat only the affected native capture modes after the full tour exits."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
from ziling_settle_transform import transform

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = Path(__file__).parent
review = Path('/tmp/garden-paving-review-20261010-v4')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
pipeline = load(review / 'review-pipeline.json')
assert pipeline['status'] == 'complete_paving_technical_review_direct_allroom_and_moving_visual_review_pending'
assert len(pipeline['phases']) == 45
for pid in [pipeline['pid'], *[p['pid'] for p in pipeline['phases']]]:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        continue
    raise AssertionError(('Full native worker still alive', pid))
assert not (review / 'ziling-timed-repeat.json').exists(), 'Preserve prior attempts'
test = review / 'godot/tests/test_ziling_framing.gd'
assert sha(test) == '3d7d3363fd057755e7a81712fea5a092c65e50a0c06f5eaf40c49484a251a11a'
shutil.copyfile(test, review / 'executed-ziling-before-timed-settle.gd')
shutil.copyfile(review / 'fixture-preparation.json', review / 'fixture-preparation-before-timed-settle.json')
updated = transform(test.read_text())
assert updated == (work / 'pending-ziling-settle.gd').read_text()
test.write_text(updated)
prep = load(review / 'fixture-preparation.json')
guard = prep['source_guard_changes']['test_ziling_framing.gd']
guard['before_timed_settle_sha256'] = guard['after_sha256']
guard['after_sha256'] = sha(test)
guard['change'] += '; test-only real250ms foliage settle and measured per-capture LOD assertions'
prep['ziling_timed_settle_seconds'] = .25
(review / 'fixture-preparation.json').write_text(json.dumps(prep, indent=2) + '\n')
shutil.copyfile(__file__, review / 'executed-ziling-timed-repeat.py')
shutil.copyfile(work / 'ziling_settle_transform.py', review / 'executed-ziling-settle-transform.py')
report = {'status': 'running', 'pid': os.getpid(), 'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'source_glb_sha256': pipeline['candidate_glb_sha256'], 'runtime_sha256': sha(review / 'godot/runtime/entry_route.gd'),
          'prior_pipeline_sha256': sha(review / 'review-pipeline.json'), 'test_sha256': sha(test), 'phases': [],
          'scope': 'Repeat three affected Ziling capture modes with real timed foliage settle. Previous full-run tests and images retained; no runtime, camera, source or lighting edits.'}

def save():
    (review / 'ziling-timed-repeat.json').write_text(json.dumps(report, indent=2) + '\n')

try:
    save()
    for mode, flags, count in [('normal', [], 13), ('touch', ['--touch'], 12), ('density', ['--density'], 10)]:
        output = review / 'review-captures' / ('ziling-timed-' + mode)
        assert not output.exists()
        log = review / 'review-logs' / ('ziling-timed-' + mode + '.log')
        command = ['/Applications/Godot.app/Contents/MacOS/Godot', '--path', str(review / 'godot'),
                   '--windowed', '--resolution', '1410x600', '--script', 'res://tests/test_ziling_framing.gd',
                   '--', '--output=' + str(output), *flags]
        phase = {'name': mode, 'status': 'running', 'command': command, 'log': str(log)}
        report['phases'].append(phase)
        print('ZILING_TIMED_REPEAT_START', mode, flush=True)
        with log.open('w') as out:
            child = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT)
            phase['pid'] = child.pid
            save()
            try:
                phase['exit_code'] = child.wait(timeout=160)
            except subprocess.TimeoutExpired:
                child.terminate()
                child.wait(timeout=30)
                phase['exit_code'] = 124
        text = log.read_text(errors='replace')
        okay = phase['exit_code'] == 0 and f'ZILING_FRAMING_RESULT {count} originals; 0 failures' in text
        okay = okay and not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)', text)
        phase.update(status='passed' if okay else 'failed', log_sha256=sha(log))
        save()
        assert okay, (mode, text[-4000:])
        native = load(output / 'report.json')
        assert native['status'] == 'ziling_framing_passed' and not native['errors']
        assert native['source_glb_sha256'] == report['source_glb_sha256'] and native['route_sha256'] == report['runtime_sha256']
        assert native['test_sha256'] == report['test_sha256'] and native['lod_settle_seconds'] == .25
        assert len(native['rows']) == count
        for row in native['rows']:
            p = Path(row['capture'])
            assert sha(p) == row['sha256'] and list(struct.unpack('>II', p.read_bytes()[16:24])) == row['pixels']
            assert row['lod_settle_ms'] >= 250 and row['reed_lod_state']
        phase.update(report_sha256=sha(output / 'report.json'), originals=count)
        save()
        print('ZILING_TIMED_REPEAT_PASS', mode, flush=True)
    assert sha(repo / 'godot/runtime/entry_route.gd') == report['runtime_sha256']
    report.update(status='ziling_timed_repeat_passed_direct_original_review_pending', finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
except BaseException as error:
    report.update(status='failed', error=str(error))
    save()
    raise
