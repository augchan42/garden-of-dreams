"""Package current candidate source and run six fresh lighting phases."""
from pathlib import Path
import json,hashlib,subprocess,sys,re,os
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path('/tmp/garden-qiushuang-lattice-20261010')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((root/'export-preservation.json').read_text())['status']=='lattice_export_preservation_passed'
assert not (root/'lighting-preparation.json').exists()
(root/'lighting-preparation-logs').mkdir();(root/'export/lightmaps').mkdir()
report={'status':'running','orchestrator_pid':os.getpid(),'authoring_sha256':sha(root/'blender/authoring.blend'),'source_glb_sha256':sha(root/'export/garden-of-dreams.glb'),'phases':[]}
def save():(root/'lighting-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,command,marker):
 log=root/'lighting-preparation-logs'/(name+'.log');phase={'name':name,'command':command,'status':'running','log':str(log)};report['phases'].append(phase);save();print('QIUSHUANG_START',name,flush=True)
 with log.open('w') as stream:
  child=subprocess.Popen(command,cwd=root,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 text=log.read_text(errors='replace');assert phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-3500:]
 phase.update(status='passed',log_sha256=sha(log));save();print('QIUSHUANG_PASS',name,flush=True)
blender=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1','--python']
try:
 save();run('site-libraries',blender+[str(repo/'scripts/prepare_candidate_libraries.py'),'--','--root',str(root)],'CANDIDATE_LIBRARIES_PREPARED')
 run('shared-wash-receivers',blender+[str(root/'scripts/package_site_washes.py'),'--','--portable-master'],'SITE_WASH')
 assert sha(root/'blender/authoring.blend')==report['authoring_sha256'];assert sha(root/'export/garden-of-dreams.glb')==report['source_glb_sha256']
 frozen={str(p.relative_to(root)):sha(p) for folder in ['blender','scripts','export/sites','export/kits'] for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p)}
 for name in ['export/garden-of-dreams.glb','export/site-wash-rig.json']:frozen[name]=sha(root/name)
 assert not any((root/'export/lightmaps').iterdir())
 (root/'full-lighting-inputs.json').write_text(json.dumps({'files':frozen,'empty_lightmaps_before_refresh':True},indent=2)+'\n')
 run('full-lighting',[sys.executable,str(root/'scripts/refresh_full_lighting.py'),'--samples','128','--size','1024'],'FULL_SOURCE_LIGHTING_REFRESH_PASS')
 for name,h in frozen.items():assert sha(root/name)==h,name
 report['status']='complete_lattice_source_lighting_passed_native_review_pending';save();print('QIUSHUANG_COMPLETE_SOURCE_LIGHTING_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
