from pathlib import Path
import hashlib
import json
import shutil
import struct

root = Path('/Users/auchan/projects/garden-of-dreams')
ledger = root / '.superpowers/sdd/2026-09-23-garden-completion'
archive = root / 'docs/reference/hengwu-detail-framing'
assert not archive.exists(), 'Archive must be new; historical evidence is immutable'
archive.mkdir()
files, locations, pngs = {}, {}, []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def copy(source, relative):
    target = archive / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    digest = sha(source)
    assert sha(target) == digest
    name = str(target.relative_to(root))
    files[name] = digest
    locations[str(source)] = name
    if target.suffix == '.png':
        data = target.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        width, height = struct.unpack('>II', data[16:24])
        pngs.append({'path': name, 'sha256': digest, 'pixels': [width, height]})

for folder, prefix in [('hengwu-detail-framing-comparison', 'comparison'), ('hengwu-detail-runtime', 'runtime')]:
    for source in sorted((ledger / folder).rglob('*')):
        if source.is_file():
            copy(source, Path(prefix) / source.relative_to(ledger / folder))

for source in [Path('/tmp/garden_prepare_hengwu_framing.py'), Path('/tmp/garden_compare_hengwu_detail_framing.gd'), Path('/tmp/garden_diagnose_hengwu_detail.gd'), Path('/tmp/garden_review_hengwu_details.py'), Path(__file__)]:
    copy(source, Path('helpers') / source.name)

for relative in ['godot/runtime/entry_route.gd', 'godot/runtime/entry_route.tscn', 'godot/tests/test_hengwu_detail_framing.gd', 'godot/tests/source-contract.json', 'godot/tests/test_import_source_contract.gd', 'godot/tests/test_courtyard_route.gd', 'godot/tests/test_farmhouse_route.gd', 'godot/tests/test_mobile_ui_scaling.gd', 'godot/tests/test_gate_reveal.gd', 'godot/tests/test_first_reading_demo.gd', 'godot/tests/test_pond_view.gd', 'godot/tests/test_portrait_architecture.gd', 'godot/tests/test_oux_portrait_framing.gd']:
    copy(root / relative, Path('installed-code') / relative)

work = ledger / 'hengwu-detail-runtime'
focused = json.loads((work / 'accepted-focused-pipeline.json').read_text())
regressions = json.loads((work / 'regression-pipeline.json').read_text())
assert focused['status'] == regressions['status'] == 'passed'
assert focused['route_sha256'] == regressions['route_sha256'] == sha(root / 'godot/runtime/entry_route.gd')
assert focused['test_sha256'] == sha(root / 'godot/tests/test_hengwu_detail_framing.gd')
assert len(focused['phases']) == 3 and len(regressions['phases']) == 10
for phase in focused['phases'] + regressions['phases']:
    assert phase['exit_code'] == 0 and sha(Path(phase['log'])) == phase['log_sha256']

for mode in ['normal', 'touch', 'density']:
    report = json.loads((work / ('accepted-' + mode) / 'report.json').read_text())
    assert not report['errors'] and len(report['rows']) == 10
    for row in report['rows']:
        original = Path(row['capture'])
        assert sha(original) == row['sha256']
        assert list(struct.unpack('>II', original.read_bytes()[16:24])) == row['pixels']

preservation = json.loads((work / 'source-preservation.json').read_text())
for relative, digest in preservation['source']['lighting_pngs'].items():
    assert sha(root / relative) == digest
assert sha(root / 'godot/assets/garden-of-dreams.glb') == focused['source_glb_sha256']

readme = '''# Hengwu portrait detail actions

Inspect the rocks and Examine the book now keep the nearest pierced stone and the complete book/tabletop above the portrait controls. Resizing preserves the selected action and text; rotation restores the original desktop transform and projection. Look restores the courtyard overview and clears the detail selection. Hengwu's portrait action list scrolls within 128 logical units, preserving 48-unit touch targets and access to its last action.

The actual public-action baseline failed eight assertions: six subject-fit failures and two Look failures. The first touch variant failed two narrower-viewport fits; the first density variant failed two stone/header-clearance checks. All are preserved with original captures, reports, commands and executed code. One later native command timed out before any capture; the reason was not established. A subsequent diagnostic found its root visible and completed normally. The final test explicitly shows its native window and has a deadline.

Three final graphical modes pass with thirty original PNGs: normal, touch-size and desktop density-scaled. Ten adjacent regressions also pass: import/source agreement, courtyard, farmhouse, mobile UI, gate reveal, first reading, pond view, portrait architecture and Ouxiang framing. Fifteen portrait-architecture and three Ouxiang originals are retained. All evidence paths are mapped to exact copied bytes; PNG dimensions come from their original headers.

The earlier four camera comparisons retain all fifty-six originals, including wall-occluded proposals. A collider ray alone did not establish rendered visibility. The accepted camera stays inside the courtyard. Final visual review inspected eight original stone/book frames across normal, narrow touch and both density viewports: all three nearest-stone holes and its base are visible, and the book/tabletop clears the panel.

Source geometry and matching lighting remain unchanged: GLB 26033c99 and authoring 19eb386d. All 282 source/engine lighting PNG hashes were rechecked. The two full fourteen-room walks in the preceding source-adoption archive used the previous runtime; they are not new walks of this camera update.

The desktop density request was clamped by its host window: actual portrait PNGs are 1080×1978 and 944×1978. These tests do not establish physical-phone, sustained, 2020 Adreno or final all-site art acceptance. Hengwu's arrival wall cap, roof crop and facade lighting remain open. Five reference slots, other site art, release and authenticated services remain required. The full goal stays active.
'''
(archive / 'README.md').write_text(readme)
files[str((archive / 'README.md').relative_to(root))] = sha(archive / 'README.md')
index = {'status': 'installed_camera_actions_and_adjacent_regressions_passed', 'scope': 'Portrait stone/book actions, rotation/resize/Look behavior and touch scroll reachability; original failures and camera comparisons retained. No geometry/light change, physical-device acceptance or final all-site art claim.', 'source_glb_sha256': focused['source_glb_sha256'], 'route_sha256': focused['route_sha256'], 'test_sha256': focused['test_sha256'], 'final_focused_modes': 3, 'adjacent_regressions': 10, 'original_png_count': len(pngs), 'checked_file_count': len(files), 'files': files, 'artifact_locations': locations, 'original_pngs': pngs}
(root / 'export/hengwu-detail-framing-evidence.json').write_text(json.dumps(index, indent=2) + '\n')
print(json.dumps({'files': len(files), 'original_pngs': len(pngs), 'route': focused['route_sha256']}))
