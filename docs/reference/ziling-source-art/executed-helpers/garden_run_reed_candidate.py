from pathlib import Path
import json,subprocess,hashlib
w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root']);log=w/'reed-build.log';cmd=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1','--python','/tmp/garden_build_reed_candidate.py']
with log.open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
(w/'reed-command.json').write_text(json.dumps({'status':'terminal','command':cmd,'exit_code':p.returncode,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()},indent=2)+'\n');print(log.read_text()[-1700:]);print('REED_BUILD_TERMINAL',p.returncode)
