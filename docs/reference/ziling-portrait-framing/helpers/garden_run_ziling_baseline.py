import subprocess,json,hashlib
from pathlib import Path
w=Path('/Users/auchan/projects/garden-of-dreams/.superpowers/sdd/2026-09-23-garden-completion/ziling-runtime')
cmd=json.loads((w/"baseline-command.json").read_text())
with (w/"baseline.log").open("w") as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=130)
(w/"baseline-exit.json").write_text(json.dumps({"status":"terminal","exit_code":r.returncode,"log_sha256":hashlib.sha256((w/"baseline.log").read_bytes()).hexdigest()},indent=2)+"\n")
print((w/"baseline.log").read_text()[-6000:])
print("BASELINE_TERMINAL",r.returncode)
