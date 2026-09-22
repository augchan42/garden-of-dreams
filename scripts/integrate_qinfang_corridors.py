"""Replace the sixteen straight Qinfang approach bays with the completed kit."""
import bpy,math,os
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
site=next(c for c in scene.collection.children if c.name=='SITE_qinfang-ting')
bpy.context.view_layer.update()
removed=0
for o in list(site.objects):
 is_old=o.name.startswith(('KIT_corridor_','COL_corridor'))
 center=sum((o.matrix_world@Vector(p) for p in o.bound_box),Vector())/8 if o.type=='MESH' else Vector()
 bridge_rail=o.name.startswith(('KIT_corridor_rail','KIT_corridor_baluster')) and abs(abs(center.x)-3.25)<.1 and 3.1<=abs(center.y)<=6.9
 if o.get('kit_placement')=='qinfang_corridor' or (is_old and not bridge_rail):
  bpy.data.objects.remove(o,do_unlink=True);removed+=1
canonical={m.name:m for m in bpy.data.materials}
with bpy.data.libraries.load(str(R/'blender/kits/KIT_corridor.blend'),link=False) as (src,dst):dst.collections=['KIT_corridor_straight']
module=dst.collections[0]
for direction,dx,dy,angle in [('north',0,1,0),('south',0,-1,math.pi),('east',1,0,-math.pi/2),('west',-1,0,math.pi/2)]:
 for bay in range(4):
  distance=8.5+3*bay
  xf=Matrix.Translation((dx*distance,dy*distance,0))@Matrix.Rotation(angle,4,'Z')
  for source in module.objects:
   if source.name.startswith('PORT_'):continue
   o=source.copy()
   if o.type=='MESH':
    o.data=source.data.copy()
    for i,m in enumerate(o.data.materials):
     if m and m.name.split('.')[0] in canonical:o.data.materials[i]=canonical[m.name.split('.')[0]]
    for layer in list(o.data.uv_layers)[1:]:o.data.uv_layers.remove(layer)
   site.objects.link(o);o.matrix_world=xf@source.matrix_basis
   col=source.name.startswith('COL_')
   o.name=('COL_' if col else '')+f'QINFANG_corridor_{direction}_{bay}'
   o['kit_placement']='qinfang_corridor';o['kit_part']='straight';o['bay_direction']=direction
   o.hide_viewport=col;o.hide_render=col
bpy.context.view_layer.update()
assert sum(o.get('kit_placement')=='qinfang_corridor' and not o.name.startswith('COL_') for o in site.objects)==16
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_qinfang-ting.blend';bpy.data.libraries.write(str(file),{site},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_qinfang-ting']
s=bpy.context.scene;s.name='SITE_qinfang-ting';s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.camera=next(o for o in s.objects if o.name.startswith('CAM_stage_wide'))
tmp=file.with_name('SITE_qinfang-ting-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('QINFANG_CORRIDORS_INTEGRATED',removed,'old objects replaced by 16 bays')
