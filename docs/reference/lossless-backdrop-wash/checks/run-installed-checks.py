import json,subprocess,re
from pathlib import Path
r=Path('/tmp/garden-backdrop-seam-20261010');project=Path('/Users/auchan/projects/garden-of-dreams/godot');phases=[]
checks=[('wash-resource','test_backdrop_wash_import.gd',['--output='+str(r/'installed-wash-resource.json')]),('baked-wash-normal','test_baked_backdrop_wash.gd',[]),('baked-wash-demo','test_baked_backdrop_wash.gd',['--demo']),('runtime-caps','test_runtime_texture_caps.gd',['--output='+str(r/'installed-runtime-caps.json')]),('moon-resource','test_moon_runtime_import.gd',['--output='+str(r/'installed-moon-resource.json')]),('arrivals-desktop','render_entry_route.gd',['--views-only','--fixed-clock','--output-directory='+str(r/'installed-arrivals-desktop')]),('arrivals-portrait','render_entry_route.gd',['--views-only','--fixed-clock','--mobile','--output-directory='+str(r/'installed-arrivals-portrait')])]
for name,script,args in checks:
 command=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(project),'--script','res://tests/'+script,'--',*args]
 log=r/('installed-'+name+'.log');row={'name':name,'command':command,'status':'running'};phases.append(row)
 with log.open('w') as f:
  p=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT);row['pid']=p.pid;(r/'installed-checks.json').write_text(json.dumps(phases,indent=2)+'\n')
  try:row['exit_code']=p.wait(timeout=100)
  except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=10);row['status']='timeout';(r/'installed-checks.json').write_text(json.dumps(phases,indent=2)+'\n');raise
 row['diagnostics']=re.findall(r'^(?:SCRIPT ERROR|ERROR|WARNING):.*$',log.read_text(),re.MULTILINE)
 row['status']='passed' if row['exit_code']==0 and not row['diagnostics'] else 'failed';(r/'installed-checks.json').write_text(json.dumps(phases,indent=2)+'\n');assert row['status']=='passed',log.read_text()[-2000:]
print('INSTALLED_LOSSLESS_WASH_CHECKS_PASS',len(phases))
