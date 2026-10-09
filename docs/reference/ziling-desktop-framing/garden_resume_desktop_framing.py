from pathlib import Path
import subprocess,json,datetime
p=Path('/Users/auchan/projects/garden-of-dreams/.superpowers/sdd/2026-09-23-garden-completion/ziling-desktop-framing')
g='/Applications/Godot.app/Contents/MacOS/Godot';rows=[]
for mode,flags in [('touch',['--touch']),('density',['--density'])]:
 out=p/('green-'+mode);cmd=[g,'--path',str(p/'godot'),'--windowed','--resolution','1410x600','--script','res://tests/test_ziling_framing.gd','--','--output='+str(out),*flags]
 with (p/('green-'+mode+'.log')).open('w') as log:
  r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 rows.append({'phase':mode,'returncode':r.returncode,'command':cmd})
 (p/'green-pipeline.json').write_text(json.dumps({'status':'running' if r.returncode==0 else 'rejected','rows':rows},indent=2))
 print('DESKTOP_FRAMING_PHASE',mode,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
cmd=[g,'--headless','--path',str(p/'godot'),'--script','res://tests/test_western_route.gd']
with (p/'western-route.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
rows.append({'phase':'western-route','returncode':r.returncode,'command':cmd})
(p/'green-pipeline.json').write_text(json.dumps({'status':'focused_checks_passed' if r.returncode==0 else 'rejected','rows':rows},indent=2))
print('DESKTOP_FRAMING_PHASE western-route',r.returncode,flush=True)
raise SystemExit(r.returncode)
