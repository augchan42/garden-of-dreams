"""Compare independent candidate and installed captures with equal fixture clocks."""
from pathlib import Path
import hashlib,json,shutil,subprocess,re,os
r=Path('/tmp/garden-qiushuang-lattice-20261010');repo=Path('/Users/auchan/projects/garden-of-dreams')
assert not (r/'fixed-capture-comparison.json').exists()
report={'status':'running','pid':os.getpid(),'fixed_clock':3.,'phases':[],'scope':'Equal explicit native draw and scene clocks in both projects. Product files unchanged; no screenshot tolerance.'}
def save():(r/'fixed-capture-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 for label,game in [('candidate',r/'godot'),('installed',repo/'godot')]:
  helper=game/'tests/capture_lattice_fixed.gd';assert not helper.exists();shutil.copy2(r/'capture_lattice_fixed.gd',helper)
  log=r/f'fixed-capture-{label}.log';phase={'name':label,'status':'running','log':str(log)};report['phases'].append(phase);save()
  try:
   with log.open('w') as stream:
    child=subprocess.Popen(['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/capture_lattice_fixed.gd','--','--output='+str(r/f'native-fixed-{label}')],stdout=stream,stderr=subprocess.STDOUT)
    phase['pid']=child.pid;save()
    try:phase['exit_code']=child.wait(timeout=210)
    except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=15);raise
   text=log.read_text();assert phase['exit_code']==0 and 'QIUSHUANG_LATTICE_LIT_PASS' in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:)',text),text[-2000:]
   phase.update(status='passed',log_sha256=sha(log));save()
  finally:helper.unlink(missing_ok=True);Path(str(helper)+'.uid').unlink(missing_ok=True)
 files={}
 for p in (r/'native-fixed-candidate').glob('*.png'):
  other=r/'native-fixed-installed'/p.name
  assert p.read_bytes()==other.read_bytes(),p.name
  files[p.name]=sha(p)
 assert len(files)==8
 report.update(status='passed',byte_exact_originals=8,files=files);save()
 original=json.loads((r/'installed-validation.json').read_text())
 completed={**original,'status':'installed_canonical_source_and_engine_checks_passed','phases':original['phases'][:-1]+[{'name':'native_lattice_equal_explicit_draw_and_clock','status':'passed','exit_code':0,'log':str(r/'fixed-capture-installed.log'),'log_sha256':sha(r/'fixed-capture-installed.log')}],'failed_first_attempt':'installed-validation.json','failed_serial_attempt':'installed-capture-retry.json','explicit_draw_unfrozen_comparison':'forced-capture-comparison-failed.json','fixed_capture_comparison':'fixed-capture-comparison.json','installed_originals_exact_to_candidate':8,'scope':original['scope']+' Eight installed originals match a fresh candidate with the same fixture clock and native draw; earlier failures retained.'}
 (r/'installed-validation-completed.json').write_text(json.dumps(completed,indent=2)+'\n')
 print('QIUSHUANG_FIXED_NATIVE_COMPARISON_PASS',8,flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
