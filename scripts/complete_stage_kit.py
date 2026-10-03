"""Build seven stage modules and semantic LODs without changing the garden assembly."""
import bpy,math,json,sys,shutil,io_scene_gltf2
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from kit_geometry import Geometry
from make_stage_art import CELLS
bpy.ops.wm.read_factory_settings(use_empty=True)
fmt=next(i[0] for i in io_scene_gltf2.get_format_items(None,bpy.context) if i[0]=='GLB')
def material(name):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.use_backface_culling=True
 return m,next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
atlas,bs=material('MAT_stage_atlas');nt=atlas.node_tree
for key in ['basecolor','orm']:
 node=nt.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(R/f'textures/kits/stage/stage-{key}.png'));node.image.pack()
 if key=='basecolor':nt.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 else:
  node.image.colorspace_settings.name='Non-Color';sep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(node.outputs['Color'],sep.inputs['Color']);nt.links.new(sep.outputs['Green'],bs.inputs['Roughness']);nt.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
black,bs=material('MAT_stage_backstage');bs.inputs['Base Color'].default_value=(0,0,0,1);bs.inputs['Roughness'].default_value=1
skies={}
for name in ['moonlit','dusk','mist']:
 m,bs=material('MAT_stage_cyclorama_'+name);node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(R/f'textures/kits/stage/cyclorama-{name}.png'));node.image.pack()
 m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(node.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.6;bs.inputs['Roughness'].default_value=1;skies[name]=m
fog,bs=material('MAT_stage_fog');fog.use_backface_culling=False;fog.surface_render_method='BLENDED';bs.inputs['Base Color'].default_value=(.5,.5,.5,1);bs.inputs['Roughness'].default_value=1
node=fog.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(R/'godot/materials/fog-mask.png'));node.image.pack();fog.node_tree.links.new(node.outputs['Alpha'],bs.inputs['Alpha'])
gel,bs=material('MAT_stage_gel');gel.use_backface_culling=False;gel.surface_render_method='BLENDED';bs.inputs['Base Color'].default_value=(.9,.55,.2,1);bs.inputs['Alpha'].default_value=.24;bs.inputs['Roughness'].default_value=.45

def build(variant,low):
 g=Geometry(atlas,CELLS);ports={'ground':(0,0,0)};colliders=[];front_faces=0
 if variant.startswith('cyclorama_'):
  n=16 if low else 40;rows=4
  def point(u,v,back=False):
   a=(u-.5)*1.44;return (14*math.sin(a),14*(1-math.cos(a))+(.08 if back else 0),v*7.5)
  for row in range(rows):
   for j in range(n):
    uv=[(j/n,row/rows),((j+1)/n,row/rows),((j+1)/n,(row+1)/rows),(j/n,(row+1)/rows)]
    g.face([point(u,v) for u,v in uv],'black');g.uv[-1]=uv
  front_faces=len(g.f)
  # Black painted back and sealed canvas edges; same silhouette at both levels.
  for j in range(n):
   u=j/n;v=(j+1)/n
   g.face([point(v,0,True),point(u,0,True),point(u,1,True),point(v,1,True)],'black')
   for height in [0,1]:g.face([point(u,height),point(v,height),point(v,height,True),point(u,height,True)],'black')
  for u in [0,1]:g.face([point(u,0),point(u,0,True),point(u,1,True),point(u,1)],'black')
  ports.update(left=point(0,0),right=point(1,0),wash=(0,-2,3.75))
  # Simplified faceted wall, separate from the painted render shell.
  for j in range(8):
   u=(j+.5)/8;a=(u-.5)*1.44;p=point(u,.5,True)
   colliders.append((p,(2.52,.18,7.5),(0,0,-a)))
 elif variant=='studio_wall':
  g.box((0,0,1.5),(3,.12,3),'black')
  for x in [-1.4,0,1.4]:g.box((x,.16,1.5),(.09,.2,3),'black')
  for z in ([.15,.6,1.1,1.6,2.1,2.65] if not low else [.15,1.5,2.65]):
   g.box((0,.18,z),(2.9,.09,.065),'black')
  # Exposed bolt heads only on the rear construction side.
  for x in [-1.4,1.4]:
   for z in [.15,1.5,2.65]:g.stem((x,.21,z),(x,.24,z),.022,'black',4 if low else 12)
  colliders=[((0,.05,1.5),(3,.3,3),(0,0,0))];ports.update(left=(-1.5,0,0),right=(1.5,0,0),top=(0,0,3))
 elif variant=='floor_boards':
  rows=6 if low else 15
  for j in range(rows):
   y=-1.5+(j+.5)*3/rows
   segments=2 if low else 3
   for k in range(segments):g.box((-1.5+(k+.5)*3/segments,y,-.025),(3/segments-.006,3/rows-.006,.05),'wood')
  for x in [-1.35,1.35]:
   for j in range(15):g.stem((x,-1.4+j*.2,-.002),(x,-1.4+j*.2,.001),.006,'steel',4 if low else 6)
  colliders=[((0,0,-.025),(3,3,.05),(0,0,0))];ports.update(left=(-1.5,0,0),right=(1.5,0,0),front=(0,-1.5,0),back=(0,1.5,0))
 elif variant=='fog_plane':
  n=6 if low else 10
  for j in range(n):
   for k in range(n):
    uv=[(k/n,j/n),((k+1)/n,j/n),((k+1)/n,(j+1)/n),(k/n,(j+1)/n)]
    g.face([(3*(u-.5),3*(v-.5),.3) for u,v in uv],'black');g.uv[-1]=uv
  front_faces=len(g.f);ports['layer']=(0,0,.3)
 elif variant=='gel_frame':
  for x in [-.5,.5]:g.case((x,0,.5),(.07,.07,1.07),'steel',1 if low else 4)
  for z in [0,1]:g.case((0,0,z),(1,.07,.07),'steel',1 if low else 4)
  for x in [-.45,.45]:g.stem((x,0,1.035),(x,0,1.16),.018,'brass',6 if low else 12)
  front_faces=len(g.f);n=6 if low else 8
  for j in range(n):
   for k in range(n):
    uv=[(k/n,j/n),((k+1)/n,j/n),((k+1)/n,(j+1)/n),(k/n,(j+1)/n)]
    g.face([((u-.5)*.93,0,.035+v*.93) for u,v in uv],'black')
  colliders=[((0,0,.55),(1.07,.09,1.2),(0,0,0))];ports.update(hang=(0,0,1.16),light=(0,-.05,.5),left=(-.5,0,.5),right=(.5,0,.5))
 else:raise ValueError(variant)
 return g,ports,colliders,front_faces

variants=['cyclorama_moonlit','cyclorama_dusk','cyclorama_mist','studio_wall','floor_boards','fog_plane','gel_frame']
out=R/'export/kits/stage';manifest={'units':'metres','atlas_size':2048,'cyclorama_size':4096,'variants':{}};collections=[]
for variant in variants:
 counts=[]
 for suffix,low in [('',False),('_LOD1',True)]:
  scene=bpy.data.scenes.new('Stage '+variant+suffix);scene.unit_settings.system='METRIC';bpy.context.window.scene=scene
  col=bpy.data.collections.new('KIT_stage_'+variant+suffix);scene.collection.children.link(col);collections.append(col)
  g,ports,colliders,front_faces=build(variant,low);model=g.object('KIT_stage_'+variant+'_render'+suffix,col);model['variant']=variant
  if variant.startswith('cyclorama_'):
   model.data.materials.clear();model.data.materials.append(skies[variant.removeprefix('cyclorama_')]);model.data.materials.append(atlas)
   for p in model.data.polygons:p.material_index=0 if p.index<front_faces else 1
  elif variant=='studio_wall':model.data.materials.clear();model.data.materials.append(black)
  elif variant=='fog_plane':model.data.materials.clear();model.data.materials.append(fog)
  elif variant=='gel_frame':
   model.data.materials.append(gel)
   for p in model.data.polygons:p.material_index=0 if p.index<front_faces else 1
  for port,position in ports.items():
   o=bpy.data.objects.new('PORT_'+port,None);o.location=position;o['connection']='stage_mount';col.objects.link(o)
  for j,(position,size,rotation) in enumerate(colliders):
   bpy.ops.mesh.primitive_cube_add(size=1,location=position);o=bpy.context.object;o.name='COL_stage_'+variant+'_'+str(j)+suffix+'-colonly';o.scale=size;o.rotation_euler=rotation;o['collision_only']=True
   for old in list(o.users_collection):old.objects.unlink(o)
   col.objects.link(o)
  counts.append(sum(len(p.vertices)-2 for p in model.data.polygons));model['lod_ratio']=counts[-1]/counts[0]
  bpy.ops.export_scene.gltf(filepath=str(out/f'KIT_stage_{variant}{suffix}.glb'),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':counts[0],'triangles_lod1':counts[1],'ratio':counts[1]/counts[0],'connectors':ports,'colliders':len(colliders),'surfaces':len(model.data.materials)}
gallery=bpy.data.scenes.new('Stage kit showroom');bpy.context.window.scene=gallery;root=bpy.data.collections.new('KIT_stage');gallery.collection.children.link(root)
for index,col in enumerate(collections):
 o=bpy.data.objects.new(col.name,None);root.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=col;o.location=((index//2)%3*24,(index//2)//3*14+(index%2)*48,0)
 for obj in col.objects:
  if obj.name.startswith('COL_'):obj.hide_render=True;obj.hide_viewport=True
cam=bpy.data.cameras.new('CAM_stage_gallery');o=bpy.data.objects.new(cam.name,cam);root.objects.link(o);o.location=(25,-45,25);o.rotation_euler=(Vector((24,14,3))-o.location).to_track_quat('-Z','Y').to_euler();gallery.camera=o
sun=bpy.data.lights.new('LGT_stage_preview','SUN');sun.energy=1.5;o=bpy.data.objects.new(sun.name,sun);root.objects.link(o);o.rotation_euler=(.5,-.5,-.4)
gallery.world=bpy.data.worlds.new('Stage preview world');gallery.world.use_nodes=True;gallery.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.18,1)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/kits/KIT_stage.blend'),compress=True)
for suffix in ['','_LOD1']:shutil.copyfile(out/f'KIT_stage_cyclorama_moonlit{suffix}.glb',R/f'export/kits/KIT_stage{suffix}.glb')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('STAGE_KIT_COMPLETE',json.dumps(manifest))
