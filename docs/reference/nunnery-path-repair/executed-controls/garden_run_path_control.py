from pathlib import Path
import json,subprocess,hashlib,re
r=Path(json.load(open('/tmp/garden-nunnery-path-candidate.json'))['folder']);gd=r/'control-godot';out=r/'native-control';out.mkdir();report={'status':'running','phases':[],'scope':'Separate source-matched controlled paving render only. No production changes.'}
def save():(r/'native-control-pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 for name,cmd,marker in [('import',['/Applications/Godot.app/Contents/MacOS/Godot','--headless','--path',str(gd),'--editor','--import'],None),('render',['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(gd),'--script','res://render_path_control.gd','--','--output='+str(out)],'PATH_NATIVE_CONTROL_CAPTURE_PASS')]:
  log=out/(name+'.log');phase={'name':name,'command':cmd,'log':str(log),'status':'running'};report['phases'].append(phase);save()
  with log.open('w') as file:p=subprocess.run(cmd,stdout=file,stderr=subprocess.STDOUT)
  phase['exit_code']=p.returncode;phase['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest();txt=log.read_text();assert p.returncode==0 and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:)|Parse Error:',txt),txt[-4000:]
  if marker:assert marker in txt,txt[-3000:]
  phase['status']='passed';save();print('PATH_NATIVE_PHASE_PASS',name,flush=True)
 report['status']='native_captures_complete_visual_review_pending';save()
except BaseException as e:report['status']='failed';report['error']=str(e);save();raise
