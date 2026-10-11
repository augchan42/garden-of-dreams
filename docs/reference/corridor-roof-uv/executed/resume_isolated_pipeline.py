"""Continue after a terminal runner marker failure; never restart source bakes."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
r=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();state=r/'isolated-pipeline.json'
old=json.loads(state.read_text());assert old['status']=='failed' and old['source_glb_sha256']=='7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b'
process=subprocess.run(['ps','-p',str(old['orchestrator_pid']),'-o','command='],capture_output=True,text=True);assert process.returncode!=0 or str(r/'continue_isolated_pipeline.py') not in process.stdout
refresh=json.loads((r/'export/full-lighting-refresh.json').read_text());assert refresh['status']=='source_complete' and len(refresh['phases'])==6 and all(p['status']=='passed' and p['exit_code']==0 for p in refresh['phases'])
report={'status':'source_complete_isolated_checks_running','orchestrator_pid':os.getpid(),'orchestrator_command':str(Path(__file__).resolve()),'source_glb_sha256':old['source_glb_sha256'],'phases':[],'resumed_failed_report':str(r/'failed-marker-01/isolated-pipeline.json'),'scope':old['scope']}
def save():
 t=state.with_suffix('.new');t.write_text(json.dumps(report,indent=2)+'\n');t.replace(state)
def run(name,script,marker,timeout):
 phase={'name':name,'status':'running','command':[sys.executable,str(r/script)],'log':str(r/('resumed-pipeline-'+name+'.log'))};report['phases'].append(phase);save()
 with Path(phase['log']).open('w') as stream:
  child=subprocess.Popen(phase['command'],cwd=r,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid;save()
  try:phase['exit_code']=child.wait(timeout=timeout)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=20);raise
 text=Path(phase['log']).read_text(errors='replace');assert phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-4000:]
 phase.update(status='passed',log_sha256=sha(Path(phase['log'])));save();print('ROOF_RESUMED_PIPELINE_PASS',name,flush=True)
try:
 save();run('native','resume_lighting.py','CORRIDOR_ROOF_ISOLATED_LIT_CHECKS_PASS',900)
 run('native-originals','verify_lit_native.py','CORRIDOR_ROOF_NATIVE_FILES_PASS',120)
 run('tours','run_tours.py','CORRIDOR_ROOF_NATIVE_TOUR_PASS',3100)
 run('tour-originals','verify_tour_files.py','CORRIDOR_ROOF_TOUR_FILES_PASS',120)
 report['status']='isolated_source_native_tours_complete_direct_review_adoption_pending';save();print('CORRIDOR_ROOF_ISOLATED_PIPELINE_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
