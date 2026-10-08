"""Create one solid and one joined broken bronze mesh for each table slot."""
import bpy,ast,os,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from pavilion_material import apply_atlas
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
C=scene.collection.children['SITE_qinfang-ting']
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
gold=bpy.data.materials['MAT_bronze']
for o in list(C.objects):
 if o.name.startswith('HERO_table_line_'):bpy.data.objects.remove(o,do_unlink=True)
for i in range(6):
 for variant in ['solid','broken']:
  y=-.35+i*.14
  pieces=[box('line_piece',(0,y,.91),(.65,.055,.018),gold)] if variant=='solid' else [box('line_piece',(x,y,.91),(.215,.055,.018),gold) for x in [-.2175,.2175]]
  bpy.ops.object.select_all(action='DESELECT')
  for o in pieces:o.select_set(True)
  bpy.context.view_layer.objects.active=pieces[0]
  if len(pieces)>1:bpy.ops.object.join()
  model=bpy.context.object;model.name=f'HERO_table_line_{i+1}_{variant}'
  model['line_index']=i+1;model['variant']=variant;model['line_order']='bottom_to_top'
  for channel in ['UVMap','LightmapUV']:
   model.data.uv_layers.new(name=channel);model.data.uv_layers.active_index=len(model.data.uv_layers)-1
   bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
  apply_atlas(model,R)
  model.hide_render=variant=='broken';model.hide_viewport=variant=='broken'
assert len([o for o in C.objects if o.name.startswith('HERO_table_line_')])==12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_qinfang-ting.blend';bpy.data.libraries.write(str(file),{C},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_qinfang-ting']
s=bpy.context.scene;s.name='SITE_qinfang-ting';s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.camera=next(o for o in s.objects if o.name.startswith('CAM_stage_wide'))
tmp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('HEXAGRAM_LINES_COMPLETE: twelve meshes, six bottom-to-top solid/broken pairs')
