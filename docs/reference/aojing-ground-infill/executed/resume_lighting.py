from pathlib import Path
import hashlib,json,subprocess,sys,re,os
root=Path('/tmp/garden-aojing-ground-v2-20261011');game=root/'godot';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290'
old=json.loads((root/'failed-native-winding-01/lit-validation.json').read_text())
assert old['status']=='failed' and old['source_glb_sha256']==expected
assert sha(game/'assets/garden-of-dreams.glb')==expected
assert sha(game/'tests/test_aojing_ground_native.gd')==sha(root/'test_aojing_ground_native.gd')
for n,d in json.loads((root/'full-lighting-inputs.json').read_text())['files'].items():assert sha(root/n)==d,n
fresh=json.loads((root/'export/full-lighting-refresh.json').read_text());assert fresh['status']=='source_complete' and len(fresh['phases'])==6 and all(p['status']=='passed' and p['exit_code']==0 for p in fresh['phases'])
assert [p['name'] for p in old['phases'][:5]]==['sync_full_lightmaps','sync_backdrop_wash','sync_terminal_spill','sync_demo','native_import']
for phase in old['phases'][:5]:assert phase['status']=='passed' and phase['exit_code']==0 and sha(Path(phase['log']))==phase['log_sha256']
corrected=json.loads((root/'export/ground-native-green.json').read_text());assert corrected['status']=='passed' and corrected['facts']['source_glb_sha256']==expected and corrected['facts']['clockwise_outward_faces_checked']==12
text=(root/'native-ground-corrected.log').read_text();assert 'AOJING_GROUND_NATIVE_PASS' in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:)',text)
report={**old,'status':'running','pid':os.getpid(),'phases':old['phases'][:5],'resumed_failed_report':str(root/'failed-native-winding-01/lit-validation.json')};report.pop('error',None)
report['phases'].append({'name':'ground_geometry','status':'passed','exit_code':0,'log':str(root/'native-ground-corrected.log'),'log_sha256':sha(root/'native-ground-corrected.log'),'test_sha256':sha(root/'test_aojing_ground_native.gd'),'credited_verified_standalone_phase':True})
logs=root/'lit-validation-logs'
godot='/Applications/Godot.app/Contents/MacOS/Godot';head=[godot,'--headless','--path',str(game)];native=[godot,'--path',str(game),'--windowed','--resolution','1410x600']
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
try:
 save()
 checks=[('roof_uv','test_corridor_roof_uv.gd','CORRIDOR_ROOF_UV_NATIVE_PASS',[]),('full_scene','test_full_scene_lighting.gd','FULL_SCENE_LIGHTING_PASS',['--imperial-lossless512','--ouxiang-lossless512']),('wash','test_backdrop_wash_import.gd','BACKDROP_WASH_IMPORT_PASS',[]),('spill','test_terminal_spill.gd','TERMINAL_SPILL_PASS',[]),('runtime_caps','test_runtime_texture_caps.gd','RUNTIME_TEXTURE_CAPS_PASS',[])]
 for name,script,marker,args in checks:run(name,head+['--script','res://tests/'+script,'--',*args],marker)
 run('roof_lit',native+['--script','res://tests/capture_corridor_lit.gd','--','--output='+str(root/'native-lit-corridor')],'CORRIDOR_LIT_PASS')
 run('ground_lit',native+['--script','res://tests/capture_aojing_lit.gd','--','--output='+str(root/'native-lit-ground')],'AOJING_LIT_PASS')
 for label,args in [('normal',[]),('touch',['--touch'])]:
  run('framing_'+label,native+['--script','res://tests/test_qiushuang_framing.gd','--','--output='+str(root/('lit-framing-'+label)),*args],'QIUSHUANG_FRAMING_RESULT')
 for label,args in [('desktop',[]),('portrait',['--mobile'])]:
  run('arrivals_'+label,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--fixed-clock','--output-directory='+str(root/('lit-arrivals-'+label)),*args],'ROUTE_RENDER_SAVED',timeout=240)
 report['status']='isolated_lit_views_and_resource_checks_passed_tours_and_direct_review_pending';save();print('CORRIDOR_ROOF_ISOLATED_LIT_CHECKS_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
