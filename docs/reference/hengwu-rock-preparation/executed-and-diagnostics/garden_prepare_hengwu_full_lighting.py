from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,sys
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path(json.loads(Path('/tmp/garden-hengwu-compact-rock.json').read_text())['root']).resolve()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert json.loads((root/'export-preservation.json').read_text())['status']=='controlled_hengwu_rock_export_preserved'
assert json.loads((root/'native-physics-review/report.json').read_text())['status']=='native_compact_collider_and_adjacent_route_checks_passed'
assert json.loads((root/'native-geometry-review-actions-settled/report.json').read_text())['status']=='unbaked_native_comparison_phases_passed'
assert not (root/'scripts').exists();shutil.copytree(repo/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
(root/'export/lightmaps').mkdir();(root/'blender/sites').mkdir();(root/'lighting-preparation-logs').mkdir()
shutil.copyfile(repo/'export/site-wash-rig.json',root/'export/site-wash-rig.json')
# The copied helper runs inside the isolated root rather than its source repo.
p=root/'scripts/prepare_candidate_libraries.py';original=sha(p);s=p.read_text().replace("assert root!=repo and repo not in root.parents,'Use a separate candidate tree'", "assert root==repo and root!=Path('/Users/auchan/projects/garden-of-dreams'), 'Frozen separate source only'");p.write_text(s)
report={'status':'preparing','root':str(root),'orchestrator_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':sha(root/'export/garden-of-dreams.glb'),'authoring_sha256':sha(root/'blender/authoring.blend'),'library_helper_original_sha256':original,'library_helper_frozen_sha256':sha(p),'phases':[],'scope':'Separate saved-source libraries/shared receiver packaging and complete fresh six-phase lighting for compact Hengwu stone. No production adoption; final art, cameras, all native rendered checks and full goal requirements remain open.'}
def save():(root/'lighting-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,cmd,marker):
 log=root/'lighting-preparation-logs'/(name+'.log');phase={'name':name,'command':cmd,'status':'running','log':str(log)};report['phases'].append(phase);save();print('HENGWU_SOURCE_PHASE_START',name,flush=True)
 with log.open('w') as f:
  child=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 txt=log.read_text(errors='replace');assert phase['exit_code']==0 and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',txt),txt[-4000:];assert marker in txt,txt[-4000:]
 phase['status']='passed';phase['log_sha256']=sha(log);save();print('HENGWU_SOURCE_PHASE_PASS',name,flush=True)
try:
 native=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1','--python']
 run('site-libraries',native+[str(root/'scripts/prepare_candidate_libraries.py'),'--','--root',str(root)],'CANDIDATE_LIBRARIES_PREPARED')
 run('shared-wash-receivers',native+[str(root/'scripts/package_site_washes.py'),'--','--portable-master'],'SITE_WASH')
 assert sha(root/'blender/authoring.blend')==report['authoring_sha256'] and sha(root/'export/garden-of-dreams.glb')==report['source_glb_sha256']
 assert len(list((root/'blender/sites').glob('SITE_*.blend')))==15
 freeze={str(p.relative_to(root)):sha(p) for folder in ['blender','scripts','export/sites'] for p in sorted((root/folder).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
 freeze['export/garden-of-dreams.glb']=sha(root/'export/garden-of-dreams.glb');freeze['export/site-wash-rig.json']=sha(root/'export/site-wash-rig.json')
 assert not any((root/'export/lightmaps').iterdir());(root/'full-lighting-inputs.json').write_text(json.dumps({'files':freeze,'empty_lightmaps_before_refresh':True,'scope':'Frozen saved authoring/libraries/master, all source GLBs and executed helpers for full current-source lighting.'},indent=2)+'\n')
 report['status']='full_source_bake_running';save()
 run('full-lighting',[sys.executable,str(root/'scripts/refresh_full_lighting.py'),'--samples','128','--size','1024'],'FULL_SOURCE_LIGHTING_REFRESH_PASS')
 for name,h in freeze.items():assert sha(root/name)==h,name
 report['status']='complete_source_lighting_passed_native_review_pending';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('HENGWU_COMPLETE_SOURCE_LIGHTING_PASS',root,flush=True)
except BaseException as e:report['status']='failed';report['error']=str(e);save();raise
