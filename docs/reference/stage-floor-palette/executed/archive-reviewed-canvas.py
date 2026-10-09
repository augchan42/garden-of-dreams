"""Archive executed island evidence after adoption, without repeating binary sources."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import datetime

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette'
review = work / 'lit-native-review'
adoption = work / 'adoption'
archive = repo / 'docs/reference/stage-floor-palette'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
application = load(adoption / 'application.json')
assert application['status'] == 'working_canvas_source_adopted_installed_checks_passed'
assert not archive.exists(), 'Preserve earlier archives rather than overwriting them'
pipeline = load(review / 'review-pipeline.json')
assert pipeline['status'] == 'complete_canvas_technical_review_direct_allroom_and_moving_visual_review_pending'
assert len(pipeline['phases']) == 40
assert sha(repo / 'export/garden-of-dreams.glb') == sha(repo / 'godot/assets/garden-of-dreams.glb') == application['candidate_glb_sha256']
assert sha(repo / 'blender/authoring.blend') == application['authoring_sha256']
assert sha(repo / 'godot/runtime/entry_route.gd') == sha(review / 'godot/runtime/entry_route.gd')
for phase in pipeline['phases'] + application['checks']:
    assert (phase['status'], phase['exit_code']) == (('passed_expected_rejection', 1) if phase['name'] in ['candidate-corrupt-canvas', 'baseline-canvas-palette-red'] else ('passed', 0))
    assert sha(phase['log']) == phase['log_sha256']
installed = {}
for item in load(adoption / 'plan.json')['items']:
    target = repo / item['target']
    if target.is_file():
        assert sha(target) == item['staged']['file']
        installed[item['target']] = sha(target)
    else:
        actual = {str(p.relative_to(target)): sha(p) for p in sorted(target.rglob('*'))
                  if p.is_file() and not p.name.endswith(('.blend1', '.blend2'))}
        assert actual == item['staged']
        installed.update({str(p.relative_to(repo)): sha(p) for p in sorted(target.rglob('*'))
                          if p.is_file() and not p.name.endswith(('.blend1', '.blend2'))})


def copy(path, name):
    destination = archive / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        shutil.copytree(path, destination)
        for p in path.rglob('*'):
            if p.is_file():
                assert sha(p) == sha(destination / p.relative_to(path))
    else:
        shutil.copyfile(path, destination)
        assert sha(path) == sha(destination)


archive.mkdir(parents=True)
for name in ['canvas-red.json', 'canvas-red.log', 'canvas-green.json', 'canvas-green.log',
             'saved-floor-inspection.json', 'ordinary-phase-completion.json', 'palette-contract-before-canvas.json',
             'inspect-saved-floor.py', 'save-canvas-candidate.py', 'test_saved_canvas_palette.py',
             'verify-canvas-export.py', 'prepare-full-lighting.py', 'prepare-lit-review.py',
             'run-lit-review.py', 'review-when-ready.py', 'render-water-edge-lit.gd',
             'run-unbaked-comparison.py', 'prepare-adoption.py', 'archive-reviewed-canvas.py']:
    copy(work / name, 'executed/' + name)
assert sha(work / 'run-lit-review.py') == sha(review / 'executed-review-pipeline.py')
assert sha(work / 'prepare-adoption.py') == sha(adoption / 'executed-adoption.py')
copy(review / 'executed-review-pipeline.py', 'executed/executed-review-pipeline.py')
copy(adoption / 'executed-adoption.py', 'executed/executed-adoption.py')
for name in ['source-preservation.json', 'export-preservation.json', 'lighting-preparation.json',
             'full-lighting-inputs.json']:
    copy(work / 'candidate' / name, 'source/' + name)
for name in ['review-pipeline.json', 'fixture-preparation.json', 'native-import-contract.json',
             'direct-original-visual-review.json', 'texture-memory-normal.json', 'texture-memory-demo.json',
             'review-originals-inventory.json', 'matched-lit-visual-review.json', 'arrivals-visual-review.json',
             'desktop-tour-visual-review.json', 'palette-transfer-normal.json', 'palette-transfer-demo.json']:
    copy(review / name, 'native/' + name)
for name in ['review-logs', 'source-phase-logs', 'review-captures']:
    copy(review / name, 'native/' + name)
for name in ['full-lighting-refresh.json', 'lightmaps-coverage.json', 'lightmap-pixels.json',
             'terminal-spill-pixels.json', 'site-source-audit.json']:
    copy(review / 'export' / name, 'source/' + name)
copy(work / 'saved-source-reproduction/saved-source-verification.json', 'source/saved-source-verification.json')
for item in (work / 'unbaked-native-probe').iterdir():
    if item.is_file() or item.name in ['candidate', 'baseline']:
        copy(item, 'unbaked/' + item.name)
for name in ['application.json', 'plan.json', 'installed-import-contract.json',
             'installed-palette-normal.json', 'installed-palette-demo.json',
             'installed-ziling', 'installed-lit-originals', 'installed-arrivals-desktop', 'installed-arrivals-portrait']:
    copy(adoption / name, 'installed/' + name)
for phase in application['checks']:
    copy(Path(phase['log']), 'installed/logs/' + Path(phase['log']).name)

# Compare installed native originals to the reviewed candidate before describing
# them as a reproduction. Reports retain the actual executed paths and inputs.
for baseline_path, installed_path in [
    (review / 'review-captures/ziling-normal', adoption / 'installed-ziling'),
    (review / 'review-captures/candidate', adoption / 'installed-lit-originals')]:
    original = load(baseline_path / 'report.json')
    current = load(installed_path / 'report.json')
    assert len(original['rows']) == len(current['rows'])
    for a, b in zip(original['rows'], current['rows']):
        assert a['sha256'] == b['sha256']
        assert sha(b['capture']) == b['sha256']
        assert list(struct.unpack('>II', Path(b['capture']).read_bytes()[16:24])) == b['pixels']
# Installed arrivals were also reproduced, using the exact reviewed camera and clock.
assert len(application['installed_arrival_originals_byte_exact']) == 28
for mode in ['desktop', 'portrait']:
    for path in (adoption / ('installed-arrivals-' + mode)).glob('*.png'):
        original = review / 'review-captures' / ('arrivals-' + mode) / path.name
        assert sha(path) == sha(original) == application['installed_arrival_originals_byte_exact'][mode + '/' + path.name]
        assert path.read_bytes()[16:24] == original.read_bytes()[16:24]
readme = """# Neutral stage floor

The saved stage canvas was dark olive green. Its linear base color is now
(0.065, 0.060, 0.055), a muted warm gray. The saved Blender regression first
rejects the original palette and then passes the repair. The five material users,
all 4,467 objects and 47 other materials remain unchanged. Export comparisons
preserve positions, normals, both UV channels and hierarchy across 621 expanded
meshes; fourteen other site GLBs remain byte-exact. The canonical generator uses
the same neutral color. The palette guard adds one canvas record while retaining
all existing checks; actual baseline and corrupted-canvas controls each reject
exactly the intended base-color mismatch.

Six source phases refresh all 141 PNG lightmaps. Forty sequential native review
phases include 38 positive passes and two expected rejection controls. Saved
Blender exports reproduce all sixteen default GLBs exactly. Import retains
42 cameras, 454 colliders and ray checks, 71 markers and 167 render meshes.
Desktop and portrait tours each traverse 26 legs and visit fourteen rooms, with
139 captures each, zero unsupported floor rays and at most four practicals.
The reports retain 17,582 desktop and 17,581 portrait support samples.

All 409 review PNG originals have recorded hashes and dimensions. Fifty-two
original files were directly inspected: twelve matched lit comparisons,
twenty-eight all-room arrivals and six travel/settled frames from each tour.
Direct inspection accepts this palette repair. It does not accept final site art.
Fifteen installed checks pass; all 47 installed lit, Ziling and arrival originals
match the reviewed candidate bytes. The canonical files remain at their normal
paths, identified by the accompanying installed-file hashes. This archive retains
executed helpers, reports, logs and original captures rather than duplicating all
binary sources. Unbaked observations are qualified separately.

Desktop renderer allocations are 52,517,225 bytes in normal mode and 43,468,745
bytes in demo mode. These measurements are not physical-phone performance.
Red-court and imperial portrait composition, Hengwu arrival composition,
ground/water boundaries, foliage, signage and final fourteen-site art remain open.
Five reference slots, current phones/2020 Adreno and sustained budgets, release
and authenticated services remain required. Reference collection stays 37/42.
Records PR14 and the shared-backend proposal retain their separate approval gates.
"""
(archive / 'README.md').write_text(readme)
archive_hashes = {str(p.relative_to(archive)): sha(p) for p in sorted(archive.rglob('*')) if p.is_file()}
evidence = {'status': 'canvas_palette_source_review_and_installed_reproduction_verified',
            'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_glb_sha256': application['candidate_glb_sha256'],
            'authoring_sha256': application['authoring_sha256'],
            'runtime_sha256': sha(repo / 'godot/runtime/entry_route.gd'),
            'source_phases': 6, 'native_review_phases': 40, 'positive_review_phases': 38, 'expected_rejection_controls': 2,
            'directly_inspected_originals': 52, 'review_png_originals': 409, 'installed_originals_byte_exact': 47,
            'installed_checks': len(application['checks']),
            'archive_file_sha256': archive_hashes, 'installed_file_sha256': installed,
            'scope': 'Focused neutral stage-canvas repair; final fourteen-site art, missing references, phone/sustained/release and authenticated services remain open.'}
output = repo / 'export/stage-floor-palette-evidence.json'
assert not output.exists()
output.write_text(json.dumps(evidence, indent=2) + '\n')
for name, digest in archive_hashes.items():
    assert sha(archive / name) == digest
for name, digest in installed.items():
    assert sha(repo / name) == digest
print('CANVAS_REVIEW_ARCHIVE_VERIFIED', len(archive_hashes), 'archive files;', len(installed), 'installed files')
