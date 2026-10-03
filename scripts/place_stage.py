"""Fit floor, studio-wall, fog and gel modules while preserving the 360-degree backdrop."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
variants=['floor_boards','studio_wall','fog_plane','gel_frame']
with bpy.data.libraries.load(str(R/'blender/kits/KIT_stage.blend'),link=False) as (src,dst):dst.collections=['KIT_stage_'+v for v in variants]
models={v:next(o for o in c.objects if o.type=='MESH' and not o.name.startswith('COL_')) for v,c in zip(variants,dst.collections)}
proxies={v:[o for o in c.objects if o.name.startswith('COL_')] for v,c in zip(variants,dst.collections)}
# Keep one source material per semantic surface after library appends.
for model in models.values():
 for i,m in enumerate(model.data.materials):
  base=m.name.split('.')[0];model.data.materials[i]=bpy.data.materials[base]
manifest=R/'export/stage-placements.json';records=[]
before={o.name:list(v for row in o.matrix_basis for v in row) for o in scene.objects if o.name.startswith(('COL_','TRG_','LGT_')) and not o.get('stage_placement')}
def bounds(o):
 points=[o.matrix_basis@Vector(p) for p in o.bound_box]
 return Vector(tuple(min(p[i] for p in points) for i in range(3))),Vector(tuple(max(p[i] for p in points) for i in range(3)))
def add(site,variant,position,scale=(1,1,1),rotation=(0,0,0),collision=False,matrix=None):
 record=dict(site=site,variant=variant,position=list(position),scale=list(scale),rotation=list(rotation),collision=collision)
 if matrix is not None:record['matrix']=[list(row) for row in matrix]
 records.append(record)
if any(o.get('stage_placement') for o in scene.objects):
 records=json.loads(manifest.read_text())['placements']
 for o in list(scene.objects):
  if o.get('stage_placement'):bpy.data.objects.remove(o,do_unlink=True)
else:
 col=bpy.data.collections['SITE_terminal-cells'];floors=sorted([o for o in col.objects if o.name.startswith('KIT_stage_cell_floor')],key=lambda o:bounds(o)[0].x);assert len(floors)==6
 for floor in floors:
  lo,hi=bounds(floor);center=(lo+hi)/2;size=hi-lo
  add('terminal-cells','floor_boards',(center.x,center.y,hi.z),(size.x/3,size.y/3,size.z/.05))
  # Black wall sits behind the corridor, away from the barred garden windows.
  add('terminal-cells','studio_wall',(center.x,-40.25,0),(2.6/3,1,2.8/3),(0,0,math.pi),True)
  bpy.data.objects.remove(floor,do_unlink=True)
 for col in scene.collection.children:
  for fog in list(col.objects):
   if fog.type=='MESH' and fog.name.startswith('KIT_stage_fog_plane'):
    lo,hi=bounds(fog);center=(lo+hi)/2;size=hi-lo
    add(col.name.removeprefix('SITE_'),'fog_plane',(center.x,center.y,center.z-.3),(size.x/3,size.y/3,1))
    bpy.data.objects.remove(fog,do_unlink=True)
 for x in [-6.5,6.5]:add('terminal-cells','gel_frame',(x,-40.145,1.3),rotation=(0,0,math.pi),collision=True)
for i,record in enumerate(records):
 col=bpy.data.collections['SITE_'+record['site']];source=models[record['variant']];o=source.copy();o.data=source.data;o.parent=None;o.name='PLACED_stage_'+record['site'].replace('-','_')+'_'+str(i);o.matrix_basis=Matrix.Identity(4)
 if 'matrix' in record:o.matrix_basis=Matrix(record['matrix'])
 else:o.location=record['position'];o.scale=record['scale'];o.rotation_euler=record['rotation']
 o.hide_render=False;o.hide_viewport=False;o['stage_placement']=True;o['stage_variant']=record['variant'];col.objects.link(o);record['name']=o.name
 if record['collision']:
  for j,proxy in enumerate(proxies[record['variant']]):
   c=proxy.copy();c.data=proxy.data;c.parent=None;c.name='COL_stage_placed_'+str(i)+'_'+str(j);c.matrix_basis=o.matrix_basis@proxy.matrix_basis;c.hide_render=True;c.hide_viewport=True;c['stage_placement']=True;col.objects.link(c)
for name,matrix in before.items():assert list(v for row in bpy.data.objects[name].matrix_basis for v in row)==matrix,name
assert sum(r['variant']=='floor_boards' for r in records)==6
assert sum(r['variant']=='studio_wall' for r in records)==6
assert sum(r['variant']=='gel_frame' for r in records)==2
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for site in sorted({r['site'] for r in records}|{'qiushuang-zhai','daguan-lou'}):bpy.data.libraries.write(str(R/f'blender/sites/SITE_{site}.blend'),{bpy.data.collections['SITE_'+site]},fake_user=True,compress=True)
manifest.write_text(json.dumps({'count':len(records),'placements':records,'existing_collision_light_trigger_transforms_preserved':True,'backdrop_unchanged':True,'changed_site_libraries':sorted({r['site'] for r in records}|{'qiushuang-zhai','daguan-lou'})},indent=2)+'\n')
print('STAGE_PLACEMENTS_PASS',len(records),{v:sum(r['variant']==v for r in records) for v in variants})
