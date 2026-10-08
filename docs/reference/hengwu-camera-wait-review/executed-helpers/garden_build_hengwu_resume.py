from pathlib import Path
import ast
base=Path('/tmp/garden_review_hengwu_full.py').read_text()
helper=base[base.index('def save():'):base.index('\ntry:\n')]
tail=base[base.index(" cap=ROOT/'review-captures';cap.mkdir()") : base.index('\nexcept BaseException as error:')]
tail=tail.replace(" cap=ROOT/'review-captures';cap.mkdir()"," cap=ROOT/'review-captures-completed-camera-waits';cap.mkdir(exist_ok=False)")
tail=tail.replace("run('hengwu-lit-actions'","run('hengwu-lit-actions-completed'").replace("run('portrait-architecture'","run('portrait-architecture-completed'")
header='''from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys
from datetime import datetime,timezone
REPO=Path('/Users/auchan/projects/garden-of-dreams')
ROOT=Path(json.loads(Path('/tmp/garden-hengwu-full-review.json').read_text())['folder']).resolve()
GD=ROOT/'godot';LOG=ROOT/'review-resume-logs';LOG.mkdir(exist_ok=False)
REPORT=ROOT/'review-resume-pipeline.json'
EXPECTED='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((ROOT/'first-review-pipeline.json').read_text())
assert prior['status']=='failed' and prior['phases'][-1]['name']=='portrait-architecture' and prior['phases'][-1]['exit_code']==1
assert sha(GD/'assets/garden-of-dreams.glb')==EXPECTED
assert sha(GD/'runtime/entry_route.gd')==sha(REPO/'godot/runtime/entry_route.gd')=='db32d9c058a732c330d9df910b22b961f755045c5904c47e8fde68fd3c056138'
for name,digest in prior['runtime_inputs_sha256'].items():
 if name not in ['tests/test_portrait_architecture.gd','tests/render_hengwu_lit_candidate.gd']:assert sha(GD/name)==digest,name
reused=[]
for phase in prior['phases']:
 if phase['status']=='passed' and phase['name']!='hengwu-lit-actions':
  assert sha(phase['log'])==phase['log_sha256'];reused.append(phase)
assert len(reused)==28
report={'status':'running','source_glb_sha256':EXPECTED,'orchestrator_pid':os.getpid(),'started_at':datetime.now(timezone.utc).isoformat(),'root':str(ROOT),'first_review_report':str(ROOT/'first-review-pipeline.json'),'reused_completed_checks':reused,'invalidated_first_capture_report':str(ROOT/'first-lit-capture-pose-rejection.json'),'updated_test_inputs_sha256':{name:sha(GD/name) for name in ['tests/test_portrait_architecture.gd','tests/render_hengwu_lit_candidate.gd']},'phases':[],'scope':'Resume after a terminal native test failure. Runtime/source unchanged; test waits now use actual camera tween completion with timeout. Original failure and six rejected partial action captures are retained. Completed source/import/lighting/library/reexport/memory checks are reused after verifying their original logs. Final art, devices, references, release and services remain open.'}
godot='/Applications/Godot.app/Contents/MacOS/Godot';head=[godot,'--headless','--path',str(GD)];native=[godot,'--path',str(GD)]
'''
script=header+helper+'\ntry:\n shutil.copy2(__file__,ROOT/"executed-review-resume.py")\n save()\n'+tail+'\nexcept BaseException as error:\n report["status"]="failed";report["error"]=str(error);save();raise\n'
ast.parse(script);Path('/tmp/garden_resume_hengwu_full.py').write_text(script)
print('HENGWU_REVIEW_RESUME_PREPARED')
