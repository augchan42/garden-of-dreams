from pathlib import Path
import hashlib,json,subprocess,os,re
from datetime import datetime,timezone
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path(json.loads(Path('/tmp/garden-oux-default-export.json').read_text())['folder']).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected_author='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c';old='361a67c759974e4fb5897a15d5a7354076ef30392b7a6ed988cca6029f198611';new='be80374cbc0959830205af0efbe198f044ec25df15e7933c91178d0ecf516e5a'
assert sha(repo/'blender/authoring.blend')==expected_author and sha(repo/'export/garden-of-dreams.glb')==old
report={'status':'running','orchestrator_pid':os.getpid(),'started_at':datetime.now(timezone.utc).isoformat(),'source_authoring_sha256':expected_author,'phases':[],'scope':'Native default Ouxiang UV2 export and disabled-option control. Saved authoring unchanged; geometry/light/camera/material/image equivalence and expected complete/site attributes are separate assertions. No bake or production install.'}
logs=root/'native-logs';logs.mkdir()
def save():(root/'native-export-verification.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 blender='/Applications/Blender.app/Contents/MacOS/Blender'
 for mode,args in [('default',[]),('disabled',['--no-ouxiang-tile-uvs'])]:
  out=root if mode=='default' else root/'disabled-control'
  log=logs/(mode+'.log');command=[blender,'--background',str(repo/'blender/authoring.blend'),'--python-exit-code','1','--python',str(root/'scripts/export_garden.py'),'--','--output-root',str(out),*args]
  row={'name':mode,'command':command,'log':str(log),'status':'running'};report['phases'].append(row);save();print('OUX_EXPORT_START',mode,flush=True)
  with log.open('w') as stream:
   child=subprocess.Popen(command,cwd=repo,stdout=stream,stderr=subprocess.STDOUT);row['pid']=child.pid;save();row['exit_code']=child.wait()
  row['log_sha256']=sha(log);save();text=log.read_text(errors='replace')
  assert row['exit_code']==0 and not re.search(r'(?m)^(?:Traceback|ERROR:|.*AssertionError)',text),(mode,text[-5000:])
  actual=sha(out/'export/garden-of-dreams.glb');row['complete_glb_sha256']=actual;save()
  assert actual==(new if mode=='default' else old),(mode,'whole-source hash mismatch',actual)
  row['site_hashes']={}
  for path in sorted((repo/'export/sites').glob('*.glb')):
   output=out/'export/sites'/path.name
   if mode=='disabled' or path.name!='SITE_ouxiang-xie.glb':assert sha(path)==sha(output),path.name
   row['site_hashes'][path.name]=sha(output)
  assert len(row['site_hashes'])==15
  assert sha(repo/'blender/authoring.blend')==expected_author
  row['status']='passed';save();print('OUX_EXPORT_PASS',mode,actual,flush=True)
 report['status']='native_default_and_disabled_exports_verified';report['finished_at']=datetime.now(timezone.utc).isoformat();save();print('OUX_NATIVE_EXPORT_VERIFIED',root,flush=True)
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
