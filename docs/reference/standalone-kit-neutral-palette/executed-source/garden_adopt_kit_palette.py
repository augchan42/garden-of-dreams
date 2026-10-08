import datetime,hashlib,json,shutil,subprocess,sys
from pathlib import Path
root=Path('/Users/auchan/projects/garden-of-dreams');c=json.loads(Path('/tmp/garden-kit-neutral-palette.json').read_text());work=Path(c['work']);candidate=Path(c['candidate']);project=work/'godot';out=work/'adoption';out.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert json.loads((work/'source-update.json').read_text())['status']=='four_saved_kits_updated_exported_preserved'
assert json.loads((work/'export-preservation.json').read_text())['status']=='48_native_exports_preserve_contracts_change_only_one_color_image_each'
assert json.loads((work/'native-checks/report.json').read_text())['status']=='ten_native_kit_phases_passed'
assert json.loads((work/'native-palettes-final/report.json').read_text())['status']=='48_native_kit_palette_and_pbr_bindings_passed'
for rel,wanted in c['inputs'].items():assert sha(root/rel)==wanted,('Production input changed',rel)
protected=[root/'blender/authoring.blend',root/'blender/master.blend',root/'export/garden-of-dreams.glb',root/'godot/assets/garden-of-dreams.glb',*sorted((root/'blender/sites').glob('*.blend')),*sorted((root/'export/sites').glob('*.glb')),*[p for folder in ('godot/runtime','godot/lightmaps') for p in sorted((root/folder).rglob('*')) if p.is_file()]]
protected_hashes={str(p.relative_to(root)):sha(p) for p in protected}
updates={}
for kit in ('pavilion','corridor','wall','rockery'):
 for p in [candidate/f'blender/kits/KIT_{kit}.blend',*sorted((candidate/f'export/kits/{kit}').glob('*.glb')),*[candidate/f'export/kits/KIT_{kit}{s}.glb' for s in ('','_LOD1')]]:
  updates[str(p.relative_to(candidate))]=p
 for p in sorted((project/f'assets/kits/{kit}').glob('*')):
  if not p.is_file():continue
  rel='godot/'+str(p.relative_to(project));old=root/rel
  assert old.exists(),('Unexpected generated engine input',rel)
  if sha(p)!=sha(old):
   assert p.suffix=='.glb' or '_basecolor.png' in p.name,('Unrelated engine image/import changed',rel)
   updates[rel]=p
backup=out/'backup';targets={}
for rel,p in updates.items():
 old=root/rel;assert old.exists();dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
 targets[rel]={'before_sha256':sha(old),'after_sha256':sha(p),'candidate':str(p),'backup':str(dest)}
report={'status':'preflight_passed','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'targets':targets,'protected_hashes':protected_hashes,'checks':[]}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 for rel,row in targets.items():
  assert sha(root/rel)==row['before_sha256'];assert sha(Path(row['candidate']))==row['after_sha256'];shutil.copy2(row['candidate'],root/rel)
 for rel,wanted in protected_hashes.items():assert sha(root/rel)==wanted,('Unrelated garden file changed',rel)
 print('APPLIED',len(targets),'kit files with backups; assembled source/maps/runtime unchanged',flush=True)
 godot='/Applications/Godot.app/Contents/MacOS/Godot';path=str(root/'godot')
 commands=[('production-import',[godot,'--headless','--path',path,'--editor','--import']),('production-kit-palette',[godot,'--path',path,'--windowed','--resolution','1600x900','--script','res://tests/test_standalone_kit_palette.gd','--','--output='+str(out/'production-palettes')])]
 for kit in ('pavilion','corridor','wall','rockery'):
  commands.append(('production-pbr-'+kit,[godot,'--headless','--path',path,'--script','res://tests/test_pavilion_atlas.gd','--']+([] if kit=='pavilion' else ['--'+kit])))
 for name,args in commands:
  log=out/(name+'.log');print('START',name,flush=True)
  with log.open('w') as file:r=subprocess.run(args,stdout=file,stderr=subprocess.STDOUT,timeout=900)
  text=log.read_text();assert r.returncode==0 and 'SCRIPT ERROR' not in text and 'ERROR:' not in text,(name,text[-5000:])
  report['checks'].append({'name':name,'command':args,'exit_code':r.returncode,'log':str(log)});print('PASS',name,flush=True)
 for kit in ('pavilion','corridor','wall','rockery'):
  name='production-cpu-'+kit;args=[sys.executable,str(root/'scripts/verify_pavilion_atlas.py'),'--kit',kit];log=out/(name+'.log')
  with log.open('w') as file:r=subprocess.run(args,stdout=file,stderr=subprocess.STDOUT,timeout=300)
  assert r.returncode==0,(name,log.read_text());report['checks'].append({'name':name,'command':args,'exit_code':r.returncode,'log':str(log)});print('PASS',name,flush=True)
 for rel,row in targets.items():assert sha(root/rel)==row['after_sha256'],('Adopted file differs after reimport',rel)
 for rel,wanted in protected_hashes.items():assert sha(root/rel)==wanted,('Unrelated garden file changed after reimport',rel)
 report['status']='four_standalone_kit_palettes_installed_ten_production_checks_passed'
except BaseException as error:
 for rel,row in targets.items():shutil.copy2(row['backup'],root/rel)
 report['status']='rolled_back';report['error']=repr(error)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');raise
report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('KIT_PALETTE_ADOPTION_PASS',len(targets),flush=True)
