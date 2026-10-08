"""Fit the tech kit to six terminal cells and three bulletin screen banks."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
s=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=s
variants=['crt_green','terminal_desk','cell_door','monitor_bank','cable_run']
with bpy.data.libraries.load(str(R/'blender/kits/KIT_tech.blend'),link=False) as (src,dst):dst.collections=['KIT_tech_'+v for v in variants]
models={v:next(o for o in c.objects if o.type=='MESH' and not o.name.startswith('COL_')) for v,c in zip(variants,dst.collections)}
proxies={v:[o for o in c.objects if o.name.startswith('COL_')] for v,c in zip(variants,dst.collections)}
canonical=bpy.data.materials['MAT_tech_atlas']
for model in models.values():model.data.materials.clear();model.data.materials.append(canonical)
def bounds(objects):
 points=[o.matrix_basis@Vector(p) for o in objects for p in o.bound_box]
 return Vector(tuple(min(p[i] for p in points) for i in range(3))),Vector(tuple(max(p[i] for p in points) for i in range(3)))
records=[];before={o.name:[v for row in o.matrix_basis for v in row] for o in s.objects if o.name.startswith(('COL_','TRG_','LGT_')) and not o.get('tech_placement')}
manifest=R/'export/tech-placements.json'
def add(site,variant,position,scale=(1,1,1),rotation=(0,0,0),colliders=True):
 records.append(dict(site=site,variant=variant,position=list(position),scale=list(scale),rotation=list(rotation),colliders=colliders))
if any(o.get('tech_placement') for o in s.objects):
 records=json.loads(manifest.read_text())['placements']
 for o in list(s.objects):
  if o.get('tech_placement'):bpy.data.objects.remove(o,do_unlink=True)
else:
 col=bpy.data.collections['SITE_terminal-cells']
 desks=sorted([o for o in col.objects if o.name.startswith('KIT_tech_terminal_desk')],key=lambda o:bounds([o])[0].x)
 assert len(desks)==6
 for desk in desks:
  lo,hi=bounds([desk]);center=(lo+hi)/2;size=hi-lo;cx=center.x
  add('terminal-cells','terminal_desk',(cx,center.y,0),(size.x/1.35,size.y/.74,hi.z/.8))
  root=Vector((cx,center.y+.1,hi.z+.001));scale=Vector((1,.5/.54,1))
  add('terminal-cells','crt_green',root,scale)
  add('terminal-cells','cell_door',(cx,-38.235,0),(1.12/1.08,.13/.18,2.1/2.32))
  socket=root+Vector((0,.29*scale.y,.24))
  add('terminal-cells','cable_run',(socket.x-.07*.4,socket.y,socket.z),((socket.z-.075)/3,.4,.4),(0,math.pi/2,0),False)
 for o in list(col.objects):
  if o.name.startswith(('KIT_tech_terminal_desk','KIT_tech_desk_leg','KIT_tech_CRT_','KIT_tech_scanline','KIT_tech_cursor')):bpy.data.objects.remove(o,do_unlink=True)
 # Original black jambs/head remain as wall infill around the fitted metal frame.
 col=bpy.data.collections['SITE_qiushuang-zhai']
 for desk in sorted([o for o in col.objects if o.name.startswith(('STUDY_desk_left','STUDY_desk_centre','STUDY_desk_right'))],key=lambda o:bounds([o])[0].x):
  lo,hi=bounds([desk]);center=(lo+hi)/2;size=hi-lo;cx=center.x
  add('qiushuang-zhai','terminal_desk',(cx,center.y,0),(size.x/1.35,size.y/.74,hi.z/.8),colliders=False)
  root=Vector((cx,15.65,.7));scale=Vector((.74/.72,.5/.54,.62/.65))
  add('qiushuang-zhai','monitor_bank',root,scale)
  socket=root+Vector((0,.29*scale.y,.665*scale.z))
  add('qiushuang-zhai','cable_run',(socket.x-.07*.5,socket.y,socket.z),((socket.z-.1)/3,.5,.5),(0,math.pi/2,0),False)
 for o in list(col.objects):
  if o.name.startswith(('STUDY_desk_','KIT_tech_CRT_','KIT_tech_scanline','KIT_tech_cursor')):bpy.data.objects.remove(o,do_unlink=True)
for index,record in enumerate(records):
 col=bpy.data.collections['SITE_'+record['site']];source=models[record['variant']];o=source.copy();o.data=source.data;o.parent=None;o.matrix_basis=Matrix.Identity(4)
 o.name='PLACED_tech_'+record['site'].replace('-','_')+'_'+str(index);o.location=record['position'];o.rotation_euler=record['rotation'];o.scale=record['scale'];o.hide_render=False;o.hide_viewport=False;o['tech_placement']=True;o['tech_variant']=record['variant'];o['placement_index']=index;col.objects.link(o);record['name']=o.name
 if record['colliders']:
  for collider_index,proxy in enumerate(proxies[record['variant']]):
   c=proxy.copy();c.data=proxy.data;c.parent=None;c.name='COL_tech_placed_'+str(index)+'_'+str(collider_index);c.matrix_basis=o.matrix_basis@proxy.matrix_basis;c.hide_render=True;c.hide_viewport=True;c['tech_placement']=True;col.objects.link(c)
for name,transform in before.items():assert [v for row in bpy.data.objects[name].matrix_basis for v in row]==transform,name
assert len(records)==33,len(records)
assert sum(4 if r['variant']=='monitor_bank' else 1 if r['variant'].startswith('crt_') else 0 for r in records)==18
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for slug in ['terminal-cells','qiushuang-zhai']:
 col=bpy.data.collections['SITE_'+slug];bpy.data.libraries.write(str(R/f'blender/sites/SITE_{slug}.blend'),{col},fake_user=True,compress=True)
manifest.write_text(json.dumps({'count':len(records),'screen_count':18,'placements':records,'existing_collision_light_trigger_transforms_preserved':True,'export_policy':'Batch each site by shared tech atlas; preserve existing room/action markers.'},indent=2)+'\n')
print('TECH_PLACEMENTS_PASS',len(records),'modules, 18 screens')
