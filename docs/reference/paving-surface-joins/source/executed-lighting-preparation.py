"""Package and bake one isolated paving source after independent floor guards."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,sys
repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/paving-site-joins'
root=Path('/tmp/garden-paving-joins-20261010-v4')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
source=load(root/'source-preservation.json')
export=load(root/'export-preservation.json')
audit=load(work/'candidate-paving-audit-v4-normalized.json')
assert audit['status']=='saved_paving_disjoint_and_footprint_preserved' and not audit['positive_coplanar_pairs']
assert audit['before_top_faces']==1142 and audit['analytic_controls_passed']==4
assert audit['candidate_authoring_sha256']==source['candidate_authoring_sha256']==sha(root/'blender/authoring.blend')
assert export['status']=='paving_export_preservation_passed'
assert export['master']['after_sha256']==source['candidate_glb_sha256']==sha(root/'export/garden-of-dreams.glb')
assert sha(repo/'blender/authoring.blend')==source['baseline_authoring_sha256']
assert sha(repo/'export/garden-of-dreams.glb')==export['master']['before_sha256']
assert not (root/'scripts').exists() and not (root/'lighting-preparation.json').exists()
shutil.copytree(repo/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(repo/'textures',root/'textures')
for folder in ['export/lightmaps','blender/sites','blender/kits','lighting-preparation-logs','docs/reference/paving-surface-joins']:
    (root/folder).mkdir(parents=True)
shutil.copyfile(repo/'blender/kits/KIT_water.blend',root/'blender/kits/KIT_water.blend')
shutil.copytree(repo/'export/kits/water',root/'export/kits/water')
shutil.copyfile(repo/'export/site-wash-rig.json',root/'export/site-wash-rig.json')
shutil.copyfile(work/'saved-paving-baseline-normalized.json',root/'docs/reference/paving-surface-joins/saved-paving-baseline-normalized.json')
shutil.copyfile(__file__,root/'executed-lighting-preparation.py')
report={'status':'preparing','root':str(root),'orchestrator_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':source['candidate_glb_sha256'],'authoring_sha256':source['candidate_authoring_sha256'],'phases':[],'scope':'Partitioned visiblefloor source; stairs/cameras/colliders/materials retained. Independent normalized-normal RED84 toGREEN0 floor guard precedes portable15libraries, exact16default exports and six fresh matching source-lighting phases. No canonical adoption/native appearance/phone/full-goal acceptance.'}
def save():
    (root/'lighting-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,command,marker):
    log=root/'lighting-preparation-logs'/(name+'.log')
    phase={'name':name,'command':command,'status':'running','log':str(log)}
    report['phases'].append(phase);save();print('PAVING_SOURCE_START',name,flush=True)
    with log.open('w') as out:
        child=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT)
        phase['pid']=child.pid;save();phase['exit_code']=child.wait()
    text=log.read_text(errors='replace')
    assert phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-3500:]
    phase.update(status='passed',log_sha256=sha(log));save();print('PAVING_SOURCE_PASS',name,flush=True)
try:
    save()
    blender=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1']
    baseline=root/'docs/reference/paving-surface-joins/saved-paving-baseline-normalized.json'
    run('saved-floor-regression',blender+[str(root/'blender/authoring.blend'),'--python',str(root/'scripts/test_saved_paving_surfaces.py'),'--','--baseline',str(baseline),'--output',str(root/'native-saved-floor-green.json')],'SAVED_PAVING_SOURCE_PASS')
    run('water-contract',[sys.executable,str(root/'scripts/verify_water_kit.py')],'WATER_EXPORT_PASS')
    # Invoke the canonical read-only library extractor so its separate-root guard
    # remains intact; execute the root-specific receiver packager from the copy.
    run('site-libraries',blender+['--python',str(repo/'scripts/prepare_candidate_libraries.py'),'--','--root',str(root)],'CANDIDATE_LIBRARIES_PREPARED')
    run('shared-wash-receivers',blender+['--python',str(root/'scripts/package_site_washes.py'),'--','--portable-master'],'SITE_WASH')
    run('default-sixteen-reexports',blender+[str(root/'blender/authoring.blend'),'--python',str(root/'scripts/verify_saved_garden_candidate.py'),'--','--source-root',str(root),'--output-root',str(root/'default-source-reproduction'),'--paving-baseline',str(baseline)],'SAVED_GARDEN_CANDIDATE_PASS')
    assert sha(root/'blender/authoring.blend')==report['authoring_sha256'] and sha(root/'export/garden-of-dreams.glb')==report['source_glb_sha256']
    assert len(list((root/'blender/sites').glob('SITE_*.blend')))==15
    frozen={str(p.relative_to(root)):sha(p) for folder in ['blender','scripts','export/sites','export/kits/water','textures'] for p in sorted((root/folder).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
    for name in ['export/garden-of-dreams.glb','export/site-wash-rig.json','docs/reference/paving-surface-joins/saved-paving-baseline-normalized.json']:
        frozen[name]=sha(root/name)
    assert not any((root/'export/lightmaps').iterdir())
    (root/'full-lighting-inputs.json').write_text(json.dumps({'files':frozen,'empty_lightmaps_before_refresh':True,'scope':'Actual separate saved partitioned floor authoring,15portablelibraries, canonicaldefault16GLBexports and all executed helpers/textures frozen before complete fresh source lighting.'},indent=2)+'\n')
    report['status']='full_source_bake_running';save()
    run('full-lighting',[sys.executable,str(root/'scripts/refresh_full_lighting.py'),'--samples','128','--size','1024'],'FULL_SOURCE_LIGHTING_REFRESH_PASS')
    for name,digest in frozen.items():assert sha(root/name)==digest,name
    assert sha(repo/'blender/authoring.blend')==source['baseline_authoring_sha256']
    assert sha(repo/'export/garden-of-dreams.glb')==export['master']['before_sha256']
    report.update(status='complete_source_lighting_passed_native_review_pending',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print('PAVING_COMPLETE_SOURCE_LIGHTING_PASS',flush=True)
except BaseException as error:
    report.update(status='failed',error=str(error));save();raise
