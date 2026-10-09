from pathlib import Path
import subprocess,json,hashlib
cmd=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1','--python','/tmp/garden_inspect_ziling_source.py'];log=Path('/tmp/garden-ziling-source-inspection.log')
with log.open('w') as out:p=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=120)
print(log.read_text()[-2200:]);print('ZILING_SOURCE_INSPECTION_TERMINAL',p.returncode)
if Path('/tmp/garden-ziling-source-art.json').exists():
 w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root']);(w/'inspection-command.json').write_text(json.dumps({'command':cmd,'exit_code':p.returncode,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()},indent=2)+'\n');(w/'inspection.log').write_bytes(log.read_bytes())
