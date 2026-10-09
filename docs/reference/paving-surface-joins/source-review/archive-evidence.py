"""Archive executed evidence only after the reversible native installation passes."""
from pathlib import Path
import hashlib
import json
import shutil
import struct

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = Path(__file__).parent
source = Path('/tmp/garden-paving-joins-20261010-v4')
review = Path('/tmp/garden-paving-review-20261010-v4')
adoption = work / 'adoption-second'
archive = repo / 'docs/reference/paving-surface-joins'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
application = load(adoption / 'application.json')
assert application['status'] == 'working_paving_source_adopted_installed_checks_passed'
assert len(application['checks']) == 22 and all(p['status'] == 'passed' for p in application['checks'])
assert not archive.exists(), 'Preserve earlier archive'

def copy(p, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if p.is_dir():
        shutil.copytree(p, target)
    else:
        shutil.copyfile(p, target)

for p in sorted(work.iterdir()):
    if p.is_file() and p.suffix in ('.json', '.log', '.py', '.gd', '.md'):
        copy(p, archive / 'source-review' / p.name)
for p in sorted(source.iterdir()):
    if p.is_file() and p.suffix in ('.json', '.log', '.py'):
        copy(p, archive / 'source' / p.name)
for name in ['source-preservation.json', 'export/manifest.json', 'export/candidate-libraries.json',
             'export/full-lighting-refresh.json', 'export/lightmaps-coverage.json', 'export/lightmap-pixels.json',
             'export/terminal-spill-pixels.json', 'export/site-source-audit.json']:
    p = source / name
    if p.exists():copy(p, archive / 'source' / name)
copy(source / 'lighting-preparation-logs', archive / 'source/lighting-preparation-logs')
bake = load(source / 'export/full-lighting-refresh.json')
for phase in bake['phases']:
    copy(Path(phase['log']), archive / 'source/bake-logs' / (phase['name'] + '.log'))
for p in sorted(review.iterdir()):
    if p.is_file() and p.suffix in ('.json', '.log', '.py', '.gd'):
        copy(p, archive / 'native-review' / p.name)
for name in ['review-logs', 'review-captures']:
    copy(review / name, archive / 'native-review' / name)
for p in sorted((review / 'godot/tests').iterdir()):
    if p.is_file() and p.suffix in ('.gd', '.json'):
        copy(p, archive / 'native-review/executed-tests' / p.name)
for p in sorted(adoption.iterdir()):
    if p.name not in ['stage', 'backup']:
        copy(p, archive / 'installed' / p.name)
for p in sorted((work / 'adoption').iterdir()):
    if p.name not in ['stage', 'backup']:
        copy(p, archive / 'failed-installed-report-schema' / p.name)
reproduction = Path('/tmp/garden-paving-review-20261010-v4-default-reproduction')
for p in sorted(reproduction.iterdir()):
    if p.is_file() and p.suffix in ('.json', '.log'):
        copy(p, archive / 'default-reproduction' / p.name)
canonical = {}
for item in load(adoption / 'plan.json')['items']:
    target = repo / item['target']
    paths = sorted(target.rglob('*')) if target.is_dir() else [target]
    for p in paths:
        if p.is_file() and not p.name.endswith(('.blend1', '.blend2')):
            canonical[str(p.relative_to(repo))] = sha(p)
for name in ['blender/authoring.blend', 'blender/master.blend', 'export/garden-of-dreams.glb',
             'godot/assets/garden-of-dreams.glb', 'godot/runtime/entry_route.gd',
             'scripts/audit_paving_footprint.py', 'scripts/paving_surface_partition.py',
             'scripts/prepare_paving_surface_candidate.py', 'scripts/test_saved_paving_surfaces.py',
             'scripts/verify_saved_garden_candidate.py', 'godot/tests/test_paving_surface_transfer.gd',
             'godot/tests/test_ziling_framing.gd']:
    canonical[name] = sha(repo / name)
for name in ['blender/sites', 'export/sites', 'export/lightmaps', 'godot/lightmaps']:
    for p in sorted((repo / name).rglob('*')):
        if p.is_file() and not p.name.endswith(('.blend1', '.blend2')):
            canonical[str(p.relative_to(repo))] = sha(p)
images = {}
for p in sorted(archive.rglob('*.png')):
    images[str(p.relative_to(archive))] = {'sha256': sha(p), 'pixels': list(struct.unpack('>II', p.read_bytes()[16:24]))}
(archive / 'capture-inventory.json').write_text(json.dumps({'count': len(images), 'files': images,
    'scope': 'Raw review, failed attempts and installed originals. Only files named by direct review manifests are claimed directly inspected.'}, indent=2) + '\n')
index = {'status': 'paving_source_and_matching_lighting_installed', 'scope': application.get('scope', 'Focused paving repair; full Garden goal remains open'),
         'candidate_glb_sha256': application['candidate_glb_sha256'], 'authoring_sha256': application['authoring_sha256'],
         'runtime_sha256': canonical['godot/runtime/entry_route.gd'], 'installed_checks': 22,
         'installed_arrivals_byte_exact': application['installed_arrival_originals_byte_exact'],
         'installed_focused_byte_exact': application['installed_focused_originals_byte_exact'],
         'canonical_files_sha256': canonical, 'archive_files_sha256': {}, 'archive_capture_count': len(images)}
for p in sorted(archive.rglob('*')):
    if p.is_file():index['archive_files_sha256'][str(p.relative_to(repo))] = sha(p)
(repo / 'export/paving-surface-joins-evidence.json').write_text(json.dumps(index, indent=2) + '\n')
print('PAVING_EVIDENCE_ARCHIVED', len(index['archive_files_sha256']), 'files;', len(images), 'originals;', len(canonical), 'canonical hashes')
