"""Wait on the existing verified source job; never start or restart a bake.

After complete source gates, run only copied-project native validation and tours.
Production adoption, direct visual review and device actions remain separate.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,os,re,time
r=Path('/tmp/garden-corridor-roof-full-20261011');expected='7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=r/'isolated-pipeline.json';assert not state.exists(),'Resume existing pipeline instead of starting another'
prep=json.loads((r/'lighting-preparation.json').read_text());source_pid=prep['orchestrator_pid'];assert prep['status']=='running' and prep['source_glb_sha256']==expected
command=subprocess.check_output(['ps','-p',str(source_pid),'-o','command='],text=True).strip();assert str(r/'prepare_lighting.py') in command,'Existing source process is not live'
report={'status':'waiting_on_existing_source_job','orchestrator_pid':os.getpid(),'existing_source_pid':source_pid,'existing_source_command':command,'source_glb_sha256':expected,'phases':[],'scope':'Waits on one existing source job, then actual isolated native review/files/tours. No duplicate bake, production adoption, user-editor reload, phone/device action or final art claim.'}
def save():
 temporary=state.with_suffix('.json.new');temporary.write_text(json.dumps(report,indent=2)+'\n');temporary.replace(state)
def read(path):
 for attempt in range(3):
  try:return json.loads(path.read_text())
  except json.JSONDecodeError:
   if attempt==2:raise
   time.sleep(.1)
def run(name,args,marker,timeout):
 phase={'name':name,'status':'running','command':args,'log':str(r/('pipeline-'+name+'.log'))};report['phases'].append(phase);save();print('ROOF_PIPELINE_START',name,flush=True)
 with Path(phase['log']).open('w') as f:
  child=subprocess.Popen(args,cwd=r,stdout=f,stderr=subprocess.STDOUT);phase['pid']=child.pid;save()
  try:phase['exit_code']=child.wait(timeout=timeout)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=20);raise
 text=Path(phase['log']).read_text(errors='replace');assert phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-4000:]
 phase.update(status='passed',log_sha256=sha(Path(phase['log'])));save();print('ROOF_PIPELINE_PASS',name,flush=True)
try:
 save();deadline=time.monotonic()+10800
 while True:
  prep=read(r/'lighting-preparation.json')
  if prep['status']=='complete_roof_source_lighting_passed_native_review_pending':break
  assert prep['status']=='running',prep
  command=subprocess.run(['ps','-p',str(source_pid),'-o','command='],text=True,capture_output=True)
  if command.returncode!=0 or str(r/'prepare_lighting.py') not in command.stdout:
   # Re-read after terminal publication; never restart a missing job.
   time.sleep(.2);prep=read(r/'lighting-preparation.json')
   assert prep['status']=='complete_roof_source_lighting_passed_native_review_pending','Existing source process stopped before complete acceptance; inspect it rather than restarting'
   break
  assert time.monotonic()<deadline,'Observation deadline: inspect same source job; no restart'
  time.sleep(2)
 assert sha(r/'export/garden-of-dreams.glb')==expected
 refresh=read(r/'export/full-lighting-refresh.json');assert refresh['status']=='source_complete' and len(refresh['phases'])==6 and all(p['status']=='passed' and p['exit_code']==0 for p in refresh['phases'])
 report['status']='source_complete_isolated_checks_running';save()
 run('native',[sys.executable,str(r/'validate_lighting.py')],'CORRIDOR_ROOF_ISOLATED_LIT_CHECKS_PASS',1800)
 run('native-originals',[sys.executable,str(r/'verify_lit_native.py')],'CORRIDOR_ROOF_NATIVE_FILES_PASS',120)
 run('tours',[sys.executable,str(r/'run_tours.py')],'CORRIDOR_ROOF_NATIVE_TOUR_PASS',3100)
 run('tour-originals',[sys.executable,str(r/'verify_tour_files.py')],'CORRIDOR_ROOF_TOUR_FILES_PASS',120)
 report['status']='isolated_source_native_tours_complete_direct_review_adoption_pending';save();print('CORRIDOR_ROOF_ISOLATED_PIPELINE_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
