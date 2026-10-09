from pathlib import Path
import json,subprocess,hashlib
p=Path(json.loads(Path('/tmp/garden-ziling-framing.json').read_text())['folder']);d=json.loads((p/'roof-command.json').read_text());log=p/'roof-native.log'
with log.open('w') as f:
 try:res=subprocess.run(d['command'],stdout=f,stderr=subprocess.STDOUT,timeout=190);code=res.returncode
 except subprocess.TimeoutExpired:code=124
d.update(status='terminal',exit_code=code,log_sha256=hashlib.sha256(log.read_bytes()).hexdigest());(p/'roof-command.json').write_text(json.dumps(d,indent=2)+'\n')
print(log.read_text()[-2500:]);print('ZILING_ROOF_NATIVE_TERMINAL',code)
