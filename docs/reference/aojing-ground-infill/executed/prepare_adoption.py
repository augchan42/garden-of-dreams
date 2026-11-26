from pathlib import Path
import json,hashlib,subprocess
r=Path(__file__).resolve().parent;repo=Path('/Users/auchan/projects/garden-of-dreams');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected='09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290'
assert not (r/'adoption-baseline.json').exists(),'Inspect existing preparation'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()=='598e209278c38064e44f7f6341b86ba7913dcbc9'
assert sha(repo/'blender/authoring.blend')=='4eb31445889e5f30f57bb7935759d83169655eefea6c6cfa798879e9f384b0f6'
assert sha(repo/'export/garden-of-dreams.glb')=='7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b'
assert sha(r/'export/garden-of-dreams.glb')==expected
source=['blender/authoring.blend','blender/master.blend','scripts/fill_aojing_ground.py','scripts/test_aojing_ground.py','scripts/test_saved_canvas_palette.py','export/garden-of-dreams.glb','export/sites/SITE_stage.glb','export/manifest.json','export/full-lighting-refresh.json','export/site-wash-rig.json','export/candidate-libraries.json','export/lightmaps-coverage.json','export/lightmap-pixels.json','export/terminal-spill-pixels.json','export/pavilion-tile-uv-layout.json','export/uv2-validation.json']
for folder in ['blender/sites','export/lightmaps']:
 source += [str(p.relative_to(r)) for p in (r/folder).rglob('*') if p.is_file() and p.suffix in ['.blend','.png','.json']]
v=json.loads((r/'lit-validation.json').read_text());pins=v['updated_source_pins'];print('PINS',pins)
engine=['godot/assets/garden-of-dreams.glb','godot/assets/garden-source.json','godot/tests/test_aojing_ground_native.gd']
engine += ['godot/'+n if not n.startswith('godot/') else n for n in (pins.keys() if isinstance(pins,dict) else pins)]
engine += [str(p.relative_to(r)) for p in (r/'godot/lightmaps').rglob('*') if p.is_file() and p.suffix in ['.png','.json']]
names=sorted(set(source+engine));assert all((r/n).is_file() for n in names)
protected={str(p.relative_to(repo)):sha(p) for folder in ['blender/kits','blender/textures/stage','export/kits','godot/assets/kits'] for p in (repo/folder).rglob('*') if p.is_file() and p.suffix in ['.blend','.glb','.png','.json']}
for n in ['scripts/complete_stage_kit.py','scripts/verify_stage_kit.py','scripts/stage_kit_export_texture.py','scripts/verify_stage_kit_texture_size.py','godot/runtime/entry_route.gd']:
 protected[n]=sha(repo/n)
parameters={str(p.relative_to(repo)):p.read_text().split('[params]',1)[1] for folder in ['godot/lightmaps','godot/assets/kits'] for p in (repo/folder).rglob('*.import') if '[params]' in p.read_text()}
data={'status':'prepared_current_stage_branch','head':'598e209278c38064e44f7f6341b86ba7913dcbc9','files':{n:sha(repo/n) if (repo/n).exists() else None for n in names},'candidate_files':{n:sha(r/n) for n in names},'protected_files':protected,'protected_import_parameters':parameters,'scope':'Ground authoring/master/site library, canonical stage/global export, fresh maps and source-pin fixtures only. Current stage-kit source/export/engine code and all runtime retained.'}
(r/'adoption-baseline.json').write_text(json.dumps(data,indent=2)+'\n');print('AOJING_ADOPTION_PREPARATION_PASS',len(names),len(protected),len(parameters))
