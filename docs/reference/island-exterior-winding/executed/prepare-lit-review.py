"""Prepare isolated review files without starting a native application."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/island-face-source'
source = work / 'candidate'
review = work / 'lit-native-review'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline = '7a9fc523bc1517941cc248c040877b86f9cd00a11654c6c31e40f3acc089632f'
candidate = '73267e2b17c52531ad6bc1e9df1279634564e93e3ef04519b2f27ade26ec178e'
assert sha(repo / 'export/garden-of-dreams.glb') == baseline
assert sha(source / 'export/garden-of-dreams.glb') == candidate
assert not review.exists()
review.mkdir()
shutil.copytree(source / 'blender', review / 'blender', ignore=shutil.ignore_patterns('*.blend1', '*.blend2'))
for p in (repo / 'blender/kits').glob('*.blend'):
    if p.name != 'KIT_water.blend':
        shutil.copyfile(p, review / 'blender/kits' / p.name)
shutil.copytree(source / 'scripts', review / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(source / 'export', review / 'export', ignore=shutil.ignore_patterns('lightmaps', 'full-lighting-refresh.json', 'lightmaps-coverage.json', 'lightmap-pixels.json', 'terminal-spill-pixels.json'))
shutil.copytree(repo / 'export/kits', review / 'export/kits', dirs_exist_ok=True)
shutil.copytree(repo / 'textures', review / 'textures')
shutil.copytree(repo / 'docs/sites', review / 'docs/sites')
ignore = shutil.ignore_patterns('.godot', 'lightmaps', 'acceptance-captures', 'captures')
game = review / 'godot'
shutil.copytree(repo / 'godot', game, ignore=ignore)
(game / 'lightmaps').mkdir()
shutil.copyfile(source / 'export/garden-of-dreams.glb', game / 'assets/garden-of-dreams.glb')
(game / 'assets/garden-source.json').write_text(json.dumps({'source_glb_sha256': candidate}, indent=2) + '\n')
subprocess.run([sys.executable, str(review / 'scripts/build_godot_import_contract.py'), '--source', str(source / 'export/garden-of-dreams.glb'), '--output', str(game / 'tests/source-contract.json')], check=True)
before = json.loads((repo / 'godot/tests/source-contract.json').read_text())
after = json.loads((game / 'tests/source-contract.json').read_text())
assert before['source_glb_sha256'] == baseline and after['source_glb_sha256'] == candidate
for key in ['cameras', 'colliders', 'markers', 'render_meshes']:
    assert before[key] == after[key], key
assert [len(after[k]) for k in ['cameras', 'colliders', 'markers']] == [42, 454, 71]
assert after['render_meshes'] == 167
p = game / 'tests/test_ziling_framing.gd'
assert p.read_text().count(baseline) == 1
p.write_text(p.read_text().replace(baseline, candidate))
guard = {'baseline_sha256': sha(repo / 'godot/tests/test_ziling_framing.gd'), 'candidate_sha256': sha(p), 'change': 'source digest only; all shape, framing, deadline and public-action assertions retained'}
script = work / 'render-water-edge-lit.gd'
shutil.copyfile(repo / '.superpowers/sdd/2026-09-23-garden-completion/water-edge-source/garden_compare_water_edge_lit.gd', script)
# --candidate means 54 bank colliders in this existing helper. Both fixtures
# already contain those banks; both modes must retain that assertion.
base_game = review / 'baseline-godot'
shutil.copytree(repo / 'godot', base_game, ignore=shutil.ignore_patterns('.godot', 'acceptance-captures', 'captures'))
assert sha(game / 'runtime/entry_route.gd') == sha(base_game / 'runtime/entry_route.gd') == sha(repo / 'godot/runtime/entry_route.gd')
assert not (game / '.godot').exists() and not (base_game / '.godot').exists()
assert not list((game / 'lightmaps').iterdir())
record = {'status': 'static_lit_fixture_prepared_no_native_worker_started', 'source_root': str(source), 'review_root': str(review), 'baseline_glb_sha256': baseline, 'candidate_glb_sha256': candidate, 'authoring_sha256': sha(source / 'blender/authoring.blend'), 'runtime_sha256': sha(game / 'runtime/entry_route.gd'), 'source_contract_sha256': sha(game / 'tests/source-contract.json'), 'ziling_source_guard': guard, 'comparison_script_sha256': sha(script), 'counts': {'cameras': 42, 'colliders': 454, 'markers': 71, 'render_meshes': 167}, 'scope': 'Both fixed-camera comparison modes retain54bank assertions. Candidate starts with no maps; full fresh source lighting must finish and all native parents exit before review. Baseline is current main with its matching prior maps. Runtime/source contracts remain exact. No visual/adoption/phone/all-site acceptance.'}
(review / 'fixture-preparation.json').write_text(json.dumps(record, indent=2) + '\n')
print('ISLAND_LIT_FIXTURE_PREPARED_NO_NATIVE_START')
