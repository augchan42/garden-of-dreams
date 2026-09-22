import bpy, ast, math, random
from pathlib import Path
from mathutils import Vector
R=Path('/Users/auchan/projects/garden-of-dreams')
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
sites={};random.seed(74)
tree=ast.parse((R/'scripts/build_garden.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','plaster':'whitewash','roofmat':'rooftile','stone':'plaster_rock','black':'backstage','gold':'bronze','amber':'lantern','green':'crt_green','crtamber':'crt_amber','water':'water','foliage':'foliage_card','cycomat':'cyclorama'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
font=next(f for f in bpy.data.fonts if 'Songti' in f.filepath)
for kit in ['corridor','pavilion','wall','rockery','water','flora','props','tech','stage']:
 if kit in ['corridor','wall','pavilion','water','rockery'] and (R/f'export/kits/{kit}/manifest.json').exists():continue
 C=bpy.data.collections.new('KIT_'+kit)
 scene.collection.children.link(C)
 if kit=='corridor':corridor((0,0,0))
 if kit=='pavilion':pavilion((0,0,0))
 if kit=='wall':
  box('KIT_wall_bay',(0,0,1.2),(3,.2,2.4),plaster)
  for i in range(7):box('KIT_wall_lattice',(5+i*.15,0,1.4),(.025,.05,1.4),wood)
 if kit=='rockery':
  for i in range(6):rock((i*3,0,0),(.6+i*.14,.7,1+i*.3))
 if kit=='water':box('KIT_water_surface',(0,0,0),(6,3,.03),water);box('KIT_water_bank',(0,2,0),(6,.5,.6),stone)
 if kit=='flora':bamboo((0,0,0))
 if kit=='props':lantern((0,0,1.5));cyl('KIT_props_table',(2,0,.75),.8,.15,stone);cyl('KIT_props_stool',(3.2,0,.25),.3,.5,stone)
 if kit=='tech':crt((0,0,1));crt((2,0,1),True);box('KIT_tech_desk',(0,0,.65),(1.3,.7,.1),wood)
 if kit=='stage':
  box('KIT_stage_boards',(0,0,-.1),(3,3,.2),wood)
  box('KIT_stage_black_wall',(0,2,2),(3,.15,4),black)
 bpy.data.libraries.write(str(R/'blender/kits'/('KIT_'+kit+'.blend')),{C},fake_user=True,compress=True)
# Make each collection library a normal, directly openable .blend.
paths=list((R/'blender/sites').glob('*.blend'))+list((R/'blender/kits').glob('*.blend'))
for file in paths:
 if file.stem in ["KIT_corridor","KIT_wall","KIT_pavilion","KIT_water","KIT_rockery"] and (R/f"export/kits/{file.stem[4:]}/manifest.json").exists():continue
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
 s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC';s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1410;s.render.resolution_y=600
 s.camera=next((o for o in s.objects if o.type=='CAMERA'),None)
 if not s.camera:
  d=bpy.data.cameras.new('CAM_library');o=bpy.data.objects.new('CAM_library',d);s.collection.objects.link(o);o.location=(10,-14,9);o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler();s.camera=o
 for a in bpy.context.screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
 tmp=file.with_name(file.stem+'-packaged.blend')
 bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True)
 import os
 os.replace(tmp,file)
 if file.parent.name=='kits':
  import io_scene_gltf2
  fmt=next(i[0] for i in io_scene_gltf2.get_format_items(None,bpy.context) if i[0]=='GLB')
  bpy.ops.export_scene.gltf(filepath=str(R/'export/kits'/(file.stem+'.glb')),export_format=fmt,use_active_scene=True,export_extras=True,export_apply=True,export_animations=False)
print('24 site and kit files packaged')
