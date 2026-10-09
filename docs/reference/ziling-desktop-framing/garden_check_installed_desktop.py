from pathlib import Path
import subprocess,json
r=Path('/Users/auchan/projects/garden-of-dreams');p=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-desktop-framing';g='/Applications/Godot.app/Contents/MacOS/Godot';rows=[]
for name,script in [('installed-normal','res://tests/test_ziling_framing.gd'),('installed-western','/tmp/garden_render_western_framing.gd')]:
 cmd=[g,'--path',str(r/'godot'),'--windowed','--resolution','1410x600','--script',script,'--','--output='+str(p/name)]
 with (p/(name+'.log')).open('w') as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 rows.append({'phase':name,'returncode':result.returncode,'command':cmd})
 (p/'installed-pipeline.json').write_text(json.dumps({'status':'running' if result.returncode==0 and name=='installed-normal' else ('installed_checks_passed' if result.returncode==0 else 'rejected'),'rows':rows},indent=2))
 print('INSTALLED_DESKTOP_PHASE',name,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
