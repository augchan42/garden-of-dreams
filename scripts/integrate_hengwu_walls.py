"""Place textured wall modules around Hengwu's existing 9 x 8 metre court."""
import bpy, math, os
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
site=scene.collection.children['SITE_hengwu-yuan']
prefixes=('HENGWU_side_wall','HENGWU_window_spandrel','HENGWU_window_jamb',
 'HENGWU_window_frame','HENGWU_leak_lattice','HENGWU_side_cap',
 'HENGWU_front_wall','HENGWU_front_cap','HENGWU_entry_jamb','HENGWU_entry_lintel',
 'COL_hengwu_side_wall','COL_hengwu_front_wall')
for o in list(site.objects):
 if o.name.startswith(prefixes) or o.get('kit_placement')=='hengwu_wall':
  bpy.data.objects.remove(o,do_unlink=True)
canonical={m.name:m for m in bpy.data.materials}
parts=['bay','moon_gate','window_diamond','window_ice']
with bpy.data.libraries.load(str(R/'blender/kits/KIT_wall.blend'),link=False) as (src,dst):
 dst.collections=['KIT_wall_'+part for part in parts]
modules=dict(zip(parts,dst.collections))
def place(part,p,angle=0,width_scale=1):
 xf=Matrix.Translation(p)@Matrix.Rotation(angle,4,'Z')@Matrix.Diagonal((width_scale,1,1,1))
 for source in modules[part].objects:
  if source.type!='MESH':continue
  o=source.copy();o.data=source.data.copy()
  for i,m in enumerate(o.data.materials):
   if m and m.name.split('.')[0] in canonical:o.data.materials[i]=canonical[m.name.split('.')[0]]
  for layer in list(o.data.uv_layers)[1:]:o.data.uv_layers.remove(layer)
  site.objects.link(o);o.matrix_world=xf@source.matrix_basis
  collision=source.name.startswith('COL_')
  o.name=('COL_' if collision else '')+'HENGWU_kit_'+part
  o['kit_placement']='hengwu_wall';o['kit_part']=part
  o.hide_viewport=collision;o.hide_render=collision
for x in [-21,-15]:place('bay',(x,10,0))
place('moon_gate',(-18,10,0))
for x,window in [(-22.5,'window_diamond'),(-13.5,'window_ice')]:
 for i,part in enumerate(['bay',window,'bay']):
  place(part,(x,10+(i+.5)*8/3,0),math.pi/2,8/9)
bpy.context.view_layer.update()
assert sum(o.get('kit_placement')=='hengwu_wall' for o in site.objects)==18
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_hengwu-yuan.blend'
bpy.data.libraries.write(str(file),{site},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_hengwu-yuan']
s=bpy.context.scene;s.name='SITE_hengwu-yuan';s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.camera=next(o for o in s.objects if o.name.startswith('CAM_hengwu-yuan_wide'))
tmp=file.with_name(file.stem+'-packaged.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('HENGWU_WALL_KIT_INTEGRATED: nine wall modules with separate collision')
