"""Prepare and bake the complete isolated paving + plain-material revision."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,sys,tempfile
repo=Path('/Users/auchan/projects/garden-of-dreams')
path=Path(json.load(open('/tmp/garden-nunnery-path-candidate.json'))['folder']).resolve()
root=Path(tempfile.mkdtemp(prefix='garden-neutral-path-full-source-')).resolve()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert json.load(open(path/'native-control-pipeline.json'))['status']=='native_captures_complete_visual_review_pending'
assert json.load(open(path/'native-paving-verification.json'))['status']=='native_controlled_paving_repair_verified_full_adoption_pending'
assert json.load(open(path/'export-preservation.json'))['after_sha256']==sha(path/'export/garden-of-dreams.glb')
shutil.copytree(repo/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
(root/'export/lightmaps').mkdir(parents=True);(root/'preparation-logs').mkdir()
shutil.copy2(repo/'export/site-wash-rig.json',root/'export/site-wash-rig.json')
report={'status':'preparing','folder':str(root),'orchestrator_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':[],'scope':'Isolated complete-source paving and four neutral plain-material changes, fresh all-scene lighting. No production scene/map adoption; atlas/final art/device/budgets/services remain open.'}
def save():(root/'source-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
pointer=Path('/tmp/garden-neutral-path-full-source.json');pointer.write_text(json.dumps({'folder':str(root),'orchestrator_pid':os.getpid(),'report':str(root/'source-preparation.json')},indent=2)+'\n');save()
def run(name,cmd,marker=None):
 log=root/'preparation-logs'/(name+'.log');phase={'name':name,'command':cmd,'status':'running','log':str(log)};report['phases'].append(phase);save();print('NEUTRAL_PATH_PHASE_START',name,flush=True)
 with log.open('w') as out:
  child=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT);phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 phase['log_sha256']=sha(log);txt=log.read_text(errors='replace')
 assert phase['exit_code']==0 and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',txt),txt[-4000:]
 if marker:assert marker in txt,txt[-4000:]
 phase['status']='passed';save();print('NEUTRAL_PATH_PHASE_PASS',name,flush=True)
try:
 blender='/Applications/Blender.app/Contents/MacOS/Blender';native=[blender,'--background','--threads','8','--python-exit-code','1','--python']
 run('material-source-export',[blender,'--background',str(path/'blender/authoring.blend'),'--python-exit-code','1','--python',str(root/'scripts/apply_garden_material_palette.py'),'--','--output-root',str(root)],'GARDEN_NEUTRAL_MATERIAL_SOURCE_PASS')
 run('palette-export-preservation',[sys.executable,str(root/'scripts/verify_garden_palette_export.py'),'--before',str(path/'export/garden-of-dreams.glb'),'--after',str(root/'export/garden-of-dreams.glb'),'--output',str(root/'export/palette-export-preservation.json')],'GARDEN_PALETTE_EXPORT_PRESERVATION_PASS')
 sourcehash=sha(root/'export/garden-of-dreams.glb');authorhash=sha(root/'blender/authoring.blend');report.update(source_glb_sha256=sourcehash,authoring_sha256=authorhash);save()
 text=(root/'scripts/prepare_candidate_libraries.py').read_text();text=text.replace("assert root!=repo and repo not in root.parents,'Use a separate candidate tree'","assert root==repo and root!=Path('/Users/auchan/projects/garden-of-dreams'), 'Frozen separate source only'")
 (root/'scripts/prepare_candidate_libraries_frozen.py').write_text(text)
 run('site-libraries',native+[str(root/'scripts/prepare_candidate_libraries_frozen.py'),'--','--root',str(root)],'CANDIDATE_LIBRARIES_PREPARED')
 run('wash-receivers',native+[str(root/'scripts/package_site_washes.py'),'--','--portable-master'],'SITE_WASH')
 assert sha(root/'blender/authoring.blend')==authorhash and sha(root/'export/garden-of-dreams.glb')==sourcehash
 assert len(list((root/'blender/sites').glob('SITE_*.blend')))==15
 freeze={'source_glb_sha256':sourcehash,'authoring_sha256':authorhash,'site_glbs':{p.name:sha(p) for p in sorted((root/'export/sites').glob('*.glb'))},'master_sha256':sha(root/'blender/master.blend'),'site_libraries':{p.name:sha(p) for p in sorted((root/'blender/sites').glob('*.blend'))},'scripts':{str(p.relative_to(root)):sha(p) for p in sorted((root/'scripts').rglob('*')) if p.is_file()},'empty_lightmaps_before_refresh':not any((root/'export/lightmaps').iterdir()),'paving_evidence_sha256':sha(repo/'export/nunnery-path-repair-evidence.json'),'palette_preview_evidence_sha256':sha(repo/'export/neutral-material-preview-evidence.json'),'palette_application_sha256':sha(root/'material-palette-application.json'),'palette_export_preservation_sha256':sha(root/'export/palette-export-preservation.json')}
 assert freeze['empty_lightmaps_before_refresh']
 report['status']='prepared_frozen_complete_source';save();freeze['source_preparation_sha256']=sha(root/'source-preparation.json');(root/'full-refresh-inputs.json').write_text(json.dumps(freeze,indent=2)+'\n')
 report['status']='full_source_bake_running';save()
 run('full-lighting',[sys.executable,str(root/'scripts/refresh_full_lighting.py'),'--samples','128','--size','1024'],'FULL_SOURCE_LIGHTING_REFRESH_PASS')
 assert sha(root/'blender/authoring.blend')==authorhash and sha(root/'export/garden-of-dreams.glb')==sourcehash
 report['status']='complete_source_bake_passed_native_review_pending';save();print('NEUTRAL_PATH_FULL_SOURCE_COMPLETE',root,flush=True)
except BaseException as e:report['status']='failed';report['error']=str(e);save();raise
