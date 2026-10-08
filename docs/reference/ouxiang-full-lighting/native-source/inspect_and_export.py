import bpy,json,sys,runpy,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
REPO=Path('/Users/auchan/projects/garden-of-dreams')
SOURCE=Path(json.load(open('/tmp/garden-oux-full-source.json'))['folder']).resolve()
expected=[([-20.1,-.24,0],[-18.3,0,5]),([-25.9,-.24,4.1],[-18.3,0,5.9]),([-25.9,-.24,4.1],[-24.1,0,11.7])]
def bounds(o):
 points=[o.matrix_world@v.co for v in o.data.vertices]
 points=[(p.x,p.z,-p.y) for p in points]
 return [min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]
def inspect(label):
 col=bpy.data.collections['SITE_stage'];rows=[]
 for prefix in ['LONGCUI_approach','COL_longcui_approach']:
  objects=sorted([o for o in col.objects if o.name.startswith(prefix)],key=lambda o:o.name)
  assert len(objects)==3,(label,prefix,[o.name for o in objects])
  for i,o in enumerate(objects):
   assert o.type=='MESH' and len(o.data.vertices)==8 and len(o.data.polygons)==6
   lo,hi=bounds(o);elo,ehi=expected[i]
   assert all(abs(a-b)<1e-5 for a,b in zip(lo+hi,elo+ehi)),(label,o.name,lo,hi)
   if prefix=='LONGCUI_approach':assert len(o.data.materials)==1 and o.data.materials[0].name=='MAT_plaster_rock'
   rows.append({'name':o.name,'vertices':8,'polygons':6,'bounds_min_y_up':lo,'bounds_max_y_up':hi,
    'materials':[m.name if m else None for m in o.data.materials],
    'matrix_world':[list(row) for row in o.matrix_world],
    'hide_render':o.hide_render,'collision':prefix.startswith('COL_')})
 return rows
report={'status':'native_saved_path_ownership_verified','scope':'Read-only native saved-object ownership. No source repair applied.','authoring':inspect('authoring')}
sys.path.insert(0,str(REPO/'scripts'))
runpy.run_path(str(REPO/'scripts/export_garden.py'),run_name='__main__')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'blender/sites/SITE_stage.blend'))
report['stage_library']=inspect('stage library')
assert report['authoring']==report['stage_library']
report['saved_stage_library_sha256']=hashlib.sha256((SOURCE/'blender/sites/SITE_stage.blend').read_bytes()).hexdigest()
(ROOT/'saved-path-ownership.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED_NUNNERY_PATH_OWNERSHIP_PASS')
