"""Package the current ground candidate without starting another lighting job."""
from pathlib import Path
import hashlib, json, os, re, subprocess

r = Path(__file__).resolve().parent
repo = Path('/Users/auchan/projects/garden-of-dreams')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((r/'export-pipeline.json').read_text())['status'] == 'source_export_uv_passed_lighting_native_review_pending'
assert json.loads((r/'canonical-replay.json').read_text())['status'] == 'canonical_replay_16_glbs_byte_exact'
assert sha(r/'blender/authoring.blend') == '9b6c83259f79aeb56bbdc67b1fd939b2e9ff69977bcb941cb8141b2ce329b66e'
assert sha(r/'export/garden-of-dreams.glb') == '09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290'
assert sha(repo/'scripts/prepare_candidate_libraries.py') == sha(r/'scripts/prepare_candidate_libraries.py')
assert not (r/'library-preparation.json').exists(), 'Inspect the same job instead of duplicating it'
(r/'blender/sites').mkdir()
report = {'status':'running', 'pid':os.getpid(), 'phases':[], 'authoring_sha256':sha(r/'blender/authoring.blend'),
          'source_glb_sha256':sha(r/'export/garden-of-dreams.glb'),
          'scope':'Independent candidate source libraries and shared wash receiver packaging only. No new bake, production change, editor or device action.'}

def save():
    p=r/'library-preparation.json';t=p.with_suffix('.new');t.write_text(json.dumps(report,indent=2)+'\n');t.replace(p)

def run(name,command,marker):
    phase={'name':name,'status':'running','command':command,'log':str(r/(name+'.log'))};report['phases'].append(phase);save()
    with Path(phase['log']).open('w') as stream:
        child=subprocess.Popen(command,cwd=r,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid;save();phase['exit_code']=child.wait()
    text=Path(phase['log']).read_text(errors='replace')
    assert phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-3000:]
    assert sha(r/'blender/authoring.blend')==report['authoring_sha256'] and sha(r/'export/garden-of-dreams.glb')==report['source_glb_sha256']
    phase.update(status='passed',log_sha256=sha(Path(phase['log'])));save();print('AOJING_LIBRARY_PHASE_PASS',name,flush=True)

blender=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','1','--python-exit-code','1']
try:
    save()
    run('site-libraries',blender+['--python',str(repo/'scripts/prepare_candidate_libraries.py'),'--','--root',str(r)],'CANDIDATE_LIBRARIES_PREPARED')
    run('shared-wash-receivers',blender+['--python',str(r/'scripts/package_site_washes.py'),'--','--portable-master'],'LINKED_MASTER_WASH_PASS')
    run('linked-ground-library',blender+[str(r/'blender/master.blend'),'--python',str(r/'test_ground_library.py')],'AOJING_LINKED_GROUND_LIBRARY_PASS')
    frozen={str(p.relative_to(r)):sha(p) for p in (r/'blender').rglob('*.blend')}
    frozen['export/site-wash-rig.json']=sha(r/'export/site-wash-rig.json')
    report.update(status='candidate_source_libraries_passed_fresh_lighting_pending',files=frozen);save();print('AOJING_CANDIDATE_LIBRARIES_PASS',flush=True)
except BaseException as error:
    report.update(status='failed',error=str(error));save();raise
