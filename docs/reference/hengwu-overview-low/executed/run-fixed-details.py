"""Prove stable final detail originals without altering production animation."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
repo=Path('/Users/auchan/projects/garden-of-dreams');work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-arrival-overview'
root=Path('/tmp/garden-hengwu-arrival-20261010');game=root/'godot';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
broad=json.loads((root/'broad-pipeline.json').read_text())
assert broad['status']=='broad_native_checks_passed_direct_original_review_pending' and len(broad['phases'])==30
assert all(p['status']=='passed' for p in broad['phases'])
assert not (root/'fixed-detail-pipeline.json').exists()
shutil.copyfile(game/'tests/test_hengwu_detail_framing.gd',root/'legacy-detail-before-fixed-clock.gd')
shutil.copyfile(work/'detail-regression-candidate-fixed-clock.gd',game/'tests/test_hengwu_detail_framing.gd')
frozen={str(p.relative_to(game)):sha(p) for folder in ['runtime','assets','lightmaps','tests'] for p in (game/folder).rglob('*') if p.is_file() and p.suffix!='.uid'}
report={'status':'running','frozen_inputs':frozen,'phases':[],'supersedes':'Only the three legacy-clock detail phases in focused-pipeline-v6; production runtime/source/assets are unchanged. Original broad frozen inputs remain byte-identical except the test-only deterministic capture helper.'}
for mode,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
 for repeat in [1,2]:
  name=f'detail-final-{mode}-repeat{repeat}';log=root/(name+'.log')
  command=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/test_hengwu_detail_framing.gd','--','--output='+str(root/name),*flags]
  print('HENGWU_FIXED_DETAIL_START',name,flush=True);phase={'name':name,'command':command,'log':str(log),'status':'running'};report['phases'].append(phase)
  with log.open('w') as stream:
   child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid
   (root/'fixed-detail-pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
   try:phase['exit_code']=child.wait(timeout=180)
   except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);phase['exit_code']=124
  text=log.read_text(errors='replace');okay=phase['exit_code']==0 and 'HENGWU_DETAIL_FRAMING_RESULT 10 captures; 0 failures' in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|Traceback)',text)
  phase.update(status='passed' if okay else 'failed',log_sha256=sha(log));(root/'fixed-detail-pipeline.json').write_text(json.dumps(report,indent=2)+'\n');assert okay,(name,text[-3000:]);print('HENGWU_FIXED_DETAIL_PASS',name,flush=True)
 a=root/f'detail-final-{mode}-repeat1';b=root/f'detail-final-{mode}-repeat2';images=list(a.glob('*.png'));assert len(images)==10 and all(sha(p)==sha(b/p.name) for p in images),f'Detail originals are not stable for {mode}'
 report.setdefault('originals_byte_exact',{}).update({mode+'/'+p.name:sha(p) for p in images})
assert all(sha(game/name)==digest for name,digest in frozen.items())
assert sha(repo/'godot/runtime/entry_route.gd')=='7970380d11f8eb59530602e391565f355a844a94e9aa16a369d260a86a434a05'
for name,digest in broad['frozen_inputs'].items():
 if name!='tests/test_hengwu_detail_framing.gd':assert sha(game/name)==digest,name
report['status']='fixed_detail_modes_passed_thirty_originals_reproduced_exactly'
(root/'fixed-detail-pipeline.json').write_text(json.dumps(report,indent=2)+'\n');print('HENGWU_FIXED_DETAIL_REPRODUCTION_PASS thirty_exact_originals',flush=True)
