"""Observe the existing ground bake, then validate its isolated native project."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,sys,time,shlex
r=Path(__file__).resolve().parent
expected='09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check-ready-only',action='store_true');args=parser.parse_args()
def read(p):
 for attempt in range(3):
  try:return json.loads(p.read_text())
  except json.JSONDecodeError:
   if attempt==2:raise
   time.sleep(.1)
def ready():
 q=read(r/'resumed-queued-full-lighting.json');f=read(r/'export/full-lighting-refresh.json')
 assert q['status']=='fresh_ground_source_lighting_complete_native_review_pending','Existing source lighting is incomplete; no native phase may start'
 assert f['status']=='source_complete' and f['source_glb_sha256']==expected
 assert len(f['phases'])==6 and all(p['status']=='passed' and p['exit_code']==0 for p in f['phases'])
 for name,digest in read(r/'full-lighting-inputs.json')['files'].items():assert sha(r/name)==digest,name
 assert sha(r/'export/garden-of-dreams.glb')==expected
if args.check_ready_only:ready();print('AOJING_ISOLATED_PIPELINE_READY');sys.exit(0)
state=r/'isolated-pipeline.json';assert not state.exists(),'Inspect the same recorded observer instead of duplicating it'
q=read(r/'resumed-queued-full-lighting.json');pid=q['pid'];command=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip();assert any(Path(arg).resolve()==r/'resume_queue_full_lighting.py' for arg in shlex.split(command))
report={'status':'waiting_on_existing_source_job','orchestrator_pid':os.getpid(),'existing_source_queue_pid':pid,'source_glb_sha256':expected,'phases':[],'scope':'Existing isolated ground source job followed by native geometry/resources, originals and tours. No adoption, user editor, device or final art acceptance.'}
def save():
 t=state.with_suffix('.new');t.write_text(json.dumps(report,indent=2)+'\n');t.replace(state)
def run(name,script,marker,timeout):
 phase={'name':name,'status':'running','command':[sys.executable,str(r/script)],'log':str(r/('pipeline-'+name+'.log'))};report['phases'].append(phase);save()
 with Path(phase['log']).open('w') as stream:
  child=subprocess.Popen(phase['command'],cwd=r,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid;save()
  try:phase['exit_code']=child.wait(timeout=timeout)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=20);raise
 text=Path(phase['log']).read_text(errors='replace');assert phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-4000:]
 phase.update(status='passed',log_sha256=sha(Path(phase['log'])));save();print('AOJING_ISOLATED_PIPELINE_PHASE_PASS',name,flush=True)
try:
 save()
 while True:
  q=read(r/'resumed-queued-full-lighting.json')
  if q['status']=='fresh_ground_source_lighting_complete_native_review_pending':break
  assert q['status']=='fresh_ground_source_lighting_running',q
  p=subprocess.run(['ps','-p',str(pid),'-o','command='],text=True,capture_output=True)
  if p.returncode!=0 or not any(Path(arg).resolve()==r/'resume_queue_full_lighting.py' for arg in shlex.split(p.stdout)):time.sleep(.2);ready();break
  time.sleep(2)
 ready();report['status']='source_complete_isolated_checks_running';save()
 run('native','validate_lighting.py','CORRIDOR_ROOF_ISOLATED_LIT_CHECKS_PASS',1300)
 run('native-originals','verify_lit_native.py','AOJING_GROUND_NATIVE_FILES_PASS',120)
 run('tours','run_tours.py','CORRIDOR_ROOF_NATIVE_TOUR_PASS',3100)
 run('tour-originals','verify_tour_files.py','CORRIDOR_ROOF_TOUR_FILES_PASS',120)
 report['status']='isolated_source_native_tours_complete_direct_review_adoption_pending';save();print('AOJING_ISOLATED_PIPELINE_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
