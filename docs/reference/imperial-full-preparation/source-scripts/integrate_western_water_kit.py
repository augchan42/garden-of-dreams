"""Place the water-kit bridge and lotus clusters in the two western sites."""
import bpy,math,os
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children}
for slug in ['ouxiang-xie','ziling-zhou']:
 for o in list(sites[slug].objects):
  old_lotus=o.name.startswith(('KIT_water_ouxiang_lotus','KIT_water_ziling_lotus'))
  old_bridge=slug=='ziling-zhou' and o.name.startswith(('KIT_water_footbridge_','COL_ziling_footbridge','COL_ziling_bridge_rail','KIT_corridor_rail','KIT_corridor_baluster'))
  if old_lotus or old_bridge or o.get('kit_placement')=='western_water':bpy.data.objects.remove(o,do_unlink=True)
canonical={m.name:m for m in bpy.data.materials}
with bpy.data.libraries.load(str(R/'blender/kits/KIT_water.blend'),link=False) as (src,dst):dst.collections=['KIT_water_wood_bridge','KIT_water_lotus']
modules=dict(zip(['wood_bridge','lotus'],dst.collections))
def place(slug,part,p,angle=0):
 xf=Matrix.Translation(p)@Matrix.Rotation(angle,4,'Z')
 for source in modules[part].objects:
  if source.name.startswith('PORT_'):continue
  o=source.copy()
  if o.type=='MESH':
   o.data=source.data.copy()
   for i,m in enumerate(o.data.materials):
    if m and m.name.split('.')[0] in canonical:o.data.materials[i]=canonical[m.name.split('.')[0]]
   for layer in list(o.data.uv_layers)[1:]:o.data.uv_layers.remove(layer)
  sites[slug].objects.link(o);o.matrix_world=xf@source.matrix_basis
  col=source.name.startswith('COL_');o.name=('COL_' if col else '')+'WESTERN_kit_'+part
  o['kit_placement']='western_water';o['kit_part']=part
  o.hide_viewport=col;o.hide_render=col
place('ziling-zhou','wood_bridge',(-28.5,0,0),math.pi/2)
for i,(x,y) in enumerate([(-25.7,-3.3),(-22,-3.7),(-24.8,3.5),(-20,3.6)]):place('ouxiang-xie','lotus',(x,y,-1.065),i*.71)
for i,(x,y) in enumerate([(-32.7,3.25),(-36.3,-3.2)]):place('ziling-zhou','lotus',(x,y,-1.065),i*1.3)
bpy.context.view_layer.update()
assert sum(o.get('kit_part')=='wood_bridge' and not o.name.startswith('COL_') for o in sites['ziling-zhou'].objects)==1
assert sum(o.get('kit_part')=='lotus' for slug in ['ouxiang-xie','ziling-zhou'] for o in sites[slug].objects)==6
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for slug in ['ouxiang-xie','ziling-zhou']:bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{sites[slug]},fake_user=True,compress=True)
for slug in ['ouxiang-xie','ziling-zhou']:
 file=R/'blender/sites'/('SITE_'+slug+'.blend');bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_'+slug]
 s=bpy.context.scene;s.name='SITE_'+slug;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
 s.camera=next(o for o in s.objects if o.name.startswith('CAM_'+slug+'_wide'))
 tmp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('WESTERN_WATER_KIT_INTEGRATED: 6m bridge and six lotus clusters')
