"""Resume three native phases after one verified runner-marker correction."""
from pathlib import Path
import hashlib,json,os,re,subprocess
from PIL import Image

r=Path(__file__).resolve().parent;game=r/'godot';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((r/'lit-validation.json').read_text())
assert report['status']=='failed' and report['source_glb_sha256']=='7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b'
assert len(report['phases'])==12 and all(p['status']=='passed' and p['exit_code']==0 for p in report['phases'][:-1])
phase=report['phases'][-1];assert phase['name']=='framing_normal' and phase['exit_code']==0
log=Path(phase['log']).read_text();assert 'QIUSHUANG_FRAMING_RESULT 18 originals; 0 failures' in log and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)',log)
actual=json.loads((r/'lit-framing-normal/report.json').read_text());assert actual['status']=='qiushuang_framing_passed' and not actual['errors'] and not actual['touch'] and len(actual['rows'])==18
assert actual['source_glb_sha256']==sha(r/'export/garden-of-dreams.glb')==sha(game/'assets/garden-of-dreams.glb')==report['source_glb_sha256']
assert actual['route_sha256']==sha(game/'runtime/entry_route.gd') and actual['test_sha256']==sha(game/'tests/test_qiushuang_framing.gd')
for row in actual['rows']:
 assert sha(Path(row['capture']))==row['sha256'] and not row['camera_transition_running']
 with Image.open(row['capture']) as image:image.load();assert image.format=='PNG' and list(image.size)==row['pixels']
for n,d in json.loads((r/'full-lighting-inputs.json').read_text())['files'].items():assert sha(r/n)==d,n
assert json.loads((r/'lighting-preparation.json').read_text())['status']=='complete_roof_source_lighting_passed_native_review_pending'
assert json.loads((r/'export/full-lighting-refresh.json').read_text())['status']=='source_complete'
old_pid=report['pid'];old=subprocess.run(['ps','-p',str(old_pid),'-o','command='],capture_output=True,text=True)
assert old.returncode!=0 or str(r/'validate_lighting.py') not in old.stdout,'Original validator is still live'

def save():
 p=r/'lit-validation.json';t=p.with_suffix('.new');t.write_text(json.dumps(report,indent=2)+'\n');t.replace(p)

def run(name,command,marker,timeout=240):
 phase={'name':name,'status':'running','command':command,'log':str(r/'lit-validation-logs'/(name+'.log'))};report['phases'].append(phase);save()
 with Path(phase['log']).open('w') as stream:
  child=subprocess.Popen(command,cwd=r,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid;save()
  try:phase['exit_code']=child.wait(timeout=timeout)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=15);phase['status']='timeout';save();raise
 text=Path(phase['log']).read_text(errors='replace');assert phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-4000:]
 phase.update(status='passed',log_sha256=sha(Path(phase['log'])));save();print('CORRIDOR_ROOF_RESUMED_LIT_PASS',name,flush=True)

try:
 phase.update(status='passed',log_sha256=sha(Path(phase['log'])),runner_marker_corrected_to='QIUSHUANG_FRAMING_RESULT')
 report.update(status='running',pid=os.getpid(),resume_from_failed_marker_report=str(r/'failed-marker-01/lit-validation.json'));report.pop('error',None);save()
 native=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(game),'--windowed','--resolution','1410x600']
 run('framing_touch',native+['--script','res://tests/test_qiushuang_framing.gd','--','--output='+str(r/'lit-framing-touch'),'--touch'],'QIUSHUANG_FRAMING_RESULT 18 originals; 0 failures')
 for label,args in [('desktop',[]),('portrait',['--mobile'])]:
  run('arrivals_'+label,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--fixed-clock','--output-directory='+str(r/('lit-arrivals-'+label)),*args],'ROUTE_RENDER_SAVED')
 assert len(report['phases'])==15 and all(p['status']=='passed' and p['exit_code']==0 for p in report['phases'])
 report['status']='isolated_lit_views_and_resource_checks_passed_tours_and_direct_review_pending';save();print('CORRIDOR_ROOF_ISOLATED_LIT_CHECKS_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
