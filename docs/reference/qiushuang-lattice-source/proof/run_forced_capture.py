"""Retry only the stalled native capture after all other native jobs finish."""
from pathlib import Path
import hashlib,json,shutil,subprocess,re,os
r=Path('/tmp/garden-qiushuang-lattice-20261010');repo=Path('/Users/auchan/projects/garden-of-dreams');game=repo/'godot'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=json.loads((r/'installed-validation.json').read_text())
assert original['status']=='failed' and len(original['phases'])==16
assert all(p['status']=='passed' for p in original['phases'][:-1])
assert original['phases'][-1]['name']=='native_lattice' and original['phases'][-1]['exit_code']==1
assert json.loads((r/'android-full-build.json').read_text())['status']=='built'
assert not (r/'installed-capture-forced.json').exists()
report={'status':'running','pid':os.getpid(),'source_glb_sha256':original['source_glb_sha256'],'first_attempt':'installed-validation.json','reason':'Two retries and an instrumented trace reach the unchanged 150-second deadline while awaiting a new automatic frame_post_draw. The fixture now calls RenderingServer.force_draw(false) before native image readback. Product source/runtime and deadline stay unchanged; all eight images must remain byte-exact.'}
def save():(r/'installed-capture-forced.json').write_text(json.dumps(report,indent=2)+'\n')
helper=game/'tests/capture_lattice_forced.gd';assert not helper.exists()
shutil.copy2(r/'capture_lattice_forced.gd',helper);save()
command=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/capture_lattice_forced.gd','--','--output='+str(r/'installed-native-qiushuang-v3')]
log=r/'installed-capture-forced.log'
try:
 with log.open('w') as stream:
  child=subprocess.Popen(command,cwd=repo,stdout=stream,stderr=subprocess.STDOUT);report['child_pid']=child.pid;save()
  try:report['exit_code']=child.wait(timeout=210)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=15);raise
 text=log.read_text();assert report['exit_code']==0 and 'QIUSHUANG_LATTICE_LIT_PASS' in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:)',text),text[-2500:]
 count=0
 for p in (r/'installed-native-qiushuang-v3').glob('*.png'):
  assert p.read_bytes()==(r/'native-lit-qiushuang'/p.name).read_bytes(),p.name;count+=1
 assert count==8
 report.update(status='passed',installed_originals_exact_to_candidate=count,log_sha256=sha(log));save()
 completed={**original,'status':'installed_canonical_source_and_engine_checks_passed','phases':original['phases'][:-1]+[{'name':'native_lattice_explicit_draw','status':'passed','exit_code':0,'log':str(log),'log_sha256':sha(log)}],'failed_first_attempt':'installed-validation.json','serial_retry':'installed-capture-forced.json','installed_originals_exact_to_candidate':count}
 (r/'installed-validation-completed.json').write_text(json.dumps(completed,indent=2)+'\n')
 print('QIUSHUANG_INSTALLED_FORCED_CAPTURE_PASS',count,flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
finally:helper.unlink(missing_ok=True);Path(str(helper)+'.uid').unlink(missing_ok=True)
