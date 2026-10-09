"""Continue the failed output-location guard without rerunning completed source phases."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,sys
repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/paving-site-joins'
root=Path('/tmp/garden-paving-joins-20261010-v4')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
source=load(root/'source-preservation.json');export=load(root/'export-preservation.json')
old=load(root/'lighting-preparation.json')
assert old['status']=='failed' and len(old['phases'])==5
assert [p['name'] for p in old['phases'][:4]]==['saved-floor-regression','water-contract','site-libraries','shared-wash-receivers']
assert all(p['status']=='passed' and p['exit_code']==0 for p in old['phases'][:4])
assert old['phases'][4]['exit_code']==1 and 'not output.is_relative_to(source)' in old['error']
for pid in [old['orchestrator_pid'],*[p['pid'] for p in old['phases']]]:
    try:os.kill(pid,0)
    except ProcessLookupError:continue
    raise AssertionError(('Prior worker still alive',pid))
for phase in old['phases'][:4]:assert sha(phase['log'])==phase['log_sha256']
assert sha(root/'blender/authoring.blend')==source['candidate_authoring_sha256']
assert sha(root/'export/garden-of-dreams.glb')==source['candidate_glb_sha256']
assert not (root/'lighting-preparation-failed-output-root.json').exists()
shutil.copyfile(root/'lighting-preparation.json',root/'lighting-preparation-failed-output-root.json')
report={k:v for k,v in old.items() if k not in ['error','phases']}
report.update(status='continuing_default_export_location_guard',orchestrator_pid=os.getpid(),continued_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),prior_failure_report='lighting-preparation-failed-output-root.json',phases=old['phases'][:4])
shutil.copyfile(__file__,root/'executed-lighting-continuation.py')
def save():
    (root/'lighting-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,command,marker):
    log=root/'lighting-preparation-logs'/(name+'-continuation.log')
    assert not log.exists()
    phase={'name':name,'command':command,'status':'running','log':str(log)}
    report['phases'].append(phase);save();print('PAVING_SOURCE_START',name,flush=True)
    with log.open('w') as out:
        child=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT)
        phase['pid']=child.pid;save();phase['exit_code']=child.wait()
    text=log.read_text(errors='replace')
    passed=phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text)
    phase.update(status='passed' if passed else 'failed',log_sha256=sha(log));save()
    assert passed,text[-3500:]
    print('PAVING_SOURCE_PASS',name,flush=True)
blender=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1']
baseline=root/'docs/reference/paving-surface-joins/saved-paving-baseline-normalized.json'
try:
    save()
    run('default-sixteen-reexports',blender+[str(root/'blender/authoring.blend'),'--python',str(root/'scripts/verify_saved_garden_candidate.py'),'--','--source-root',str(root),'--output-root',str(Path('/tmp/garden-paving-joins-20261010-v4-default-reproduction')),'--paving-baseline',str(baseline)],'SAVED_GARDEN_CANDIDATE_PASS')
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
