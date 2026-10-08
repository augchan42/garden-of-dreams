"""Refresh the current demo and priority-2 bakes after source geometry changes.
Outputs per-site logs and returns nonzero on a failed Blender bake or sync.
"""
import subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
blender='/Applications/Blender.app/Contents/MacOS/Blender'
for site,samples in [('demo',32),('qiushuang-zhai',32),('tubi-tang',32),('daguan-lou',128)]:
 print('REFRESH_SITE_START',site,flush=True)
 with open('/tmp/garden-scene-bake-'+site+'.log','w') as log:
  result=subprocess.run([blender,'--background','--threads','8','--python-exit-code','1','--python',str(R/'scripts/bake_lightmaps.py'),'--','--site',site,'--size','512','--samples',str(samples)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:sys.exit(result.returncode)
 print('REFRESH_SITE_DONE',site,flush=True)
for command in [[sys.executable,'scripts/sync_lightmaps.py','--demo'],[sys.executable,'scripts/sync_priority2_lightmaps.py']]:subprocess.run(command,cwd=R,check=True)
print('SCENE_LIGHTMAP_REFRESH_PASS',flush=True)
