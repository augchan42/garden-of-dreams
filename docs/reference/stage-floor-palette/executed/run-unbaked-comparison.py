"""Render a sequential native palette comparison without stale source lighting."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import struct

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette'
source = work / 'candidate'
probe = work / 'unbaked-native-probe'
game = probe / 'godot'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
preservation = load(source / 'export-preservation.json')
assert preservation['status'] == 'canvas_palette_export_preservation_passed'
assert load(work / 'canvas-green.json')['status'] == 'saved_canvas_palette_passed'
assert sha(repo / 'export/garden-of-dreams.glb') == preservation['baseline_glb_sha256']
assert sha(source / 'export/garden-of-dreams.glb') == preservation['candidate_glb_sha256']
assert not probe.exists()
probe.mkdir()
shutil.copytree(repo / 'godot', game, ignore=shutil.ignore_patterns('.godot', 'lightmaps', 'acceptance-captures', 'captures'))
(game / 'lightmaps').mkdir()
script = probe / 'render-unbaked-floor.gd'
shutil.copyfile(repo / '.superpowers/sdd/2026-09-23-garden-completion/island-face-source/native-probe/render-water-edge.gd', script)
report = {'status': 'running', 'pid': os.getpid(),
          'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'baseline_glb_sha256': preservation['baseline_glb_sha256'],
          'candidate_glb_sha256': preservation['candidate_glb_sha256'],
          'runtime_sha256': sha(repo / 'godot/runtime/entry_route.gd'),
          'script_sha256': sha(script), 'phases': [],
          'scope': 'Identical existing renderer/runtime/cameras, lightmaps disabled, surface clocks10, six originals per source. Both sources retain54bank assertions/rays. This is a palette proposal diagnostic, not fresh-baked, full-site, phone or production acceptance.'}


def save():
    (probe / 'pipeline.json').write_text(json.dumps(report, indent=2) + '\n')


def run(name, command, marker):
    log = probe / (name + '.log')
    phase = {'name': name, 'command': command, 'status': 'running', 'log': str(log)}
    report['phases'].append(phase)
    save()
    print('CANVAS_NATIVE_START', name, flush=True)
    with log.open('w') as out:
        child = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT)
        phase['pid'] = child.pid
        save()
        try:
            phase['exit_code'] = child.wait(timeout=180)
        except subprocess.TimeoutExpired:
            child.terminate()
            child.wait(timeout=30)
            phase['exit_code'] = 124
    text = log.read_text(errors='replace')
    okay = phase['exit_code'] == 0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)', text)
    phase.update(status='passed' if okay else 'failed', log_sha256=sha(log))
    save()
    assert okay, (name, text[-3000:])
    print('CANVAS_NATIVE_PASS', name, flush=True)


try:
    save()
    shutil.copyfile(__file__, probe / 'executed-pipeline.py')
    godot = '/Applications/Godot.app/Contents/MacOS/Godot'
    for mode, path, digest in [('baseline', repo / 'export/garden-of-dreams.glb', report['baseline_glb_sha256']),
                               ('candidate', source / 'export/garden-of-dreams.glb', report['candidate_glb_sha256'])]:
        shutil.copyfile(path, game / 'assets/garden-of-dreams.glb')
        (game / 'assets/garden-source.json').write_text(json.dumps({'source_glb_sha256': digest}, indent=2) + '\n')
        run(mode + '-import', [godot, '--headless', '--path', str(game), '--editor', '--import'], 'Godot Engine')
        run(mode + '-originals', [godot, '--path', str(game), '--windowed', '--resolution', '1410x600',
                                 '--script', str(script), '--', '--output=' + str(probe / mode), '--candidate'],
            'WATER_EDGE_COMPARISON_RESULT 6 originals; 0 failures')
        images = load(probe / mode / 'report.json')
        assert not images['errors'] and len(images['rows']) == 6
        assert images['source_sha256'] == digest and images['runtime_sha256'] == report['runtime_sha256']
        assert len(images['bank_top_ray_hits']) == 54
        for row in images['rows']:
            image = Path(row['capture'])
            assert sha(image) == row['sha256']
            assert list(struct.unpack('>II', image.read_bytes()[16:24])) == row['pixels']
            assert not row['site_bakes_enabled'] and not row['camera_transition_running']
    assert sha(repo / 'export/garden-of-dreams.glb') == report['baseline_glb_sha256']
    assert sha(repo / 'godot/runtime/entry_route.gd') == report['runtime_sha256']
    report.update(status='unbaked_canvas_native_comparison_complete_direct_review_pending',
                  finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('CANVAS_NATIVE_COMPARISON_COMPLETE', flush=True)
except BaseException as error:
    report.update(status='failed', error=str(error))
    save()
    raise
