"""Continue after a runner marker mismatch; retain the original failed report."""
from pathlib import Path
import datetime, hashlib, json, os, re, struct, subprocess, sys

w = Path(__file__).resolve().parent
r = w.parents[3]
s = w / 'closed-leaf-candidate'
root = w / 'lit-native-review'
g = root / 'godot'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
prior = load(root / 'review-pipeline.json')
assert prior['status'] == 'failed'
assert prior['phases'][-1]['name'] == 'ziling-normal'
assert prior['phases'][-1]['exit_code'] == 0
for pid in [prior['orchestrator_pid'], prior['phases'][-1]['pid']]:
    try:
        os.kill(pid, 0)
        raise RuntimeError('Existing review process still present')
    except ProcessLookupError:
        pass
expected = prior['source_glb_sha256']
author = prior['authoring_sha256']
assert sha(s / 'export/garden-of-dreams.glb') == sha(g / 'assets/garden-of-dreams.glb') == expected
assert sha(s / 'blender/authoring.blend') == author
frozen = load(s / 'full-lighting-inputs.json')['files']
for name, digest in frozen.items():
    assert sha(s / name) == digest, name
for name, digest in prior['installed_source_png_sha256'].items():
    assert sha(s / 'export/lightmaps' / name) == sha(g / 'lightmaps' / name) == digest, name
reused = prior['phases'][:-1]
assert len(reused) == 21
for phase in reused:
    assert phase['status'] == 'passed' and phase['exit_code'] == 0
    assert sha(phase['log']) == phase['log_sha256']
normal = prior['phases'][-1]
text = Path(normal['log']).read_text()
assert sha(normal['log']) == normal['log_sha256']
assert 'ZILING_FRAMING_RESULT 13 originals; 0 failures' in text
assert not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)', text)
normal_root = root / 'review-captures/ziling-normal'
normal_report = load(normal_root / 'report.json')
assert normal_report['status'] == 'ziling_framing_passed'
assert not normal_report['errors'] and len(normal_report['rows']) == 13
assert normal_report['source_glb_sha256'] == expected
assert normal_report['route_sha256'] == sha(g / 'runtime/entry_route.gd')
assert normal_report['test_sha256'] == sha(g / 'tests/test_ziling_framing.gd')
for row in normal_report['rows']:
    p = Path(row['capture'])
    assert sha(p) == row['sha256']
    assert list(struct.unpack('>II', p.read_bytes()[16:24])) == row['pixels']
qualified = dict(normal)
qualified.update(status='passed', qualification='Native exit0, actual ZILING_FRAMING_RESULT13/0 and all13 hashed original captures verified. Original runner failed solely on nonexistent WATER_EDGE_FRAMING_RESULT; original failed report remains unchanged.',
                 original_runner_status='failed', report_sha256=sha(normal_root / 'report.json'))
reused = reused + [qualified]
logroot = root / 'review-logs-resume1'
cap = root / 'review-captures-resume1'
assert not logroot.exists() and not cap.exists()
logroot.mkdir(); cap.mkdir()
report = {'status': 'native_review_running', 'source_glb_sha256': expected,
          'authoring_sha256': author, 'orchestrator_pid': os.getpid(),
          'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'prior_failed_report_sha256': sha(root / 'review-pipeline.json'),
          'reused_checked_phases': reused, 'phases': [],
          'installed_source_png_sha256': prior['installed_source_png_sha256'],
          'scope': 'Sequential continuation of remaining native review. Actual Ziling13/0 completion retained and qualified; test/source/runtime/assertions/timeouts unchanged. Direct original visual review, adoption and final art/device/service acceptance remain pending.'}
def save():
    (root / 'review-pipeline-resume1.json').write_text(json.dumps(report, indent=2) + '\n')
def run(name, cmd, marker, timeout=160):
    assert sha(s / 'export/garden-of-dreams.glb') == expected
    assert sha(s / 'blender/authoring.blend') == author
    log = logroot / (name + '.log')
    phase = {'name': name, 'status': 'running', 'command': cmd, 'log': str(log)}
    report['phases'].append(phase); save()
    print('WATER_EDGE_REVIEW_START', name, flush=True)
    with log.open('w') as out:
        proc = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT)
        phase['pid'] = proc.pid; save()
        try:
            phase['exit_code'] = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.terminate(); proc.wait(); phase['exit_code'] = 124
    text = log.read_text(errors='replace')
    okay = phase['exit_code'] == 0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)', text)
    phase.update(log_sha256=sha(log), status='passed' if okay else 'failed'); save()
    if not okay:
        raise RuntimeError((name, phase['exit_code'], text[-4000:]))
    print('WATER_EDGE_REVIEW_PASS', name, flush=True)
try:
    save()
    native = ['/Applications/Godot.app/Contents/MacOS/Godot', '--path', str(g), '--windowed', '--resolution', '1410x600']
    for mode, args, count in [('touch', ['--touch'], 12), ('density', ['--density'], 10)]:
        output = cap / ('ziling-' + mode)
        run('ziling-' + mode, native + ['--script', 'res://tests/test_ziling_framing.gd', '--', '--output=' + str(output)] + args, 'ZILING_FRAMING_RESULT')
        d = load(output / 'report.json')
        assert len(d['rows']) == count and not d['errors']
        for row in d['rows']:
            p = Path(row['capture'])
            assert sha(p) == row['sha256'] and list(struct.unpack('>II', p.read_bytes()[16:24])) == row['pixels']
    for label, script, marker in [('ouxiang', 'test_oux_portrait_framing.gd', 'OUXIANG_FRAMING_PASS'), ('architecture', 'test_portrait_architecture.gd', 'PORTRAIT_ARCHITECTURE_RESULT'), ('hengwu', 'test_hengwu_detail_framing.gd', 'HENGWU_DETAIL_FRAMING_RESULT'), ('tubi', 'test_tubi_framing.gd', 'TUBI_FRAMING_RESULT'), ('qiushuang', 'test_qiushuang_framing.gd', 'QIUSHUANG_FRAMING_RESULT'), ('pond', 'test_pond_view.gd', 'POND_VIEW_PASS')]:
        run('adjacent-' + label, native + ['--script', 'res://tests/' + script, '--', '--output=' + str(cap / label)], marker)
    for mode, args in [('normal', []), ('demo', ['--demo'])]:
        run('texture-memory-' + mode, native + ['--script', 'res://tests/audit_runtime_textures.gd', '--', '--output=' + str(root / ('texture-memory-' + mode + '.json'))] + args, 'RUNTIME_TEXTURE_INVENTORY_PASS')
    for mode, args in [('desktop', []), ('portrait', ['--mobile'])]:
        output = cap / ('arrivals-' + mode)
        run('arrivals-' + mode, native + ['--script', 'res://tests/render_entry_route.gd', '--', '--views-only', '--fixed-clock', '--output-directory=' + str(output)] + args, 'ROUTE_RENDER_SAVED')
        d = load(output / ('route-' + mode + '-report.json'))
        assert d['source_glb_sha256'] == expected and len(d['captures']) == 14
    for mode, args in [('desktop', []), ('portrait', ['--portrait'])]:
        output = cap / ('tour-' + mode); output.mkdir()
        run('full-tour-' + mode, native + ['--script', 'res://tests/render_full_garden_traversal.gd', '--', '--capture-directory=' + str(output), '--output=' + str(output / 'report.json')] + args, 'FULL_GARDEN_TRAVERSAL', 900)
        d = load(output / 'report.json')
        assert d['status'] == 'passed' and d['source_glb_sha256'] == expected
    for name, digest in frozen.items():
        assert sha(s / name) == digest, name
    assert sha(g / 'runtime/entry_route.gd') == sha(r / 'godot/runtime/entry_route.gd')
    report.update(status='technical_review_complete_original_lit_visual_review_pending', finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save(); print('WATER_EDGE_FULL_TECHNICAL_REVIEW_COMPLETE', root, flush=True)
except BaseException as error:
    report.update(status='failed', error=str(error)); save(); raise
