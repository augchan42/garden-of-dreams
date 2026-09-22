"""Place the completed pavilion kit in the central site without changing route markers."""
import bpy, math, os
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
site=next(c for c in scene.collection.children if c.name=='SITE_qinfang-ting')
# Keep the existing bridge/plinth, table, lanterns, corridors and interaction markers.
for o in list(site.objects):
 if (o.name.startswith('KIT_pavilion_') and not o.name.startswith('KIT_pavilion_plinth')) or o.get('kit_placement')=='qinfang_pavilion':
  bpy.data.objects.remove(o,do_unlink=True)
canonical={m.name:m for m in bpy.data.materials}
parts=['roof_hex','post','bracket','bench']
with bpy.data.libraries.load(str(R/'blender/kits/KIT_pavilion.blend'),link=False) as (src,dst):
 dst.collections=['KIT_pavilion_'+p for p in parts]
modules=dict(zip(parts,dst.collections))
def place(part,position,angle=0):
 xf=Matrix.Translation(position)@Matrix.Rotation(angle,4,'Z')
 for source in modules[part].objects:
  if source.name.startswith('PORT_'):continue
  o=source.copy()
  if o.type=='MESH':
   o.data=source.data.copy()
   for i,m in enumerate(o.data.materials):
    if m and m.name.split('.')[0] in canonical:o.data.materials[i]=canonical[m.name.split('.')[0]]
   # Exporter rebakes the second UV channel after all placed parts are batched.
   for layer in list(o.data.uv_layers)[1:]:o.data.uv_layers.remove(layer)
  site.objects.link(o);o.matrix_world=xf@source.matrix_world
  is_collision=source.name.startswith('COL_')
  o.name=('COL_' if is_collision else '')+'QINFANG_kit_'+part
  o['kit_placement']='qinfang_pavilion';o['kit_part']=part
  o.hide_viewport=is_collision;o.hide_render=is_collision
place('roof_hex',(0,0,3.58),-math.pi/12)
for i in range(6):
 a=i*math.tau/6+math.pi/6;p=(2.7*math.cos(a),2.7*math.sin(a))
 place('post',(*p,0));place('bracket',(*p,3.1),a)
# Leaning benches sit just inside the south bridge balustrades, clear of all exits.
place('bench',(-2.85,-5,0),math.pi/2)
place('bench',(2.85,-5,0),-math.pi/2)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_qinfang-ting.blend'
bpy.data.libraries.write(str(file),{site},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_qinfang-ting']
s=bpy.context.scene;s.name='SITE_qinfang-ting';s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.camera=next(o for o in s.objects if o.name.startswith('CAM_stage_wide'))
tmp=file.with_name('SITE_qinfang-ting-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('QINFANG_KIT_INTEGRATED: one roof, six posts, six brackets, two bridge benches')
