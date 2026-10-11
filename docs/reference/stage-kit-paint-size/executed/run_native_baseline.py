from pathlib import Path
import subprocess,json,re,hashlib,sys
r=Path(__file__).resolve().parent;exe='/Applications/Godot.app/Contents/MacOS/Godot';phases=[]
for name,command,marker in [('resources',[exe,'--headless','--path',str(r/'godot-baseline'),'--script','res://tests/test_stage_kit.gd'],'STAGE_RUNTIME_PASS'),('views',[exe,'--path',str(r/'godot-baseline'),'--windowed','--resolution','1600x1000','--script','res://tests/render_stage_kit.gd'],'STAGE_RENDER_PASS')]:
 log=r/('native-baseline-'+name+'.log')
 with log.open('w') as f:p=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 text=log.read_text(errors='replace');phases.append({'name':name,'exit_code':p.returncode,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()});assert p.returncode==0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|Traceback)',text),text[-2000:]
(r/'native-baseline.json').write_text(json.dumps({'status':'passed','phases':phases},indent=2)+'\n');print('STAGE_NATIVE_BASELINE_PASS')
