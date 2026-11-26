"""Execute native visibility controls after the frozen final focused run."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
repo=Path('/Users/auchan/projects/garden-of-dreams');work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-arrival-overview'
root=Path('/tmp/garden-hengwu-arrival-20261010');game=root/'godot';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
focused=json.loads((root/'focused-pipeline-v6.json').read_text())
assert focused['status']=='focused_native_modes_passed_original_review_pending' and len(focused['phases'])==6
assert all(p['status']=='passed' for p in focused['phases'])
assert not (root/'native-visibility').exists()
shutil.copyfile(root/'focused-pipeline-v6.json',root/'focused-pipeline-final.json')
shutil.copyfile(work/'test-native-visibility.gd',game/'tests/test_hengwu_native_visibility.gd')
shutil.copyfile(root/'visibility-probes.json',game/'tests/hengwu-visibility-probes.json')
frozen={str(p.relative_to(game)):sha(p) for folder in ['runtime','assets','lightmaps','tests'] for p in (game/folder).rglob('*') if p.is_file() and p.suffix!='.uid'}
command=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/test_hengwu_native_visibility.gd','--','--output='+str(root/'native-visibility')]
log=root/'native-visibility.log';report={'status':'running','command':command,'frozen_inputs':frozen,'log':str(log)}
with log.open('w') as stream:
 child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT);report['pid']=child.pid
 (root/'native-visibility-pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
 try:report['exit_code']=child.wait(timeout=260)
 except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);report['exit_code']=124
text=log.read_text(errors='replace');okay=report['exit_code']==0 and 'HENGWU_NATIVE_VISIBILITY_RESULT 16 originals; 0 failures' in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|Traceback)',text)
report.update(status='native_visibility_passed_original_review_pending' if okay else 'failed',log_sha256=sha(log))
(root/'native-visibility-pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
assert okay,text[-3000:]
assert all(sha(game/name)==digest for name,digest in frozen.items()),'Fixture inputs changed during native control'
assert sha(repo/'godot/runtime/entry_route.gd')=='7970380d11f8eb59530602e391565f355a844a94e9aa16a369d260a86a434a05'
print('HENGWU_NATIVE_VISIBILITY_PASS sixteen_originals',flush=True)
