from pathlib import Path
import json, subprocess, hashlib, re
root=Path(json.loads(Path('/tmp/garden-oux-camera-review.json').read_text())['folder']).resolve()
gd=root/'godot'
report={'status':'running','phases':[],'scope':'Cold native import and unchanged-runtime framing rejection.'}
def save():(root/'red-phases.json').write_text(json.dumps(report,indent=2)+'\n')
for label,command in [('cold-import',['/Applications/Godot.app/Contents/MacOS/Godot','--headless','--path',str(gd),'--editor','--import']),('old-framing',['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(gd),'--script','res://tests/test_oux_portrait_framing.gd','--','--output='+str(root/'old-framing')])]:
 log=root/(label+'.log');row={'name':label,'command':command,'status':'running','log':str(log)};report['phases'].append(row);save()
 with log.open('w') as out:
  p=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT,cwd=gd);row['pid']=p.pid;save();row['exit_code']=p.wait()
 row['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest();save()
 text=log.read_text(errors='replace')
 assert not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:)',text),text[-4000:]
 assert row['exit_code']==(0 if label=='cold-import' else 1),text[-4000:]
 if label=='old-framing':
  result=json.loads((root/'old-framing/report.json').read_text());assert result['status']=='failed' and any('roof clipped' in s for s in result['failures'])
 row['status']='passed' if label=='cold-import' else 'expected_rejection';save()
report['status']='old_portrait_clipping_reproduced';save();print('OUX_CAMERA_RED_CONFIRMED',root)
