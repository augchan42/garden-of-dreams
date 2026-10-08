from pathlib import Path
import hashlib,json,shutil,tempfile,subprocess,sys,re,datetime,os
repo=Path('/Users/auchan/projects/garden-of-dreams')
ex=Path(json.loads(Path('/tmp/garden-oux-default-export.json').read_text())['folder']).resolve()
root=Path(tempfile.mkdtemp(prefix='garden-oux-full-source-')).resolve();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected='be80374cbc0959830205af0efbe198f044ec25df15e7933c91178d0ecf516e5a';author='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c'
assert sha(ex/'export/garden-of-dreams.glb')==expected and sha(repo/'blender/authoring.blend')==author
r=json.loads((ex/'native-export-verification.json').read_text());assert r['status']=='native_default_and_disabled_exports_verified'
shutil.copytree(repo/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
(root/'blender/sites').mkdir(parents=True);shutil.copy2(repo/'blender/authoring.blend',root/'blender/authoring.blend')
shutil.copytree(ex/'export',root/'export')
assert not (root/'export/lightmaps').exists();(root/'export/lightmaps').mkdir()
shutil.copy2(repo/'export/site-wash-rig.json',root/'export/site-wash-rig.json')
# The extraction wrapper resolves helpers and rig data inside this frozen tree.
prepare=(repo/'scripts/prepare_candidate_libraries.py').read_text()
prepare=prepare.replace("assert root!=repo and repo not in root.parents,'Use a separate candidate tree'","assert root==repo and root!=Path('/Users/auchan/projects/garden-of-dreams'), 'Frozen separate source only'")
(root/'scripts/prepare_candidate_libraries_frozen.py').write_text(prepare)
(root/'preparation-logs').mkdir()
report={'status':'running','source_glb_sha256':expected,'authoring_sha256':author,'phases':[],'orchestrator_pid':os.getpid(),'scope':'New complete Ouxiang UV2 source; original saved geometry retained, empty lightmaps before fresh all-scene baking. No new GLB/map install.'}
def save():(root/'source-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
Path('/tmp/garden-oux-full-source.json').write_text(json.dumps({'folder':str(root),'source_glb_sha256':expected,'authoring_sha256':author},indent=2)+'\n')
save()
try:
 for label,script,args in [('site-libraries',root/'scripts/prepare_candidate_libraries_frozen.py',['--root',str(root)]),('wash-receivers',root/'scripts/package_site_washes.py',['--portable-master'])]:
  cmd=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1','--python',str(script),'--',*args]
  log=root/'preparation-logs'/(label+'.log');row={'name':label,'command':cmd,'status':'running','log':str(log)};report['phases'].append(row);save()
  with log.open('w') as out:
   p=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,cwd=root);row['pid']=p.pid;save();row['exit_code']=p.wait()
  row['log_sha256']=sha(log);save();text=log.read_text(errors='replace')
  assert row['exit_code']==0 and not re.search(r'(?m)^(?:Error:|Traceback)',text),text[-4000:]
  row['status']='passed';save()
 assert sha(root/'blender/authoring.blend')==author and sha(root/'export/garden-of-dreams.glb')==expected
 assert len(list((root/'blender/sites').glob('SITE_*.blend')))==15
 freeze={'source_glb_sha256':expected,'authoring_sha256':author,'site_glbs':{p.name:sha(p) for p in sorted((root/'export/sites').glob('*.glb'))},'master_sha256':sha(root/'blender/master.blend'),'site_libraries':{p.name:sha(p) for p in sorted((root/'blender/sites').glob('SITE_*.blend'))},'scripts':{str(p.relative_to(root)):sha(p) for p in sorted((root/'scripts').rglob('*')) if p.is_file()},'source_preparation_sha256_pending':True,'empty_lightmaps_before_refresh':not any((root/'export/lightmaps').iterdir())}
 assert freeze['empty_lightmaps_before_refresh']
 report['status']='prepared_frozen_complete_source';save();freeze.pop('source_preparation_sha256_pending');freeze['source_preparation_sha256']=sha(root/'source-preparation.json')
 (root/'full-refresh-inputs.json').write_text(json.dumps(freeze,indent=2)+'\n')
 print('OUX_FULL_SOURCE_PREPARED',root,flush=True)
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
