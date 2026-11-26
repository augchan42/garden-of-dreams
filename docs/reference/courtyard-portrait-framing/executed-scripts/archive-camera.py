from pathlib import Path
import json, hashlib, shutil, datetime

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = Path(__file__).resolve().parent
archive = repo / 'docs/reference/courtyard-portrait-framing'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
adoption = json.loads((work / 'installed-v3/adoption.json').read_text())
assert adoption['status'] == 'installed_checks_and98_original_reproductions_passed'
assert len(adoption['phases']) == 11 and all(r['status'] == 'passed' and r['exit_code'] == 0 for r in adoption['phases'])
assert not archive.exists()
archive.mkdir()
directories = ['final-v2', 'final-v3', 'final-native', 'installed-v1', 'installed-v2', 'installed-v3',
               'baseline-normal', 'baseline-positioned', 'state-only',
               'posed-normal', 'posed-touch', 'posed-density',
               'imperial-baseline-corrected', 'combined-architecture-normal']
for name in directories:
    shutil.copytree(work / name, archive / name)
scripts = archive / 'executed-scripts'
scripts.mkdir()
for path in sorted(work.iterdir()):
    if path.is_file() and path.suffix in ['.json', '.py', '.gd', '.log'] and path.name != 'continuation-checkpoint.json':
        shutil.copy2(path, scripts / path.name)
for name in adoption['targets']:
    dst = archive / 'executed-project' / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / 'godot' / name, dst)
readme = '''# Courtyard and imperial portrait cameras — 2026-10-10

The courtyard facade, paired doors and primary banana plant now fit above portrait controls. Look restores the overview. Selecting a detail and rotating preserves its text and visitor position; returning to desktop restores the original desktop pose. The final touch action remains accessible through the action scrollbar. The imperial portrait overview occupies more of the available scene, retaining the roof tiers, closed doors, moon and amber windows. Its selected doors survive rotation and restore the desktop aspect mode.

Source `c9d4fb30`, authoring `43d7e33e` and all141 lighting PNGs remain unchanged. Runtime is `7970380d`. This change installs four code/contract files and one new test UID. No travel path, geometry, material, bake or product shader changes are included.

The positioned courtyard baseline produces20 failures; the corrected imperial baseline produces6. The state-only courtyard attempt retains12 clipping failures. Historical captures before final-v2 have an unfrozen animation clock and are not byte-exact reproduction evidence. The first imperial test parse failure, rejected narrow-screen pose and first combined touch-ceiling failure remain archived. The first installed attempt restored all five targets when the sandbox blocked Godot's editor-settings save, even though the import process exited0. The second attempt passed all eleven installed assertions but restored the files when one nunnery capture differed: the short frame wait ended before the real0.2-second FloraLOD update. The test now waits0.25 seconds after a completed camera tween; the actual runtime LOD policy remains enabled. Three affected modes were repeated. The third installed attempt passed and reproduced all98 originals without filtering errors or relaxing camera limits.

All32 full candidate phases pass, with three affected architecture modes repeated after the foliage wait correction. Checks include source/import contracts, normal/demo lighting and texture allocations, neighboring views, all arrivals, entry/demo behavior and actual public-command tours. Each desktop/portrait tour visits14 rooms over26 legs and captures139 original images, with no unsupported floor samples and at most four practicals. Tour shaders retain their normal clocks; only stationary camera/arrival comparisons freeze clock3. Actual Mac normal/demo renderer allocation is52517225/43468745 bytes; this is not phone or sustained performance acceptance.

The full run has452 native PNGs with hashes and dimensions in `final-v2/capture-inventory.json`; the three repeated architecture modes add25 originals in `final-v3/capture-inventory.json`. The final comparison set uses the427 unchanged full-run originals and25 repeated architecture originals. The original25 file paths directly inspected are listed in `final-v2/visual-review.json`; repeat inspection and exact reuse are recorded in `final-v3/visual-review.json`; the other files are inventoried without claiming direct inspection. Twenty-six of28 arrival images reproduce previously inspected PR17 originals exactly; the two changed portraits were directly inspected. Eleven installed checks pass and all98 installed courtyard/architecture/arrival originals reproduce the reviewed candidate exactly.

The evidence index at `export/courtyard-portrait-framing-evidence.json` records archive and installed-file hashes. Absolute scratch paths inside native reports are retained as executed provenance; the matching files are under the same archived phase directory.

This closes the measured two-room portrait camera defects. Hengwu composition, stage seams, ground/water closure, dark surface shading, foliage, signage and final14-site art remain open. External references remain37/42. Current phones,2020 Adreno and sustained budgets, release and authenticated reading/history/AI/presence/social remain required. The full Garden goal remains active. The user’s open editors were not reloaded or closed.
'''
(archive / 'README.md').write_text(readme)
prior = json.loads((repo / 'export/stage-floor-palette-evidence.json').read_text())
installed = {}
changed = {'godot/' + n for n in adoption['targets']}
for name, digest in prior['installed_file_sha256'].items():
    actual = sha(repo / name)
    assert name in changed or actual == digest, ('Unexpected canonical source change', name)
    installed[name] = actual
for name, row in adoption['targets'].items():
    actual = sha(repo / 'godot' / name)
    assert actual == row['after_sha256']
    installed['godot/' + name] = actual
files = {str(p.relative_to(repo)): sha(p) for p in sorted(archive.rglob('*')) if p.is_file()}
evidence = {'status': 'two_room_camera_checks_and_installed_reproduction_passed',
            'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_glb_sha256': adoption['source_glb_sha256'],
            'authoring_sha256': sha(repo / 'blender/authoring.blend'),
            'runtime_sha256': adoption['runtime_sha256'],
            'candidate_positive_phases': 32, 'affected_architecture_rechecks': 3, 'installed_checks': 11,
            'full_run_native_pngs': 452, 'repeated_architecture_pngs': 25, 'final_comparison_pngs': 452,
            'initial_direct_original_file_paths': 25,
            'installed_originals_byte_exact': 98, 'unchanged_arrival_originals': 26,
            'baseline_failures': {'positioned_courtyard': 20, 'imperial': 6},
            'archive_file_sha256': files, 'installed_file_sha256': installed,
            'scope': 'Measured two-room camera acceptance. Historical failed/unfrozen attempts preserved. Final14-site art, references, current phones/sustained performance, release and authenticated services remain open.'}
(repo / 'export/courtyard-portrait-framing-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
paragraph = '''\n\n## Courtyard and imperial portrait cameras — 2026-10-10

Runtime `7970380d` fits the courtyard facade, doors and primary banana plant above portrait controls, restores the overview through Look and preserves selected details through rotation. Original desktop poses return correctly; touch actions remain scrollable. The imperial portrait overview gives the facade more usable height while retaining the roof tiers, moon and closed doors. Source `c9d4fb30`, authoring `43d7e33e`, geometry and all141 lighting PNGs remain unchanged.

Positioned courtyard RED20 and imperial RED6 precede32 passing full native checks and three repeated architecture modes after a test-only foliage wait correction. Both actual Mac tours visit14 rooms over26 legs with zero unsupported floor samples and at most four practicals. The452 full-run originals and25 repeated architecture originals are hashed and dimension-checked;25 full-run original file paths and the repeated nunnery original were directly inspected. Twenty-four repeated architecture images reproduce their full-run counterparts exactly. Eleven installed checks pass, and all98 installed camera/arrival images reproduce the reviewed candidate exactly. Evidence: [camera checks and original images]({link}).

This is two-room camera acceptance. Hengwu composition, stage seams, dark shading, ground/water closure, foliage, signage and final14-site art remain open. Reference coverage remains37/42; current phones,2020 Adreno/sustained budgets, release and authenticated services remain required. The full goal remains active.
'''
documents = {'docs/build-status.md': 'reference/courtyard-portrait-framing/README.md',
             'docs/scene-art-review.md': 'reference/courtyard-portrait-framing/README.md',
             'docs/sites/README.md': '../reference/courtyard-portrait-framing/README.md',
             'docs/sites/yihong-yuan.md': '../reference/courtyard-portrait-framing/README.md',
             'docs/sites/daguan-lou.md': '../reference/courtyard-portrait-framing/README.md',
             'docs/superpowers/plans/2026-09-23-garden-completion.md': '../../reference/courtyard-portrait-framing/README.md',
             '.superpowers/sdd/2026-09-23-garden-completion/progress.md': '../../../docs/reference/courtyard-portrait-framing/README.md'}
for name, link in documents.items():
    path = repo / name
    path.write_text(path.read_text() + paragraph.format(link=link))
checkpoint = json.loads((work / 'continuation-checkpoint.json').read_text())
checkpoint.update(status='installed11_checks98_reproductions_passed_archive_ready',
                  production_runtime_sha256=adoption['runtime_sha256'],
                  archive=str(archive.relative_to(repo)),
                  next='Refresh reference coverage; Git stage/commit; skill-required independent GPT-6.1 Sol review; authorized push/PR/merge. Fullgoal active.')
(work / 'continuation-checkpoint.json').write_text(json.dumps(checkpoint, indent=2) + '\n')
print('CAMERA_ARCHIVED', len(files), 'INSTALLED_HASHES', len(installed), flush=True)
