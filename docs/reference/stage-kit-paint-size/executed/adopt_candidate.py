from pathlib import Path
import json,hashlib,shutil
r=Path(__file__).resolve().parent;repo=Path('/Users/auchan/projects/garden-of-dreams');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,d in json.loads((r/'inputs.json').read_text())['files'].items():assert sha(repo/n)==d,n
for n in ['source-preservation.json','export-preservation.json','canonical-replay.json','texture-size-green.json','native-fixed-comparison.json','direct-review.json','raw-native-textures.json']:
 assert json.loads((r/n).read_text())['status'] in ['passed','bounded_stage_export_change_accepted'],n
assert 'STAGE_EXPORT_EXCEPTION_CLEANUP_PASS' in (r/'export-exception-cleanup.log').read_text()
assert 'STAGE_RAW_RENDER_PASS' in (r/'raw-native-views.log').read_text()
protected={n:sha(repo/n) for n in ['blender/authoring.blend','blender/master.blend','blender/kits/KIT_stage.blend','export/garden-of-dreams.glb','godot/assets/garden-of-dreams.glb','godot/runtime/entry_route.gd']}
imports={str(p.relative_to(repo)):p.read_text().split('[params]',1)[1] for p in (repo/'godot/assets/kits/stage').glob('*.glb.import')}
targets={}
for p in (r/'candidate/export/kits/stage').glob('*.glb'):
 if sha(p)!=sha(repo/'export/kits/stage'/p.name):
  targets['export/kits/stage/'+p.name]=p;targets['godot/assets/kits/stage/'+p.name]=p
for name in ['KIT_stage.glb','KIT_stage_LOD1.glb']:
 targets['export/kits/'+name]=r/'candidate/export/kits'/name;targets['godot/assets/kits/'+name]=r/'candidate/export/kits'/name
for name in ['complete_stage_kit.py','stage_kit_export_texture.py','verify_stage_kit_texture_size.py']:targets['scripts/'+name]=r/'candidate/scripts'/name
targets['export/kits/stage/manifest.json']=r/'candidate/export/kits/stage/manifest.json'
backup=repo/'.superpowers/sdd/2026-09-23-garden-completion/stage-kit-adoption-20261011';backup.mkdir(exist_ok=False)
old={}
for n in list(targets)+['scripts/verify_stage_kit.py']:
 p=repo/n
 if p.exists():out=backup/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);old[n]=sha(p)
 else:old[n]=None
(backup/'backup.json').write_text(json.dumps({'files':old,'protected':protected,'import_parameters':imports},indent=2)+'\n')
for n,src in targets.items():dst=repo/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(dst)==sha(src)
p=repo/'scripts/verify_stage_kit.py';s=p.read_text();needle="(folder/'validation.json').write_text";assert s.count(needle)==1;s=s.replace(needle,"import subprocess,sys\nsubprocess.run([sys.executable,str(R/'scripts/verify_stage_kit_texture_size.py')],check=True)\n"+needle);p.write_text(s)
for n,d in protected.items():assert sha(repo/n)==d,n
for n,params in imports.items():assert (repo/n).read_text().split('[params]',1)[1]==params,n
(r/'adoption.json').write_text(json.dumps({'status':'adopted_installed_native_verification_pending','files':{n:sha(repo/n) for n in list(targets)+['scripts/verify_stage_kit.py']},'protected':protected,'import_parameters_preserved':len(imports),'backup':str(backup),'scope':'Standalone stage exports and canonical export checks only. Original source paints, editable library, full assembly/runtime and existing import parameters preserved.'},indent=2)+'\n');print('STAGE_KIT_ADOPTION_PASS',len(targets)+1)
