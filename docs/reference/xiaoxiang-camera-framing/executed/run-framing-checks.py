from pathlib import Path
import hashlib,json,subprocess,sys,re,datetime
root=Path('/tmp/garden-xiaoxiang-framing-20261010');game=root/'godot';out=root/'framing-validation-v5';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mode=sys.argv[1];report={'status':'running','mode':mode,'runtime_sha256':sha(game/'runtime/entry_route.gd'),'source_glb_sha256':sha(game/'assets/garden-of-dreams.glb'),'phases':[]}
path=out/(mode+'-pipeline.json')
def save():path.write_text(json.dumps(report,indent=2)+'\n')
def run(name,command,marker,timeout=240):
 log=out/(name+'.log');assert not log.exists()
 row={'name':name,'command':command,'log':str(log),'status':'running'};report['phases'].append(row);save();print('FRAMING_CHECK_START',name,flush=True)
 with log.open('w') as f:
  child=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT);row['pid']=child.pid;save()
  try:row['exit_code']=child.wait(timeout=timeout)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);row['exit_code']=124
 text=log.read_text(errors='replace');okay=row['exit_code']==0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)|AssertionError:',text)
 row.update(status='passed' if okay else 'failed',log_sha256=sha(log));save();assert okay,(name,text[-4000:]);print('FRAMING_CHECK_PASS',name,flush=True)
godot='/Applications/Godot.app/Contents/MacOS/Godot';head=[godot,'--headless','--path',str(game)];native=[godot,'--path',str(game),'--windowed','--resolution','1410x600']
try:
 if mode=='headless':
  for name,script,marker in [('entry','test_entry_route.gd','ENTRY_ROUTE_PASS'),('bamboo-route','test_bamboo_route.gd','BAMBOO_ROUTE_PASS'),('first-demo','test_first_reading_demo.gd','FIRST_READING_DEMO_PASS'),('surface','test_surface_materials.gd','SURFACE_MATERIAL_PASS'),('mobile-ui','test_mobile_ui_scaling.gd','MOBILE_UI_SCALE_PASS')]:run(name,head+['--script','res://tests/'+script],marker)
 elif mode=='native':
  run('transition',native+['--script','res://tests/test_xiaoxiang_camera_transition.gd'],'XIAOXIANG_CAMERA_TRANSITION_RESULT 0 failures')
  for name,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
   run('framing-'+name,native+['--script','res://tests/test_xiaoxiang_framing.gd','--','--output='+str(out/name),'--source='+report['source_glb_sha256'],*flags],'XIAOXIANG_FRAMING_RESULT 30 originals; 0 failures')
  run('pavilion',native+['--script','res://tests/test_pavilion_portrait_framing.gd'],'PAVILION_PORTRAIT_FRAMING_PASS')
  for name,flags in [('palette-normal',[]),('palette-demo',['--demo'])]:run(name,native+['--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(out/(name+'.json')),*flags],'GARDEN_PALETTE_TRANSFER_PASS')
 elif mode=='tours':
  assert json.loads((out/'native-pipeline.json').read_text())['status']=='passed'
  for name,flags in [('tour-desktop',[]),('tour-portrait',['--portrait'])]:
   dest=out/name;run(name,native+['--script','res://tests/render_full_garden_traversal.gd','--','--capture-directory='+str(dest),'--output='+str(dest/'report.json'),*flags],'FULL_GARDEN_TRAVERSAL_PASS rooms=14 legs=26',900)
 else:raise ValueError(mode)
 assert sha(game/'runtime/entry_route.gd')==report['runtime_sha256']
 report['status']='passed';save();print('FRAMING_PIPELINE_PASS',mode,flush=True)
except BaseException as e:report.update(status='failed',error=str(e));save();raise
