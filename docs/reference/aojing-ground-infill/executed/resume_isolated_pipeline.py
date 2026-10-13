from pathlib import Path
import hashlib,json,os,re,subprocess,sys
r=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();state=r/'isolated-pipeline.json'
old=json.loads(state.read_text());assert old['status']=='failed' and old['source_glb_sha256']=='09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290'
p=subprocess.run(['ps','-p',str(old['orchestrator_pid']),'-o','command='],capture_output=True,text=True);assert p.returncode!=0 or 'continue_isolated_pipeline.py' not in p.stdout
report={**old,'status':'source_complete_isolated_checks_running','orchestrator_pid':os.getpid(),'phases':[],'resumed_failed_report':str(r/'failed-native-winding-01/isolated-pipeline.json')};report.pop('error',None)
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
 run('native','resume_lighting.py','CORRIDOR_ROOF_ISOLATED_LIT_CHECKS_PASS',1300)
 run('native-originals','verify_lit_native.py','AOJING_GROUND_NATIVE_FILES_PASS',120)
 run('tours','run_tours.py','CORRIDOR_ROOF_NATIVE_TOUR_PASS',3100)
 run('tour-originals','verify_tour_files.py','CORRIDOR_ROOF_TOUR_FILES_PASS',120)
 report['status']='isolated_source_native_tours_complete_direct_review_adoption_pending';save();print('AOJING_ISOLATED_PIPELINE_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
