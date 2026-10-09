"""Archive executed island evidence after adoption, without repeating binary sources."""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import datetime

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/island-face-source'
review = work / 'lit-native-review'
adoption = work / 'adoption'
archive = repo / 'docs/reference/island-exterior-winding'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
application = load(adoption / 'application.json')
assert application['status'] == 'working_island_source_adopted_installed_checks_passed'
assert not archive.exists(), 'Preserve earlier archives rather than overwriting them'
pipeline = load(review / 'review-pipeline.json')
assert pipeline['status'] == 'focused_technical_review_complete_direct_lit_visual_review_pending'
assert len(pipeline['phases']) == 25
assert sha(repo / 'export/garden-of-dreams.glb') == sha(repo / 'godot/assets/garden-of-dreams.glb') == application['candidate_glb_sha256']
assert sha(repo / 'blender/authoring.blend') == application['authoring_sha256']
assert sha(repo / 'godot/runtime/entry_route.gd') == sha(review / 'godot/runtime/entry_route.gd')
for phase in pipeline['phases'] + application['checks']:
    assert phase['status'] == 'passed' and phase['exit_code'] == 0
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
for name in ['shell-contract-red.json', 'shell-contract-green.json',
             'repair_saved_island.py', 'test_saved_island_shell.py',
             'verify-island-export.py', 'prepare-full-lighting.py', 'prepare-lit-review.py',
             'run-lit-review.py', 'review-when-ready.py', 'render-water-edge-lit.gd',
             'prepare-adoption.py', 'archive-reviewed-island.py']:
    copy(work / name, 'executed/' + name)
for name in ['source-preservation.json', 'export-preservation.json', 'lighting-preparation.json',
             'full-lighting-inputs.json', 'import-subject-accessor-counts.json']:
    copy(work / 'candidate' / name, 'source/' + name)
for name in ['review-pipeline.json', 'fixture-preparation.json', 'native-import-contract.json',
             'direct-original-visual-review.json', 'texture-memory-normal.json']:
    copy(review / name, 'native/' + name)
for name in ['review-logs', 'source-phase-logs', 'review-captures']:
    copy(review / name, 'native/' + name)
for name in ['full-lighting-refresh.json', 'lightmaps-coverage.json', 'lightmap-pixels.json',
             'terminal-spill-pixels.json', 'site-source-audit.json']:
    copy(review / 'export' / name, 'source/' + name)
copy(work / 'saved-source-reproduction/saved-source-verification.json', 'source/saved-source-verification.json')
copy(work / 'native-probe/pipeline.json', 'unbaked/pipeline.json')
copy(work / 'native-probe/direct-original-review.json', 'unbaked/direct-original-review.json')
for name in ['application.json', 'plan.json', 'installed-import-contract.json',
             'installed-palette-normal.json', 'installed-palette-demo.json',
             'installed-ziling', 'installed-lit-originals']:
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
readme = '''# Island exterior winding repair

The saved island had 24 inward-facing exterior quads and inconsistent adjacent
shell winding. The repaired source reverses those quads while retaining all 48
vertices, the 26 face shapes, island heights and plaster material. Source RED and
GREEN reports, exported attribute preservation and unchanged-site comparisons
are retained here. The constructor now generates the same exterior winding.

Six source lighting phases produce matching maps for the repaired complete
export. Twenty-five sequential native checks cover source import, lighting,
saved default exports, site libraries, the supported western route, matched lit
comparisons and public Ziling framing in three modes. The direct visual report
records inspected original images and their limits. Installed checks and native
original reproduction are recorded separately.

Canonical authoring, site libraries, exports and lightmap files remain in their
normal project paths, identified by the accompanying installed-file hashes.
The archive preserves executed helpers, reports, logs and original captures;
it does not duplicate all unchanged binary assets. Unbaked observations are
qualified separately and do not establish the lit appearance.

Final art across fourteen sites, five references, current physical phones and
2020 Adreno/sustained budgets, release and authenticated services remain open.
Previous PR15 full tours qualify the previous source; this repair has focused
western-route and camera coverage. Desktop memory checks do not establish
phone acceptance. Records PR14 and its security approval remain separate.
'''
(archive / 'README.md').write_text(readme)
archive_hashes = {str(p.relative_to(archive)): sha(p) for p in sorted(archive.rglob('*')) if p.is_file()}
evidence = {'status': 'island_winding_source_review_and_installed_reproduction_verified',
            'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_glb_sha256': application['candidate_glb_sha256'],
            'authoring_sha256': application['authoring_sha256'],
            'runtime_sha256': sha(repo / 'godot/runtime/entry_route.gd'),
            'source_phases': 6, 'native_review_phases': 25,
            'installed_checks': len(application['checks']),
            'archive_file_sha256': archive_hashes, 'installed_file_sha256': installed,
            'scope': 'Focused island exterior winding repair; final fourteen-site art, missing references, phone/sustained/release and authenticated services remain open.'}
output = repo / 'export/island-exterior-winding-evidence.json'
assert not output.exists()
output.write_text(json.dumps(evidence, indent=2) + '\n')
for name, digest in archive_hashes.items():
    assert sha(archive / name) == digest
for name, digest in installed.items():
    assert sha(repo / name) == digest
print('ISLAND_REVIEW_ARCHIVE_VERIFIED', len(archive_hashes), 'archive files;', len(installed), 'installed files')
