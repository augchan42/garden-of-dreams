"""Replace existing props with fitted kit meshes; batch them during garden export."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
s=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=s
variants=['lantern_hanging','stone_stool','stone_table','incense_burner','folding_chair']
with bpy.data.libraries.load(str(R/'blender/kits/KIT_props.blend'),link=False) as (src,dst):dst.collections=['KIT_props_'+v for v in variants]
models={v:next(o for o in c.objects if o.type=='MESH' and not o.name.startswith('COL_')) for v,c in zip(variants,dst.collections)}
canonical=bpy.data.materials['MAT_props_atlas']
for model in models.values():
 model.data.materials.clear();model.data.materials.append(canonical)
def bounds(objects):
 points=[o.matrix_basis@Vector(p) for o in objects for p in o.bound_box]
 return Vector(tuple(min(p[i] for p in points) for i in range(3))),Vector(tuple(max(p[i] for p in points) for i in range(3)))
records=[];before={o.name:list(sum((list(row) for row in o.matrix_basis),[])) for o in s.objects if o.name.startswith(('COL_','TRG_','LGT_'))}
manifest=R/'export/prop-placements.json'
if any(o.get('prop_placement') for o in s.objects):
 assert manifest.exists(),'Placed source needs its catalog'
 records=json.loads(manifest.read_text())['placements']
 for o in list(s.objects):
  if o.get('prop_placement'):bpy.data.objects.remove(o,do_unlink=True)
else:
 for c in s.collection.children:
  slug=c.name.removeprefix('SITE_')
  papers=[o for o in c.objects if o.name.startswith('KIT_props_lantern_paper')]
  for paper in sorted(papers,key=lambda o:o.name):
   lo,hi=bounds([paper]);center=(lo+hi)/2;scale=(.6875,.6875,.65/.73)
   records.append(dict(site=slug,variant='lantern_hanging',position=list(center-Vector((0,0,.58*scale[2]))),scale=list(scale),replaces=paper.name))
  if papers:
   for o in list(c.objects):
    if o.name.startswith('KIT_props_lantern_'):bpy.data.objects.remove(o,do_unlink=True)
  for o in list(c.objects):
   if o.name.startswith(('KIT_props_stool','KIT_props_tea_stool','HENGWU_study_stool')):
    lo,hi=bounds([o]);center=(lo+hi)/2;size=hi-lo
    records.append(dict(site=slug,variant='stone_stool',position=[center.x,center.y,lo.z],scale=[size.x/.54,size.y/.54,size.z/.46],replaces=o.name))
    bpy.data.objects.remove(o,do_unlink=True)
  table=next((o for o in c.objects if o.name in ['HENGWU_study_table','TUBI_topic_table']),None)
  if table:
   lo,hi=bounds([table]);collider=next(o for o in c.objects if o.name in ['COL_hengwu_table','COL_tubi_topic_table']);floor,_=bounds([collider]);center=(lo+hi)/2;size=hi-lo
   records.append(dict(site=slug,variant='stone_table',position=[center.x,center.y,floor.z],scale=[size.x/1.5,size.y/1.5,(hi.z-floor.z)/.82],replaces=table.name))
   for o in list(c.objects):
    if o==table or o.name.startswith(('HENGWU_table_leg','TUBI_topic_pedestal')):bpy.data.objects.remove(o,do_unlink=True)
  burner=[o for o in c.objects if o.name.startswith(('LONGCUI_incense_','LONGCUI_burner_foot'))]
  if burner:
   lo,hi=bounds(burner);center=(lo+hi)/2;size=hi-lo
   source_lo,source_hi=bounds([models['incense_burner','folding_chair']]);source_size=source_hi-source_lo;scale=Vector((size.x/source_size.x,size.y/source_size.y,size.z/source_size.z))
   records.append(dict(site=slug,variant='incense_burner',position=list(Vector((center.x,center.y,lo.z))-Vector((0,0,source_lo.z*scale.z))),scale=list(scale),replaces='LONGCUI_incense_bowl'))
   for o in burner:bpy.data.objects.remove(o,do_unlink=True)
# Fit the terminal sheet's chairs to its existing seat markers.
if not any(r['variant']=='folding_chair' for r in records):
 col=bpy.data.collections['SITE_terminal-cells']
 seats=sorted([o for o in col.objects if o.name.startswith('TRG_cell_seat')],key=lambda o:o.location.x)
 assert len(seats)==6
 for marker in seats:
  records.append(dict(site='terminal-cells',variant='folding_chair',position=list(marker.location),scale=[1,1,1],rotation=[0,0,3.141592653589793],replaces='KIT_props_chair_*'))
 for o in list(col.objects):
  if o.name.startswith('KIT_props_chair_'):bpy.data.objects.remove(o,do_unlink=True)
for index,record in enumerate(records):
 source=models[record['variant']];o=source.copy();o.data=source.data;o.name='PLACED_props_'+record['site'].replace('-','_')+'_'+str(index);o.parent=None;o.matrix_basis=Matrix.Identity(4);o.location=record['position'];o.scale=record['scale'];o.rotation_euler=record.get('rotation',[0,0,0]);o.hide_render=False;o.hide_viewport=False;o['prop_placement']=True;o['prop_variant']=record['variant'];o['placement_index']=index
 bpy.data.collections['SITE_'+record['site']].objects.link(o);record['name']=o.name
# Also remove an old pedestal on an idempotent rerun of an earlier placement pass.
for o in list(bpy.data.collections['SITE_tubi-tang'].objects):
 if o.name.startswith('TUBI_topic_pedestal'):bpy.data.objects.remove(o,do_unlink=True)
# Preserve every existing collision, trigger and light transform exactly.
for name,transform in before.items():assert list(sum((list(row) for row in bpy.data.objects[name].matrix_basis),[]))==transform,name
assert len(records)==38,(len(records),records)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for slug in sorted({r['site'] for r in records}):
 col=bpy.data.collections['SITE_'+slug];path=R/f'blender/sites/SITE_{slug}.blend';bpy.data.libraries.write(str(path),{col},fake_user=True,compress=True)
manifest.write_text(json.dumps({'placements':records,'count':len(records),'existing_collision_light_trigger_transforms_preserved':True,'export_policy':'Batch by site and shared atlas material; retain interactive table meshes.'},indent=2)+'\n')
print('PROPS_PLACEMENTS_PASS',len(records))
