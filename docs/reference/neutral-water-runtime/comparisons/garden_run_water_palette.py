from pathlib import Path
import json,subprocess,hashlib
p=Path('/var/folders/gf/s_g2zvzj3jxbylz3ylbc7k4c0000gn/T/garden-ziling-framing-o528drf8')
d=json.loads((p/"water-palette-command.json").read_text())
with (p/"water-palette.log").open("w") as f:r=subprocess.run(d["command"],stdout=f,stderr=subprocess.STDOUT,timeout=190)
d.update(status="terminal",exit_code=r.returncode,log_sha256=hashlib.sha256((p/"water-palette.log").read_bytes()).hexdigest())
(p/"water-palette-command.json").write_text(json.dumps(d,indent=2)+"\n")
print((p/"water-palette.log").read_text()[-4000:])
print("WATER_PALETTE_NATIVE_TERMINAL",r.returncode)
