from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys
from datetime import datetime,timezone
REPO=Path('/Users/auchan/projects/garden-of-dreams')
ROOT=Path(json.loads(Path('/tmp/garden-hengwu-full-review.json').read_text())['folder']).resolve()
GD=ROOT/'godot';LOG=ROOT/'review-resume-logs';LOG.mkdir(exist_ok=False)
REPORT=ROOT/'review-resume-pipeline.json'
EXPECTED='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((ROOT/'first-review-pipeline.json').read_text())
assert prior['status']=='failed' and prior['phases'][-1]['name']=='portrait-architecture' and prior['phases'][-1]['exit_code']==1
assert sha(GD/'assets/garden-of-dreams.glb')==EXPECTED
assert sha(GD/'runtime/entry_route.gd')==sha(REPO/'godot/runtime/entry_route.gd')=='db32d9c058a732c330d9df910b22b961f755045c5904c47e8fde68fd3c056138'
for name,digest in prior['runtime_inputs_sha256'].items():
 if name not in ['tests/test_portrait_architecture.gd','tests/render_hengwu_lit_candidate.gd']:assert sha(GD/name)==digest,name
reused=[]
for phase in prior['phases']:
 if phase['status']=='passed' and phase['name']!='hengwu-lit-actions':
  assert sha(phase['log'])==phase['log_sha256'];reused.append(phase)
assert len(reused)==28
report={'status':'running','source_glb_sha256':EXPECTED,'orchestrator_pid':os.getpid(),'started_at':datetime.now(timezone.utc).isoformat(),'root':str(ROOT),'first_review_report':str(ROOT/'first-review-pipeline.json'),'reused_completed_checks':reused,'invalidated_first_capture_report':str(ROOT/'first-lit-capture-pose-rejection.json'),'updated_test_inputs_sha256':{name:sha(GD/name) for name in ['tests/test_portrait_architecture.gd','tests/render_hengwu_lit_candidate.gd']},'phases':[],'scope':'Resume after a terminal native test failure. Runtime/source unchanged; test waits now use actual camera tween completion with timeout. Original failure and six rejected partial action captures are retained. Completed source/import/lighting/library/reexport/memory checks are reused after verifying their original logs. Final art, devices, references, release and services remain open.'}
godot='/Applications/Godot.app/Contents/MacOS/Godot';head=[godot,'--headless','--path',str(GD)];native=[godot,'--path',str(GD)]
def save():REPORT.write_text(json.dumps(report,indent=2)+'\n')
def emit(message):print(message,flush=True)
def alive(pid):
 try:os.kill(pid,0);return True
 except ProcessLookupError:return False

def run(label,command,expected_marker=None,expected_exit=0):
 assert sha(ROOT/'export/garden-of-dreams.glb')==EXPECTED
 phase={'name':label,'command':command,'status':'running','log':str(LOG/(label+'.log'))};report['phases'].append(phase);save();emit('REVIEW_PHASE_START '+label)
 with open(phase['log'],'w') as log:
  child=subprocess.Popen(command,cwd=GD,stdout=log,stderr=subprocess.STDOUT)
  phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 text=Path(phase['log']).read_text(errors='replace')
 phase['log_sha256']=sha(phase['log'])
 assert phase['exit_code']==expected_exit,(label,phase['exit_code'],text[-3000:])
 if expected_exit==0:
  assert not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed)',text),(label,text[-4000:])
 if expected_marker:assert expected_marker in text,(label,'missing success marker',text[-3000:])
 phase['status']='passed';save();emit('REVIEW_PHASE_PASS '+label)

try:
 shutil.copy2(__file__,ROOT/"executed-review-resume.py")
 save()
 cap=ROOT/'review-captures-completed-camera-waits';cap.mkdir(exist_ok=False)
 run('hengwu-lit-actions-completed',native+['--script','res://tests/render_hengwu_lit_candidate.gd','--','--output='+str(cap/'hengwu-lit-actions')],'HENGWU_LIT_ACTIONS_RECORDED')
 run('portrait-architecture-completed',native+['--script','res://tests/test_portrait_architecture.gd','--','--output='+str(cap/'portrait-architecture')],'PORTRAIT_ARCHITECTURE_RESULT')
 for label,script,marker in [('courtyard','test_courtyard_route.gd','COURTYARD_ROUTE_PASS'),('farmhouse','test_farmhouse_route.gd','FARMHOUSE_ROUTE_PASS')]:
  run('route-'+label,head+['--script','res://tests/'+script],marker)
 for label,args in [('framing',[]),('framing-density',['--density'])]:
  run('ouxiang-'+label,native+['--script','res://tests/test_oux_portrait_framing.gd','--','--output='+str(cap/label),*args],'OUXIANG_FRAMING_PASS')
  framing=json.loads((cap/label/'report.json').read_text());assert framing['status']=='passed'
 for label,script,marker in [('western','test_western_route.gd','WESTERN_ROUTE_PASS'),('nunnery','test_nunnery_route.gd','NUNNERY_ROUTE_PASS'),('mobile-ui','test_mobile_ui_scaling.gd','MOBILE_UI_SCALE_PASS')]:
  run('route-'+label,head+['--script','res://tests/'+script],marker)
 run('moon-source-transfer',native+['--script','res://tests/test_moon_paint_transfer.gd','--','--source=res://assets/garden-of-dreams.glb','--atlas=res://tests/moon-paint-atlas.json','--output-directory='+str(cap/'moon-transfer')],'MOON_PAINT_TRANSFER_PASS')
 run('moon-baked-scene',native+['--script','res://tests/diagnose_moon_scene_contrast.gd','--','--output-directory='+str(cap/'moon-scene')],'MOON_SCENE_CONTRAST_DIAGNOSIS_RECORDED')
 for label,args in [('desktop',[]),('portrait',['--mobile'])]:
  run('arrivals-'+label,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--output-directory='+str(cap/('arrivals-'+label)),*args],'ROUTE_RENDER_SAVED')
  arrival=json.loads((cap/('arrivals-'+label)/('route-'+label+'-report.json')).read_text())
  assert arrival['source_glb_sha256']==EXPECTED and len(arrival['captures'])==14
 for label,args in [('desktop',[]),('portrait',['--portrait'])]:
  out=cap/('tour-'+label);out.mkdir()
  run('tour-'+label,native+['--script','res://tests/render_full_garden_traversal.gd','--','--capture-directory='+str(out),'--output='+str(out/'report.json'),*args],'FULL_GARDEN_TRAVERSAL')
  tour=json.loads((out/'report.json').read_text());assert tour['source_glb_sha256']==EXPECTED
 for label,flag in [('plain','--corrupt-plain'),('atlas','--corrupt-atlas')]:
  rejected=ROOT/('rejected-palette-'+label+'.json')
  run('reject-palette-'+label,native+['--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(rejected),flag],'GARDEN_PALETTE_TRANSFER_REJECTED',1)
  assert not rejected.exists()
 for label,args in [('normal',[]),('demo',['--demo'])]:
  out=ROOT/('garden-palette-transfer-'+label+'.json')
  run('palette-transfer-'+label,native+['--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(out),*args],'GARDEN_PALETTE_TRANSFER_PASS')
  palette=json.loads(out.read_text());assert palette['status']=='passed' and palette['source_glb_sha256']==EXPECTED
 report['status']='technical_checks_complete_visual_review_pending';report['finished_at']=datetime.now(timezone.utc).isoformat();save()
 emit('HENGWU_FULL_TECHNICAL_REVIEW_COMPLETE '+str(ROOT))
except BaseException as error:
 report["status"]="failed";report["error"]=str(error);save();raise
