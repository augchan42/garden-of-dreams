"""Run two actual native full-garden tours only after complete source and native gates."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,default=Path('/tmp/garden-corridor-roof-full-20261011'))
a=p.parse_args();root=a.root;game=root/'godot'
expected='7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Preflight everything before creating reports/directories or native children.
for name,status in [('lighting-preparation.json','complete_roof_source_lighting_passed_native_review_pending'),('export/full-lighting-refresh.json','source_complete'),('lit-validation.json','isolated_lit_views_and_resource_checks_passed_tours_and_direct_review_pending'),('native-lit-file-verification.json','passed'),('canonical-replay.json','passed')]:
 path=root/name
 if not path.exists() or json.loads(path.read_text()).get('status')!=status:
  raise RuntimeError('Incomplete source/native gates; no tour launched: '+name)
assert sha(root/'export/garden-of-dreams.glb')==sha(game/'assets/garden-of-dreams.glb')==expected
assert json.loads((root/'native-lit-file-verification.json').read_text())['source_glb_sha256']==expected
assert json.loads((root/'native-lit-file-verification.json').read_text())['decoded_and_verified_png']==78
for name,digest in json.loads((root/'full-lighting-inputs.json').read_text())['files'].items():assert sha(root/name)==digest,name
assert not (root/'tour-jobs.json').exists(),'Resume the recorded process rather than start another tour'
report={'status':'running','orchestrator_pid':os.getpid(),'source_glb_sha256':expected,'phases':[],'scope':'Actual native fourteen-room/twenty-six-leg public-command physics/camera/lighting route, desktop and portrait; not phone, sustained performance or final art acceptance.'}
def save():(root/'tour-jobs.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 save()
 for shape,args in [('desktop',[]),('portrait',['--portrait'])]:
  folder=root/('lit-tour-'+shape);folder.mkdir();log=root/('lit-tour-'+shape+'.log')
  command=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/render_full_garden_traversal.gd','--','--output='+str(folder/'report.json'),'--capture-directory='+str(folder/'captures'),*args]
  phase={'shape':shape,'status':'running','command':command,'log':str(log)};report['phases'].append(phase);save();print('CORRIDOR_ROOF_NATIVE_TOUR_START',shape,flush=True)
  with log.open('w') as stream:
   child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid;save()
   try:phase['exit_code']=child.wait(timeout=1500)
   except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=15);phase['status']='timeout';save();raise
  text=log.read_text(errors='replace')
  assert phase['exit_code']==0 and 'FULL_GARDEN_TRAVERSAL_PASS rooms=14 legs=26' in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|Traceback)|AssertionError:',text),text[-4000:]
  result=json.loads((folder/'report.json').read_text())
  assert result['status']=='passed' and len(result['legs'])==26 and len(result['visited_rooms'])==14 and not result['floor_failures']
  assert result['source_glb_sha256']==expected and result['maximum_practicals']<=4 and len(result['settled_arrivals'])==26
  phase.update(status='passed',log_sha256=sha(log));save();print('CORRIDOR_ROOF_NATIVE_TOUR_PASS',shape,flush=True)
 report['status']='both_native_full_tours_passed';save()
except BaseException as error:report.update(status='failed',error=str(error));save();raise
