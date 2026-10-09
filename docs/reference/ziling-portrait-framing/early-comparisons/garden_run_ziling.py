from pathlib import Path
import json,subprocess,hashlib
p=Path('/var/folders/gf/s_g2zvzj3jxbylz3ylbc7k4c0000gn/T/garden-ziling-framing-o528drf8')
d=json.loads((p/"command.json").read_text())
with (p/"native-comparison.log").open("w") as f:r=subprocess.run(d["command"],stdout=f,stderr=subprocess.STDOUT,timeout=160)
d.update(status="terminal",exit_code=r.returncode,log_sha256=hashlib.sha256((p/"native-comparison.log").read_bytes()).hexdigest())
(p/"command.json").write_text(json.dumps(d,indent=2)+"\n")
print((p/"native-comparison.log").read_text()[-3500:])
print("ZILING_NATIVE_TERMINAL",r.returncode)
