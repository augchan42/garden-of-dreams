"""Stage the tested Xiaoxiang cameras with recoverable original-file backups."""
from pathlib import Path
import hashlib,json,os,subprocess,re,sys
repo=Path('/Users/auchan/projects/garden-of-dreams')
source=Path('/tmp/garden-xiaoxiang-framing-20261010')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/xiaoxiang-bamboo-source/framing-adoption'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
new='ec42ec55bf382ec314b6da325da741d214d297d81418d4da38bdabe0d017ec87'
old='bde869171ad37d520ce34d10aa1ca825a327a6c6c6ce13e3dfafbeca6be5ba95'
glb='faa8a7fe4a7a399899e84373c0550c8ff2f5f15ab0273109e8ea68f433b8fe0f'
names=['godot/runtime/entry_route.gd','godot/assets/xiaoxiang-camera-subjects.json','godot/tests/test_xiaoxiang_framing.gd','godot/tests/test_xiaoxiang_camera_transition.gd','godot/tests/xiaoxiang-camera-subjects-complete.json','scripts/extract_xiaoxiang_camera_subjects.py']
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def validation():
 assert sha(source/'godot/runtime/entry_route.gd')==new
 assert sha(source/'godot/assets/garden-of-dreams.glb')==sha(repo/'godot/assets/garden-of-dreams.glb')==glb
 for mode,count in [('native',7),('headless',5),('tours',2)]:
  report=load(source/'framing-validation-v5'/(mode+'-pipeline.json'))
  assert report['status']=='passed' and report['runtime_sha256']==new and len(report['phases'])==count
  for phase in report['phases']:assert phase['status']=='passed' and phase['exit_code']==0 and sha(phase['log'])==phase['log_sha256']
 for mode in ['tour-desktop','tour-portrait']:
  report=load(source/'framing-validation-v5'/mode/'report.json')
  assert report['status']=='passed' and report['route_sha256']==new and not report['floor_failures'] and not report['error']
  assert len(report['legs'])==len(report['settled_arrivals'])==len(report['arrival_signals'])==26 and len(report['visited_rooms'])==14
  assert report['time_scale']==1 and report['physics_ticks_per_second']==60 and report['maximum_practicals']<=4
  for row in report['captures']:assert sha(source/'framing-validation-v5'/mode/row['file'])==row['sha256']
 for mode in ['normal','touch','density']:
  report=load(source/'framing-validation-v5'/mode/'report.json')
  assert report['runtime_sha256']==new and not report['errors'] and len(report['rows'])==30
  for row in report['rows']:assert sha(row['capture'])==row['sha256']
def prepare():
 assert not work.exists();(work/'stage').mkdir(parents=True)
 assert sha(repo/'godot/runtime/entry_route.gd')==old
 plan={'status':'prepared_not_applied','items':[],'candidate_validation_pending':True}
 for name in names:
  p=repo/name;out=work/'stage'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((source/name).read_bytes())
  plan['items'].append({'target':name,'original_sha256':sha(p) if p.exists() else None,'staged_sha256':sha(out)})
 write(work/'plan.json',plan);print('FRAMING_ADOPTION_STAGED',len(names))
def apply():
 validation();plan=load(work/'plan.json');assert plan['status']=='prepared_not_applied'
 assert subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()=='codex/xiaoxiang-camera-framing'
 for item in plan['items']:
  p=repo/item['target'];assert (sha(p) if p.exists() else None)==item['original_sha256'];assert sha(work/'stage'/item['target'])==item['staged_sha256']
 report={'status':'applying','checks':[],'runtime_sha256':new};write(work/'application.json',report);done=[]
 def run(name,args,marker):
  log=work/(name+'.log');row={'name':name,'command':args,'log':str(log),'status':'running'};report['checks'].append(row);write(work/'application.json',report);print('FRAMING_INSTALLED_START',name,flush=True)
  with log.open('w') as f:
   child=subprocess.Popen(args,stdout=f,stderr=subprocess.STDOUT);row['pid']=child.pid;write(work/'application.json',report)
   try:row['exit_code']=child.wait(timeout=240)
   except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);row['exit_code']=124
  text=log.read_text(errors='replace');okay=row['exit_code']==0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)|AssertionError:',text)
  row.update(status='passed' if okay else 'failed',log_sha256=sha(log));write(work/'application.json',report);assert okay,(name,text[-2500:]);print('FRAMING_INSTALLED_PASS',name,flush=True)
 try:
  for item in plan['items']:
   name=item['target'];p=repo/name;backup=work/'backup'/name;backup.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():os.replace(p,backup)
   done.append(name);p.parent.mkdir(parents=True,exist_ok=True);os.replace(work/'stage'/name,p)
  godot='/Applications/Godot.app/Contents/MacOS/Godot';head=[godot,'--headless','--path',str(repo/'godot')];native=[godot,'--path',str(repo/'godot'),'--windowed','--resolution','1410x600']
  run('import',head+['--editor','--import'],'Godot Engine')
  run('transition',native+['--script','res://tests/test_xiaoxiang_camera_transition.gd'],'XIAOXIANG_CAMERA_TRANSITION_RESULT 0 failures')
  for mode,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:run('framing-'+mode,native+['--script','res://tests/test_xiaoxiang_framing.gd','--','--output='+str(work/mode),'--source='+glb,*flags],'XIAOXIANG_FRAMING_RESULT 30 originals; 0 failures')
  for name,script,marker in [('entry','test_entry_route.gd','ENTRY_ROUTE_PASS'),('bamboo','test_bamboo_route.gd','BAMBOO_ROUTE_PASS'),('demo','test_first_reading_demo.gd','FIRST_READING_DEMO_PASS'),('mobile-ui','test_mobile_ui_scaling.gd','MOBILE_UI_SCALE_PASS')]:run(name,head+['--script','res://tests/'+script],marker)
  exact={}
  for mode in ['normal','touch','density']:
   for row in load(work/mode/'report.json')['rows']:
    previous=source/'framing-validation-v5'/mode/Path(row['capture']).name;assert sha(row['capture'])==sha(previous);exact[mode+'/'+previous.name]=sha(previous)
  assert len(exact)==90
  for item in plan['items']:assert sha(repo/item['target'])==item['staged_sha256']
  report.update(status='working_camera_changes_adopted_installed_checks_passed',originals_byte_exact=exact);write(work/'application.json',report);plan['status']='applied';plan['candidate_validation_pending']=False;write(work/'plan.json',plan);print('FRAMING_WORKING_ADOPTION_PASS',flush=True)
 except BaseException as error:
  for name in reversed(done):
   p=repo/name;staged=work/'stage'/name;staged.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():os.replace(p,staged)
   backup=work/'backup'/name
   if backup.exists():os.replace(backup,p)
  report.update(status='rolled_back',error=str(error));write(work/'application.json',report);raise
if __name__=='__main__':apply() if '--apply' in sys.argv else prepare()
