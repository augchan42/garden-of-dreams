"""Install and review only a completed isolated current-source lighting set."""
from pathlib import Path
import json,hashlib,subprocess,sys,re,os,shutil
root=Path('/tmp/garden-corridor-roof-full-20261011');game=root/'godot'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b'
refresh_path=root/'export/full-lighting-refresh.json'
preparation_path=root/'lighting-preparation.json'
refresh=json.loads(refresh_path.read_text()) if refresh_path.exists() else {'status':'missing'}
preparation=json.loads(preparation_path.read_text()) if preparation_path.exists() else {'status':'missing'}
# Complete the preflight before native launches or any fixture map writes.
if refresh['status']!='source_complete' or preparation['status']!='complete_roof_source_lighting_passed_native_review_pending':
 raise RuntimeError('Source lighting is incomplete; no engine installation or native validation started')
assert len(refresh['phases'])==6 and all(p['status']=='passed' and p['exit_code']==0 for p in refresh['phases'])
assert sha(root/'export/garden-of-dreams.glb')==refresh['source_glb_sha256']==expected
baseline='ba0e8b16dc984c0655da1290bbb438e6b2a2a2b92d36b31c32f42c083690341f'
assert sha(game/'assets/garden-of-dreams.glb')==baseline, 'Isolated engine source already changed; inspect the recorded job'
pinned_files=[p for p in (game/'tests').glob('*.gd') if baseline in p.read_text() and p.name.startswith(('test_', 'render_'))]
assert len(pinned_files)==8, [p.name for p in pinned_files]
assert sha(game/'tests/capture_corridor_lit.gd')==sha(root/'capture_corridor_lit.gd')
frozen=json.loads((root/'full-lighting-inputs.json').read_text())['files']
for name,digest in frozen.items():assert sha(root/name)==digest,name
assert len(list((root/'export/lightmaps').rglob('*.png')))==141
assert not (root/'lit-validation.json').exists(),'Resume the recorded process; do not overwrite a previous validation'
logs=root/'lit-validation-logs';logs.mkdir()
report={'status':'running','pid':os.getpid(),'source_glb_sha256':expected,'phases':[],'scope':'Isolated current-source engine integration, native views and existing regression checks. No production adoption or phone/device/performance acceptance.'}
def save():(root/'lit-validation.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,command,marker,timeout=180):
 phase={'name':name,'status':'running','command':command,'log':str(logs/(name+'.log'))};report['phases'].append(phase);save()
 print('CORRIDOR_ROOF_LIT_START',name,flush=True)
 with Path(phase['log']).open('w') as log:
  child=subprocess.Popen(command,cwd=root,stdout=log,stderr=subprocess.STDOUT);phase['pid']=child.pid;save()
  try:phase['exit_code']=child.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   child.terminate();child.wait(timeout=15);phase.update(status='timeout');save();raise
 text=Path(phase['log']).read_text(errors='replace')
 assert phase['exit_code']==0 and (not marker or marker in text) and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-4000:]
 phase.update(status='passed',log_sha256=sha(Path(phase['log'])));save();print('CORRIDOR_ROOF_LIT_PASS',name,flush=True)
godot='/Applications/Godot.app/Contents/MacOS/Godot'
head=[godot,'--headless','--path',str(game)]
native=[godot,'--path',str(game),'--windowed','--resolution','1410x600']
try:
 save()
 # The full six-phase source preflight has passed; now update only this isolated engine.
 report['baseline_engine_source_glb_sha256']=sha(game/'assets/garden-of-dreams.glb')
 report['updated_source_pins']={str(p.relative_to(game)):sha(p) for p in pinned_files}
 save()
 shutil.copy2(root/'export/garden-of-dreams.glb',game/'assets/garden-of-dreams.glb')
 assert sha(game/'assets/garden-of-dreams.glb')==expected
 for p in pinned_files:p.write_text(p.read_text().replace(baseline,expected))
 # All import files already carry the reviewed production policies; preserve
 # those parameters through PNG replacement and native reimport.
 protected_imports={str(p.relative_to(game)):p.read_text().split('[params]',1)[1] for p in (game/'lightmaps').rglob('*.png.import')}
 for name,marker in [('sync_full_lightmaps.py','FULL_LIGHTMAP_CATALOG_PASS'),('sync_backdrop_wash.py','BACKDROP_WASH_CATALOG_PASS'),('sync_terminal_spill.py','TERMINAL_SPILL_CATALOG_PASS')]:
  run(name.removesuffix('.py'),[sys.executable,str(root/'scripts'/name)],marker)
 run('sync_demo',[sys.executable,str(root/'scripts/sync_lightmaps.py'),'--demo'],'source-compatible lightmaps')
 run('native_import',head+['--editor','--import'],'',timeout=300)
 for name,params in protected_imports.items():assert (game/name).read_text().split('[params]',1)[1]==params,('Import policy changed',name)
 report['preserved_lightmap_import_parameter_files']=len(protected_imports);save()
 checks=[('roof_uv','test_corridor_roof_uv.gd','CORRIDOR_ROOF_UV_NATIVE_PASS',[]),('full_scene','test_full_scene_lighting.gd','FULL_SCENE_LIGHTING_PASS',['--imperial-lossless512','--ouxiang-lossless512']),('wash','test_backdrop_wash_import.gd','BACKDROP_WASH_IMPORT_PASS',[]),('spill','test_terminal_spill.gd','TERMINAL_SPILL_PASS',[]),('runtime_caps','test_runtime_texture_caps.gd','RUNTIME_TEXTURE_CAPS_PASS',[])]
 for name,script,marker,args in checks:run(name,head+['--script','res://tests/'+script,'--',*args],marker)
 run('roof_lit',native+['--script','res://tests/capture_corridor_lit.gd','--','--output='+str(root/'native-lit-corridor')],'CORRIDOR_LIT_PASS')
 for label,args in [('normal',[]),('touch',['--touch'])]:
  run('framing_'+label,native+['--script','res://tests/test_qiushuang_framing.gd','--','--output='+str(root/('lit-framing-'+label)),*args],'CORRIDOR_ROOF_FRAMING_RESULT')
 for label,args in [('desktop',[]),('portrait',['--mobile'])]:
  run('arrivals_'+label,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--fixed-clock','--output-directory='+str(root/('lit-arrivals-'+label)),*args],'ROUTE_RENDER_SAVED',timeout=240)
 report['status']='isolated_lit_views_and_resource_checks_passed_tours_and_direct_review_pending';save()
 print('CORRIDOR_ROOF_ISOLATED_LIT_CHECKS_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
