"""Validate the adopted canonical source and exact installed engine inputs."""
from pathlib import Path
import json,hashlib,subprocess,sys,re,os,shutil
root=Path('/tmp/garden-qiushuang-lattice-20261010');repo=Path('/Users/auchan/projects/garden-of-dreams');game=repo/'godot'
expected='72ad817f07e1fb13b565197f0a39984a2d97bc1c7c3dff6c1bccf3ae1125cab1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(repo/'export/garden-of-dreams.glb')==sha(game/'assets/garden-of-dreams.glb')==expected
assert not (root/'installed-validation.json').exists(),'Resume the recorded job'
logs=root/'installed-validation-logs';logs.mkdir()
report={'status':'running','pid':os.getpid(),'source_glb_sha256':expected,'phases':[],'scope':'Installed canonical source, exact engine inputs, actual native resources and screen views. No user editor reload, phone action, final art or performance acceptance.'}
def save():(root/'installed-validation.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,command,marker='',timeout=300):
 phase={'name':name,'status':'running','command':command,'log':str(logs/(name+'.log'))};report['phases'].append(phase);save();print('QIUSHUANG_INSTALLED_START',name,flush=True)
 with Path(phase['log']).open('w') as log:
  child=subprocess.Popen(command,cwd=repo,stdout=log,stderr=subprocess.STDOUT);phase['pid']=child.pid;save()
  try:phase['exit_code']=child.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   child.terminate();child.wait(timeout=15);phase['status']='timeout';save();raise
 text=Path(phase['log']).read_text(errors='replace')
 assert phase['exit_code']==0 and (not marker or marker in text) and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-4000:]
 phase.update(status='passed',log_sha256=sha(Path(phase['log'])));save();print('QIUSHUANG_INSTALLED_PASS',name,flush=True)
godot='/Applications/Godot.app/Contents/MacOS/Godot';blender='/Applications/Blender.app/Contents/MacOS/Blender'
head=[godot,'--headless','--path',str(game)];native=[godot,'--path',str(game),'--windowed','--resolution','1410x600']
bpy=[blender,'--background','--threads','8','--python-exit-code','1']
try:
 save()
 run('saved_rays',bpy+[str(repo/'blender/authoring.blend'),'--python',str(repo/'scripts/verify_qiushuang_lattice.py')],'QIUSHUANG_LATTICE_PASS')
 run('canonical_source',bpy+[str(repo/'blender/authoring.blend'),'--python',str(repo/'scripts/verify_saved_garden_candidate.py'),'--','--source-root',str(repo),'--output-root',str(root/'installed-source-replay')],timeout=420)
 run('site_sources',bpy+['--python',str(repo/'scripts/audit_site_sources.py')],timeout=420)
 run('uv2',[sys.executable,str(repo/'scripts/verify_uv2.py')],'UV2_MESHES',timeout=300)
 protected={str(p.relative_to(game)):p.read_text().split('[params]',1)[1] for p in (game/'lightmaps').rglob('*.png.import')}
 for script,marker,args in [('sync_full_lightmaps.py','FULL_LIGHTMAP_CATALOG_PASS',[]),('sync_backdrop_wash.py','BACKDROP_WASH_CATALOG_PASS',[]),('sync_terminal_spill.py','TERMINAL_SPILL_CATALOG_PASS',[]),('sync_lightmaps.py','source-compatible lightmaps',['--demo'])]:
  run(script.removesuffix('.py'),[sys.executable,str(repo/'scripts'/script),*args],marker)
 run('import_contract',[sys.executable,str(repo/'scripts/build_godot_import_contract.py')])
 run('native_import',head+['--editor','--import'],timeout=420)
 for name,params in protected.items():assert (game/name).read_text().split('[params]',1)[1]==params,name
 report['preserved_import_parameter_files']=len(protected);save()
 files=[]
 for source in (root/'godot/lightmaps').rglob('*'):
  if source.is_file() and source.suffix in ['.png','.json']:
   dest=game/source.relative_to(root/'godot');assert sha(dest)==sha(source),str(source);files.append(str(dest.relative_to(repo)))
 assert sha(game/'assets/garden-source.json')==sha(root/'godot/assets/garden-source.json')
 report['engine_input_files_exact_to_isolated_validation']=len(files);save()
 for name,script,marker,args in [('full_scene','test_full_scene_lighting.gd','FULL_SCENE_LIGHTING_PASS',['--imperial-lossless512','--ouxiang-lossless512']),('wash','test_backdrop_wash_import.gd','BACKDROP_WASH_IMPORT_PASS',[]),('spill','test_terminal_spill.gd','TERMINAL_SPILL_PASS',[]),('runtime_caps','test_runtime_texture_caps.gd','RUNTIME_TEXTURE_CAPS_PASS',[])]:
  run(name,head+['--script','res://tests/'+script,'--',*args],marker)
 run('cold_reimport',[sys.executable,str(repo/'scripts/verify_godot_reimport.py')],timeout=600)
 # The capture helper is a fixture, copied only for this native integration
 # check and removed on exit; it is not a production runtime change.
 helper=game/'tests/capture_lattice_lit.gd';assert not helper.exists()
 shutil.copy2(root/'capture_lattice_lit.gd',helper)
 try:run('native_lattice',native+['--script','res://tests/capture_lattice_lit.gd','--','--output='+str(root/'installed-native-qiushuang')],'QIUSHUANG_LATTICE_LIT_PASS')
 finally:
  helper.unlink(missing_ok=True);Path(str(helper)+'.uid').unlink(missing_ok=True)
 count=0
 for p in (root/'installed-native-qiushuang').glob('*.png'):
  assert p.read_bytes()==(root/'native-lit-qiushuang'/p.name).read_bytes(),p.name;count+=1
 assert count==8;report['installed_originals_exact_to_candidate']=count
 assert sha(repo/'godot/runtime/entry_route.gd')=='ec42ec55bf382ec314b6da325da741d214d297d81418d4da38bdabe0d017ec87'
 report['status']='installed_canonical_source_and_engine_checks_passed';save();print('QIUSHUANG_INSTALLED_VALIDATION_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
