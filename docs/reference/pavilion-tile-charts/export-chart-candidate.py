import json, pathlib, subprocess, hashlib
root=pathlib.Path(json.load(open('/tmp/garden-tile-ridge-candidate.json'))['folder'])
script=pathlib.Path('/Users/auchan/projects/garden-of-dreams/scripts/export_garden.py')
cmd=['/Applications/Blender.app/Contents/MacOS/Blender','--background',str(root/'blender/authoring.blend'),'--threads','8','--python-exit-code','1','--python',str(script),'--','--output-root',str(root),'--pavilion-tile-uvs']
with (root/'export.log').open('w') as log:
 result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
record={'command':cmd,'exit_code':result.returncode,'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest()}
(root/'export-phase.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
raise SystemExit(result.returncode)
