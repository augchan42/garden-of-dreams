"""Prepare a separate Godot review with no native app launch and no old maps."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/paving-site-joins'
source=Path('/tmp/garden-paving-joins-20261010-v4')
review=Path('/tmp/garden-paving-review-20261010-v4')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
audit=json.loads((work/'candidate-paving-audit-v4-normalized.json').read_text())
assert audit['status']=='saved_paving_disjoint_and_footprint_preserved'
baseline=sha(repo/'export/garden-of-dreams.glb');candidate=sha(source/'export/garden-of-dreams.glb')
assert baseline=='c9d4fb308730733af2175c424449f8a63b731674d2527df2168a260cc0f5013e'
assert candidate=='ba40866e18f9ab3dcb0263855020099b7eedce70243c6a37e4d50c5f74c0e4f2'
assert not review.exists()
review.mkdir()
shutil.copytree(source/'blender',review/'blender',ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
for p in (repo/'blender/kits').glob('*.blend'):
    if p.name!='KIT_water.blend':shutil.copyfile(p,review/'blender/kits'/p.name)
shutil.copytree(source/'scripts',review/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(source/'export',review/'export',ignore=shutil.ignore_patterns('lightmaps','full-lighting-refresh.json','lightmaps-coverage.json','lightmap-pixels.json','terminal-spill-pixels.json'))
shutil.copytree(repo/'export/kits',review/'export/kits',dirs_exist_ok=True)
shutil.copytree(source/'textures',review/'textures')
shutil.copytree(repo/'docs/sites',review/'docs/sites')
shutil.copytree(source/'docs/reference/paving-surface-joins',review/'docs/reference/paving-surface-joins')
ignore=shutil.ignore_patterns('.godot','lightmaps','acceptance-captures','captures')
game=review/'godot';shutil.copytree(repo/'godot',game,ignore=ignore);(game/'lightmaps').mkdir()
shutil.copyfile(source/'export/garden-of-dreams.glb',game/'assets/garden-of-dreams.glb')
(game/'assets/garden-source.json').write_text(json.dumps({'source_glb_sha256':candidate},indent=2)+'\n')
subprocess.run([sys.executable,str(review/'scripts/build_godot_import_contract.py'),'--source',str(source/'export/garden-of-dreams.glb'),'--output',str(game/'tests/source-contract.json')],check=True)
old=json.loads((repo/'godot/tests/source-contract.json').read_text());new=json.loads((game/'tests/source-contract.json').read_text())
for key in ['cameras','colliders','markers','render_meshes']:assert old[key]==new[key],key
assert [len(new[k]) for k in ['cameras','colliders','markers']]==[42,454,71] and new['render_meshes']==167
# Source identity only changes; retain every existing public action, projection,
# timing, shape, lighting, description, visitor, density and touch assertion.
guards={}
for p in sorted((game/'tests').glob('*')):
    if p.suffix not in ['.gd','.json'] or p.name in ['source-contract.json','garden-palette-contract.json']:continue
    text=p.read_text()
    if baseline in text:
        before=sha(p);p.write_text(text.replace(baseline,candidate));guards[p.name]={'before_sha256':before,'after_sha256':sha(p),'substitutions':text.count(baseline),'change':'source digest only; all assertions retained'}
subprocess.run([sys.executable,str(review/'scripts/build_garden_palette_contract.py'),'--source',str(source/'export/garden-of-dreams.glb'),'--atlas-root',str(review),'--output',str(game/'tests/garden-palette-contract.json')],check=True)
palette_old=json.loads((repo/'godot/tests/garden-palette-contract.json').read_text());palette_new=json.loads((game/'tests/garden-palette-contract.json').read_text());palette_old['source_glb_sha256']=candidate
# The common-material generator does not include the reviewed stage canvas.
# Verify that extra expectation against the actual exported factor and count.
sys.path.insert(0,str(review/'scripts'))
from verify_mountain_export import Glb
import numpy as np
actual=Glb(source/'export/garden-of-dreams.glb')
canvas=next(m for m in actual.doc['materials'] if m['name']=='MAT_stage_canvas')
pbr=canvas['pbrMetallicRoughness'];expected_canvas=palette_old['plain_materials']['MAT_stage_canvas']
assert np.allclose(pbr['baseColorFactor'],expected_canvas['base_color_linear_rgba'],atol=1e-7,rtol=0)
assert pbr.get('metallicFactor',1)==expected_canvas['metallic'] and abs(pbr['roughnessFactor']-expected_canvas['roughness'])<1e-7
assert 'baseColorTexture' not in pbr and canvas.get('emissiveFactor',[0,0,0])==[0,0,0]
canvas_count=sum(actual.doc['materials'][p['material']]['name']=='MAT_stage_canvas' for n in actual.doc['nodes'] if 'mesh' in n and not n['name'].startswith('COL_') for p in actual.doc['meshes'][n['mesh']]['primitives'])
assert canvas_count==expected_canvas['source_surface_count']==1
palette_new['plain_materials']['MAT_stage_canvas']=expected_canvas
assert palette_old==palette_new,'Source palette changed'
(game/'tests/garden-palette-contract.json').write_text(json.dumps(palette_new,indent=2)+'\n')
base_game=review/'baseline-godot'
shutil.copytree(repo/'godot',base_game,ignore=shutil.ignore_patterns('.godot','acceptance-captures','captures'))
assert sha(base_game/'assets/garden-of-dreams.glb')==baseline
assert sha(game/'runtime/entry_route.gd')==sha(base_game/'runtime/entry_route.gd')==sha(repo/'godot/runtime/entry_route.gd')
assert not (game/'.godot').exists() and not (base_game/'.godot').exists() and not list((game/'lightmaps').iterdir())
record={'status':'static_paving_review_prepared_no_native_app_started','source_root':str(source),'review_root':str(review),'baseline_glb_sha256':baseline,'candidate_glb_sha256':candidate,'authoring_sha256':sha(source/'blender/authoring.blend'),'runtime_sha256':sha(game/'runtime/entry_route.gd'),'source_contract_sha256':sha(game/'tests/source-contract.json'),'palette_contract_sha256':sha(game/'tests/garden-palette-contract.json'),'source_guard_only_changes':guards,'paving_native_regression_sha256':sha(game/'tests/test_paving_surface_transfer.gd'),'counts':{'cameras':42,'colliders':454,'markers':71,'render_meshes':167},'scope':'Both fixtures share current runtime and new floor plane IDs/hide/lit regression,1.8seconds/fixedclock3. Candidate has no maps; copy only complete fresh matching141sourcePNGs after sole source worker16116anditschildren exit. Existing source guards update onlydigest; palette expectations identical. Source/default16exports/14arrivals/all26legdesktop+portraittours/adjacentviews still require actual native execution and direct originals review. No product adoption or all-site/phone/fullgoal acceptance.'}
(review/'fixture-preparation.json').write_text(json.dumps(record,indent=2)+'\n')
shutil.copyfile(__file__,review/'executed-fixture-preparation.py')
print('PAVING_STATIC_NATIVE_FIXTURE_PREPARED',len(guards),'source-only guards; no native start')
