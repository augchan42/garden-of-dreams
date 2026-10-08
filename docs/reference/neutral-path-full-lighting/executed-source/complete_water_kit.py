"""Build all specified water modules at local origins, with 40% LOD companions."""
import bpy, math, ast, json
from pathlib import Path
from mathutils import Vector
import io_scene_gltf2
R=Path(__file__).resolve().parents[1]
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','roofmat':'rooftile','water':'water','leafmat':'foliage_card'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
fmt=next(i[0] for i in io_scene_gltf2.get_format_items(None,bpy.context) if i[0]=='GLB')
out=R/'export/kits/water';out.mkdir(parents=True,exist_ok=True)
manifest={'units':'metres','variants':{}}
collections=[];scenes=[]
def band(name,x0,x1,ys,top,bottom,material):
 vs=[]
 for y in ys:vs.extend([(x0,y,bottom(y)),(x1,y,bottom(y)),(x0,y,top(y)),(x1,y,top(y))])
 fs=[(0,2,3,1)]
 for j in range(len(ys)-1):
  a=j*4;b=a+4
  fs.extend([(a+2,a+3,b+3,b+2),(a,b,b+1,a+1),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 a=4*(len(ys)-1);fs.append((a,a+1,a+3,a+2))
 return mesh(name,vs,fs,material)
def manual_lod(variant):
 if variant=='embankment':
  # Keep an intact wall silhouette with a coplanar face grid for the shared UV layout.
  vs=[];fs=[]
  for y in [-.275,.275]:
   for j in range(4):
    for i in range(9):vs.append((-1.5+i*3/8,y,.02+j*.84/3))
  for side in range(2):
   for j in range(3):
    for i in range(8):
     a=side*36+j*9+i;face=(a,a+1,a+10,a+9);fs.append(face if side==0 else tuple(reversed(face)))
  fs.extend([(0,27,63,36),(8,44,71,35),(0,36,44,8),(27,35,71,63)])
  mesh('KIT_water_embankment_lod',vs,fs,stone)
  box('KIT_water_coping_lod',(0,0,.92),(3,.68,.13),stone)
 elif variant=='stone_bridge':
  rise=lambda y:.5*math.sin(math.pi*(y+3)/6)
  ys=[-3+j*.6 for j in range(11)]
  band('KIT_water_deck_lod',-.9,.9,ys,rise,lambda y:rise(y)-.28,stone)
  for x in [-.9,.9]:band('KIT_water_parapet_lod',x-.11,x+.11,ys,lambda y:rise(y)+.88,rise,stone)
  for y in [-2.8,2.8]:box('KIT_water_abutment_lod',(0,y,-.38),(2.2,.4,.5),stone)
 else:
  band('KIT_water_deck_lod',-.9,.9,[-3+j*.6 for j in range(11)],lambda y:0,lambda y:-.1,wood)
  for x in [-.73,.73]:box('KIT_water_stringer_lod',(x,0,-.18),(.16,6,.2),wood)
  for x in [-.86,.86]:
   for y in [-3,-1.5,0,1.5,3]:cyl('KIT_water_post_lod',(x,y,.5),.045,1,wood,4)
   for z in [.48,.95]:
    o=cyl('KIT_water_rail_lod',(0,0,0),.03,6,wood,4)
    o.location=(x,0,z);o.rotation_euler=Vector((0,1,0)).to_track_quat('Z','Y').to_euler()
variants=['stream','pond','embankment','lotus','wood_bridge','stone_bridge']
for variant in variants:
 scene=bpy.data.scenes.new('Water '+variant);scenes.append(scene);bpy.context.window.scene=scene
 scene.unit_settings.system='METRIC'
 C=bpy.data.collections.new('KIT_water_'+variant);scene.collection.children.link(C);collections.append(C)
 ports=[]
 if variant in ['stream','pond']:
  nx,ny=(8,16) if variant=='stream' else (16,16)
  w,l=(3,6) if variant=='stream' else (6,6)
  vs=[(-w/2+w*i/nx,-l/2+l*j/ny,0) for j in range(ny+1) for i in range(nx+1)]
  fs=[]
  for j in range(ny):
   for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
  mesh('KIT_water_surface',vs,fs,water)
  # Water is decorative and must never become an invisible walking floor.
 elif variant=='embankment':
  for row in range(3):
   for i in range(6):
    x=-1.25+i*.5
    box('KIT_water_masonry',(x,0,.15+row*.28),(.485,.55,.265),stone)
  for i in range(6):box('KIT_water_coping',(-1.25+i*.5,0,.92),(.49,.68,.13),stone)
  collision('water_embankment',(0,0,.5),(3,.68,1))
 elif variant=='lotus':
  for i,(x,y,r) in enumerate([(-.6,-.3,.34),(.05,-.45,.3),(.55,-.1,.36),(-.4,.4,.4),(.35,.45,.38),(0,.05,.25)]):
   n=20;z=.025+(i%3)*.018
   vs=[(x,y,z)]+[(x+r*math.cos(.12+j*(math.tau-.24)/n),y+r*math.sin(.12+j*(math.tau-.24)/n),z+.012*math.sin(j*1.7)) for j in range(n+1)]
   fs=[(0,j+1,j+2) for j in range(n)]
   mesh('KIT_water_lotus_leaf',vs,fs,leafmat)
   # Radial veins follow the leaf surface and preserve the characteristic slit.
   for j in [3,7,11,15]:
    a=.12+j*(math.tau-.24)/n
    beam('KIT_water_lotus_vein',(x,y,z+.008),(x+r*.85*math.cos(a),y+r*.85*math.sin(a),z+.008),.004,leafmat)
 elif variant=='wood_bridge':
  for j in range(24):box('KIT_water_plank',(0,-2.875+j*.25,-.05),(1.8,.242,.1),wood)
  for x in [-.73,.73]:box('KIT_water_stringer',(x,0,-.18),(.16,6,.2),wood)
  for x in [-.86,.86]:
   for y in [-3,-1.5,0,1.5,3]:cyl('KIT_water_post',(x,y,.5),.045,1,wood,8)
   for z in [.48,.95]:beam('KIT_water_rail',(x,-3,z),(x,3,z),.03,wood)
   collision('water_bridge_side',(x,0,.5),(.1,6,1))
  collision('water_bridge_deck',(0,0,-.1),(1.8,6,.2))
  ports=[('south',(0,-3,0)),('north',(0,3,0))]
 else:
  rise=lambda y:.5*math.sin(math.pi*(y+3)/6)
  ys=[-3+j*.5 for j in range(13)]
  band('KIT_water_stone_deck',-.9,.9,ys,rise,lambda y:rise(y)-.28,stone)
  for x in [-.9,.9]:
   for j in range(12):
    y=-2.75+j*.5
    block=box('KIT_water_parapet',(x,y,rise(y)+.4),(.18,.49,.8),stone)
    cap=box('KIT_water_parapet_cap',(x,y,rise(y)+.84),(.24,.49,.08),stone)
   band('COL_water_bridge_side',x-.11,x+.11,ys,lambda y:rise(y)+.88,rise,None)
  band('COL_water_bridge_deck',-.9,.9,ys,rise,lambda y:rise(y)-.2,None)
  for y in [-2.8,2.8]:box('KIT_water_abutment',(0,y,-.38),(2.2,.4,.5),stone)
  ports=[('south',(0,-3,0)),('north',(0,3,0))]
 for name,p in ports:
  marker=empty('PORT_'+name,p);marker['connection']='water_bridge_1.8m';marker['elevation']=0
 # Join render pieces for reliable per-piece triangle and LOD budgets; colliders stay separate.
 bpy.ops.object.select_all(action='DESELECT')
 render=[o for o in C.objects if o.type=='MESH' and not o.name.startswith('COL_')]
 for o in render:o.select_set(True)
 bpy.context.view_layer.objects.active=render[0];bpy.ops.object.join();model=bpy.context.object;model.name='KIT_water_'+variant+'_render'
 for channel in ['UVMap','LightmapUV']:
  model.data.uv_layers.new(name=channel);model.data.uv_layers.active_index=len(model.data.uv_layers)-1
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 import sys
 if str(R/'scripts') not in sys.path:sys.path.insert(0,str(R/'scripts'))
 from pavilion_material import apply_atlas
 if variant in ['wood_bridge','stone_bridge','embankment']:apply_atlas(model,R)
 base_tris=sum(len(p.vertices)-2 for p in model.data.polygons)
 model['variant']=variant;model['lod_ratio']=1.0
 for o in C.objects:
  if o.name.startswith('COL_'):o.name+='-colonly';o.hide_render=False;o['collision_only']=True
 bpy.ops.export_scene.gltf(filepath=str(out/('KIT_water_'+variant+'.glb')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 # Independent LOD1 geometry with the same collision/connector transforms.
 lodscene=bpy.data.scenes.new('Water '+variant+' LOD1');scenes.append(lodscene)
 lodC=bpy.data.collections.new('KIT_water_'+variant+'_LOD1');lodscene.collection.children.link(lodC)
 for obj in C.objects:
  o=obj.copy()
  if o.type=='MESH':o.data=obj.data.copy()
  lodC.objects.link(o)
  if o==obj:raise AssertionError('LOD must be independent')
  if o.type=='MESH' and not o.name.startswith('COL_'):
   mod=o.modifiers.new('LOD1_40_percent','DECIMATE');mod.ratio=.4;mod.use_collapse_triangulate=True;o['lod_ratio']=.4
 bpy.context.window.scene=lodscene;bpy.context.view_layer.update()
 if variant in ['embankment','wood_bridge','stone_bridge']:
  original_C=C;C=lodC
  for o in list(C.objects):
   if o.type=='MESH' and not o.name.startswith('COL_'):bpy.data.objects.remove(o,do_unlink=True)
  manual_lod(variant)
  bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
  parts=[o for o in C.objects if o.type=='MESH' and not o.name.startswith('COL_')]
  for o in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();simplified=bpy.context.object
  simplified.name='KIT_water_'+variant+'_render_LOD1'
  for channel in ['UVMap','LightmapUV']:
   simplified.data.uv_layers.new(name=channel);simplified.data.uv_layers.active_index=len(simplified.data.uv_layers)-1
   bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
  apply_atlas(simplified,R)
  C=original_C

 lodmodel=next(o for o in lodC.objects if o.type=='MESH' and not o.name.startswith('COL_'))
 evaluated=lodmodel.evaluated_get(bpy.context.evaluated_depsgraph_get());lod_tris=sum(len(p.vertices)-2 for p in evaluated.data.polygons)
 bpy.ops.export_scene.gltf(filepath=str(out/('KIT_water_'+variant+'_LOD1.glb')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':base_tris,'triangles_lod1':lod_tris,'ratio':lod_tris/base_tris,'connectors':{name:list(p) for name,p in ports},'colliders':len([o for o in C.objects if o.name.startswith('COL_')]),'within_2000_triangle_target':base_tris<=2000}
 collections.append(lodC)
# The main kit file contains a showroom and every editable module scene.
gallery=bpy.data.scenes.new('Water kit showroom');bpy.context.window.scene=gallery
root=bpy.data.collections.new('KIT_water');gallery.collection.children.link(root)
# Collection instances preserve source origins while displaying modules separately.
kind=next(i.identifier for i in bpy.types.Object.bl_rna.properties['instance_type'].enum_items if i.identifier=='COLLECTION')
for index,C in enumerate(collections):
 o=bpy.data.objects.new(C.name,None);root.objects.link(o);o.instance_type=kind;o.instance_collection=C;o.location=((index//2)%3*8,(index//2)//3*8+(index%2)*18,0)
C=root
camera('CAM_water_gallery',(25,-30,32),(8,12,0),43)
gallery.camera=next(o for o in root.objects if o.type=='CAMERA')
light('LGT_water_preview',(3,-8,12),2.5,(.7,1,.7),'SUN',(6,2,0))
gallery.world=bpy.data.worlds.new('Water preview world');gallery.world.use_nodes=True
next(n for n in gallery.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.08,.1,.08,1)
gallery.render.resolution_x=1600;gallery.render.resolution_y=900;gallery.render.resolution_percentage=100
for col in collections:
 for o in col.objects:
  if o.name.startswith('COL_'):o.hide_render=True;o.hide_viewport=True
file=R/'blender/kits/KIT_water.blend'
bpy.data.libraries.write(str(file),set(scenes+[gallery]),fake_user=True,compress=True)
# Package a normal editable file, preserving all module scenes.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.scenes=src.scenes
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.name=='Water kit showroom')
temporary=file.with_name('KIT_water-packaged.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
import os
os.replace(temporary,file)
import shutil
for suffix in ['', '_LOD1']:
 shutil.copyfile(out/('KIT_water_wood_bridge'+suffix+'.glb'),R/'export/kits'/('KIT_water'+suffix+'.glb'))
(R/'export/kits/water/manifest.json').write_text(json.dumps(manifest,indent=2))
print('WATER_KIT_COMPLETE',json.dumps(manifest))
