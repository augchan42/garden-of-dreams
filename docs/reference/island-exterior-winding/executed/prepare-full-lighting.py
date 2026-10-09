from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,sys
repo=Path('/Users/auchan/projects/garden-of-dreams')
w=repo/'.superpowers/sdd/2026-09-23-garden-completion/island-face-source';root=w/'candidate'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert json.loads((root/'export-preservation.json').read_text())['status']=='island_winding_export_preservation_passed'
assert json.loads((w/'shell-contract-red.json').read_text())['status']=='saved_island_shell_rejected'
assert json.loads((w/'shell-contract-green.json').read_text())['status']=='saved_island_shell_passed'
assert json.loads((w/'native-probe/pipeline.json').read_text())['status']=='unbaked_native_probe_complete_original_visual_review_pending'
assert json.loads((w/'native-probe/direct-original-review.json').read_text())['status']=='unbaked_native_probe_reviewed_fresh_baked_comparison_required'
assert not (root/'scripts').exists()
shutil.copytree(repo/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(w/'test_saved_island_shell.py',root/'scripts/test_saved_island_shell.py')
p=root/'scripts/refine_western_sites.py'
old='[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],stone)'
new='[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)],stone)'
assert p.read_text().count(old)==1
p.write_text(p.read_text().replace(old,new))
(root/'export/lightmaps').mkdir();(root/'blender/sites').mkdir();(root/'blender/kits').mkdir();(root/'lighting-preparation-logs').mkdir()
shutil.copyfile(repo/'blender/kits/KIT_water.blend',root/'blender/kits/KIT_water.blend')
shutil.copytree(repo/'export/kits/water',root/'export/kits/water')
shutil.copyfile(repo/'export/site-wash-rig.json',root/'export/site-wash-rig.json')
p=root/'scripts/prepare_candidate_libraries.py';original=sha(p)
p.write_text(p.read_text().replace("assert root!=repo and repo not in root.parents,'Use a separate candidate tree'", "assert root==repo and root==Path('/Users/auchan/projects/garden-of-dreams/.superpowers/sdd/2026-09-23-garden-completion/island-face-source/candidate'), 'This frozen isolated source only'"))
report={'status':'preparing','root':str(root),'orchestrator_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':sha(root/'export/garden-of-dreams.glb'),'authoring_sha256':sha(root/'blender/authoring.blend'),'library_helper_original_sha256':original,'library_helper_frozen_sha256':sha(p),'phases':[],'scope':'Separate saved source with24 corrected island exterior windings and all other4466 objects preserved. Complete15libraries/shared receiver packaging and six fresh lighting phases. Same124 receiver eligibility and water kit. No canonical adoption, native matched-lit appearance, phone or full-goal acceptance.'}
def save():(root/'lighting-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,cmd,marker):
 log=root/'lighting-preparation-logs'/(name+'.log');phase={'name':name,'command':cmd,'status':'running','log':str(log)};report['phases'].append(phase);save();print('ISLAND_SOURCE_PHASE_START',name,flush=True)
 with log.open('w') as out:
  child=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT);phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 txt=log.read_text(errors='replace');assert phase['exit_code']==0 and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',txt),txt[-4000:];assert marker in txt,txt[-4000:]
 phase.update(status='passed',log_sha256=sha(log));save();print('ISLAND_SOURCE_PHASE_PASS',name,flush=True)
try:
 run('water-contract',[sys.executable,str(root/'scripts/verify_water_kit.py')],'WATER_EXPORT_PASS')
 native=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1','--python']
 run('site-libraries',native+[str(root/'scripts/prepare_candidate_libraries.py'),'--','--root',str(root)],'CANDIDATE_LIBRARIES_PREPARED')
 run('shared-wash-receivers',native+[str(root/'scripts/package_site_washes.py'),'--','--portable-master'],'SITE_WASH')
 assert sha(root/'blender/authoring.blend')==report['authoring_sha256'] and sha(root/'export/garden-of-dreams.glb')==report['source_glb_sha256']
 assert len(list((root/'blender/sites').glob('SITE_*.blend')))==15
 freeze={str(p.relative_to(root)):sha(p) for folder in ['blender','scripts','export/sites','export/kits/water'] for p in sorted((root/folder).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
 freeze['export/garden-of-dreams.glb']=sha(root/'export/garden-of-dreams.glb');freeze['export/site-wash-rig.json']=sha(root/'export/site-wash-rig.json')
 assert not any((root/'export/lightmaps').iterdir())
 (root/'full-lighting-inputs.json').write_text(json.dumps({'files':freeze,'empty_lightmaps_before_refresh':True,'scope':'Frozen repaired saved authoring/current water kit/libraries/master, all scene/module exports and executed helpers before full fresh lighting.'},indent=2)+'\n')
 report['status']='full_source_bake_running';save()
 run('full-lighting',[sys.executable,str(root/'scripts/refresh_full_lighting.py'),'--samples','128','--size','1024'],'FULL_SOURCE_LIGHTING_REFRESH_PASS')
 for name,h in freeze.items():assert sha(root/name)==h,name
 report.update(status='complete_source_lighting_passed_native_review_pending',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print('ISLAND_COMPLETE_SOURCE_LIGHTING_PASS',root,flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
