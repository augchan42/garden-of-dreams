import pathlib,json,subprocess,hashlib
w=pathlib.Path(json.load(open('/tmp/garden-tile-ridge-candidate.json'))['folder'])
script=w/'scripts/bake_lightmaps.py'
cmd=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1','--python',str(script),'--','--mesh','SITE_qinfang-ting_MAT_pavilion_atlas','--size','1024','--samples','128']
with (w/'roof-bake.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
record={'command':cmd,'exit_code':r.returncode,'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest()}
(w/'roof-bake-phase.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
raise SystemExit(r.returncode)
