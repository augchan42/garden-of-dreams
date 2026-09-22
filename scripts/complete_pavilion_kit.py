"""Build all specified pavilion modules at local origins, with 40% LOD companions."""
import bpy, math, ast, json
from pathlib import Path
from mathutils import Vector
import io_scene_gltf2
R=Path(__file__).resolve().parents[1]
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','roofmat':'rooftile','gold':'bronze'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
fmt=next(i[0] for i in io_scene_gltf2.get_format_items(None,bpy.context) if i[0]=='GLB')
out=R/'export/kits/pavilion';out.mkdir(parents=True,exist_ok=True)
manifest={'units':'metres','variants':{}}
collections=[];scenes=[]
def pavilion_roof(n):
 radius=3.55
 rings=[(radius,.2),(radius*.9,0),(radius*.61,.45),(radius*.25,1.25),(.06,1.5)]
 vs=[]
 for r,z in rings:
  vs.extend([(r*math.cos(i*math.tau/n+math.pi/4),r*math.sin(i*math.tau/n+math.pi/4),z) for i in range(n)])
 faces=[]
 for j in range(4):
  for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 faces.append(tuple(range(4*n,5*n)))
 mesh('KIT_pavilion_roof_shell',vs,faces,roofmat)
 # Underside closes the thin eave; visible timber rafters radiate from the centre.
 lower=[(x,y,z-.08) for x,y,z in vs]
 mesh('KIT_pavilion_roof_under',lower,[tuple(reversed(f)) for f in faces],wood)
 mesh('KIT_pavilion_fascia',vs[:n]+lower[:n],[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],wood)
 for i in range(n):
  for j in range(4):beam('KIT_pavilion_hip',vs[j*n+i],vs[(j+1)*n+i],.04,roofmat)
  beam('KIT_pavilion_rafter',(0,0,1.3),lower[i],.045,wood)
  k=(i+1)%n
  tangent=(Vector(vs[k])-Vector(vs[i])).normalized()*.023
  for column in range(1,8):
   verts=[]
   for j in range(5):
    p=Vector(vs[j*n+i]).lerp(Vector(vs[j*n+k]),column/8)
    verts.extend([tuple(p-tangent),tuple(p+Vector((0,0,.026))),tuple(p+tangent)])
   fs=[]
   for j in range(4):
    for t in range(2):a=j*3+t;fs.append((a,a+1,a+4,a+3))
   mesh('KIT_pavilion_tile_ridge',verts,fs,roofmat)
 cyl('KIT_pavilion_finial',(0,0,1.65),.12,.3,gold,12)
 # Simplified closed volume; authored at eave origin for mounting above posts.
 cv=[(radius*math.cos(i*math.tau/n+math.pi/4),radius*math.sin(i*math.tau/n+math.pi/4),-.08) for i in range(n)]+[(0,0,1.8)]
 mesh('COL_pavilion_roof',cv,[tuple(reversed(range(n)))]+[(i,(i+1)%n,n) for i in range(n)],None)
 for i in range(n):
  a=i*math.tau/n+math.pi/4
  ports.append(('post_'+str(i),(2.7*math.cos(a),2.7*math.sin(a),0)))
variants=['roof_hex','roof_square','post','bracket','eave_strip','bench']
for variant in variants:
 scene=bpy.data.scenes.new('Pavilion '+variant);scenes.append(scene);bpy.context.window.scene=scene
 scene.unit_settings.system='METRIC'
 C=bpy.data.collections.new('KIT_pavilion_'+variant);scene.collection.children.link(C);collections.append(C)
 ports=[]
 if variant.startswith('roof_'):pavilion_roof(6 if variant=='roof_hex' else 4)
 elif variant=='post':
  cyl('KIT_pavilion_post',(0,0,1.6),.1,3,wood,20)
  for z,r,h in [(.07,.22,.14),(.19,.17,.1),(.28,.13,.08),(3.02,.13,.1)]:cyl('KIT_pavilion_post_base',(0,0,z),r,h,stone if z<1 else wood,12)
  collision('pavilion_post',(0,0,1.55),(.23,.23,3.1))
  ports=[('base',(0,0,0)),('top',(0,0,3.1))]
 elif variant=='bracket':
  # Stacked alternating arms with bearing blocks at their tips.
  for level in range(3):
   span=.44+level*.2;z=.08+level*.14
   for axis in [0,1]:
    box('KIT_pavilion_bracket_arm',(0,0,z),(span,.13,.1) if axis==0 else (.13,span,.1),wood)
    for sign in [-1,1]:
     pos=(sign*(span/2-.055),0,z+.07) if axis==0 else (0,sign*(span/2-.055),z+.07)
     box('KIT_pavilion_bracket_block',pos,(.15,.15,.08),wood)
  collision('pavilion_bracket',(0,0,.24),(.84,.84,.48))
 elif variant=='eave_strip':
  for i in range(10):
   cx=-.54+i*.12;vs=[]
   for y in [-.28,.28]:
    for r in [.06,.045]:
     for j in range(7):
      a=j*math.pi/6;vs.append((cx+r*math.cos(a),y,r*math.sin(a)))
   fs=[]
   for j in range(6):
    fs.extend([(j,j+1,j+15,j+14),(j+7,j+21,j+22,j+8),(j,j+7,j+8,j+1),(j+14,j+15,j+22,j+21)])
   fs.extend([(0,14,21,7),(6,13,27,20)])
   mesh('KIT_pavilion_eave_tile',vs,fs,roofmat)
  collision('pavilion_eave',(0,0,.025),(1.2,.56,.07))
 elif variant=='bench':
  for y in [-.21,-.07,.07,.21]:box('KIT_pavilion_seat',(0,y,.48),(2.4,.125,.07),wood)
  for x in [-1.02,1.02]:
   for y in [-.19,.19]:box('KIT_pavilion_leg',(x,y,.23),(.11,.11,.46),wood)
   box('KIT_pavilion_seat_support',(x,0,.4),(.13,.55,.12),wood)
  for x in [-1.08,-.65,-.22,.22,.65,1.08]:
   beam('KIT_pavilion_back_support',(x,.22,.45),(x,.32,.76),.027,wood)
   beam('KIT_pavilion_back_support',(x,.32,.76),(x,.49,1.06),.027,wood)
  for y,z in [(.26,.59),(.36,.83),(.49,1.07)]:beam('KIT_pavilion_back_rail',(-1.2,y,z),(1.2,y,z),.045,wood)
  collision('pavilion_bench',(0,.12,.54),(2.4,.75,1.08))
 for name,p in ports:
  marker=empty('PORT_'+name,p);marker['connection']='pavilion_mount';marker['elevation']=p[2]
 # Join render pieces for reliable per-piece triangle and LOD budgets; colliders stay separate.
 bpy.ops.object.select_all(action='DESELECT')
 render=[o for o in C.objects if o.type=='MESH' and not o.name.startswith('COL_')]
 for o in render:
  if variant.startswith('roof_'):
   group=o.vertex_groups.new(name='LOD_detail')
   weight=1.0 if any(part in o.name for part in ['tile_ridge','hip','rafter']) else 0.0
   group.add(list(range(len(o.data.vertices))),weight,'REPLACE')
  o.select_set(True)
 bpy.context.view_layer.objects.active=render[0];bpy.ops.object.join();model=bpy.context.object;model.name='KIT_pavilion_'+variant+'_render'
 import bmesh
 bm=bmesh.new();bm.from_mesh(model.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(model.data);bm.free()
 for channel in ['UVMap','LightmapUV']:
  model.data.uv_layers.new(name=channel);model.data.uv_layers.active_index=len(model.data.uv_layers)-1
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 import sys
 if str(R/'scripts') not in sys.path:sys.path.insert(0,str(R/'scripts'))
 from pavilion_material import apply_atlas
 apply_atlas(model,R)
 base_tris=sum(len(p.vertices)-2 for p in model.data.polygons)
 model['variant']=variant;model['lod_ratio']=1.0
 for o in C.objects:
  if o.name.startswith('COL_'):o.name+='-colonly';o.hide_render=False;o['collision_only']=True
 bpy.ops.export_scene.gltf(filepath=str(out/('KIT_pavilion_'+variant+'.glb')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 # Independent LOD1 geometry with the same collision/connector transforms.
 lodscene=bpy.data.scenes.new('Pavilion '+variant+' LOD1');scenes.append(lodscene)
 lodC=bpy.data.collections.new('KIT_pavilion_'+variant+'_LOD1');lodscene.collection.children.link(lodC)
 for obj in C.objects:
  o=obj.copy()
  if o.type=='MESH':o.data=obj.data.copy()
  lodC.objects.link(o)
  if o==obj:raise AssertionError('LOD must be independent')
  if o.type=='MESH' and not o.name.startswith('COL_'):
   mod=o.modifiers.new('LOD1_40_percent','DECIMATE');mod.ratio=.4;mod.use_collapse_triangulate=True;o['lod_ratio']=.4
   if variant.startswith('roof_'):mod.vertex_group='LOD_detail';mod.vertex_group_factor=1.0
 bpy.context.window.scene=lodscene;bpy.context.view_layer.update()
 lodmodel=next(o for o in lodC.objects if o.type=='MESH' and not o.name.startswith('COL_'))
 evaluated=lodmodel.evaluated_get(bpy.context.evaluated_depsgraph_get());lod_tris=sum(len(p.vertices)-2 for p in evaluated.data.polygons)
 bpy.ops.export_scene.gltf(filepath=str(out/('KIT_pavilion_'+variant+'_LOD1.glb')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':base_tris,'triangles_lod1':lod_tris,'ratio':lod_tris/base_tris,'connectors':{name:list(p) for name,p in ports},'colliders':len([o for o in C.objects if o.name.startswith('COL_')]),'within_2000_triangle_target':base_tris<=2000}
 collections.append(lodC)
# The main kit file contains a showroom and every editable module scene.
gallery=bpy.data.scenes.new('Pavilion kit showroom');bpy.context.window.scene=gallery
root=bpy.data.collections.new('KIT_pavilion');gallery.collection.children.link(root)
# Collection instances preserve source origins while displaying modules separately.
kind=next(i.identifier for i in bpy.types.Object.bl_rna.properties['instance_type'].enum_items if i.identifier=='COLLECTION')
for index,C in enumerate(collections):
 o=bpy.data.objects.new(C.name,None);root.objects.link(o);o.instance_type=kind;o.instance_collection=C;o.location=((index//2)%3*8,(index//2)//3*6+(index%2)*14,0)
C=root
camera('CAM_pavilion_gallery',(24,-27,30),(8,10,0),44)
gallery.camera=next(o for o in root.objects if o.type=='CAMERA')
light('LGT_pavilion_preview',(3,-8,12),2.5,(.7,1,.7),'SUN',(6,2,0))
gallery.world=bpy.data.worlds.new('Pavilion preview world');gallery.world.use_nodes=True
next(n for n in gallery.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.08,.1,.08,1)
gallery.render.resolution_x=1600;gallery.render.resolution_y=900;gallery.render.resolution_percentage=100
for col in collections:
 for o in col.objects:
  if o.name.startswith('COL_'):o.hide_render=True;o.hide_viewport=True
file=R/'blender/kits/KIT_pavilion.blend'
bpy.data.libraries.write(str(file),set(scenes+[gallery]),fake_user=True,compress=True)
# Package a normal editable file, preserving all module scenes.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.scenes=src.scenes
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.name=='Pavilion kit showroom')
temporary=file.with_name('KIT_pavilion-packaged.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
import os
os.replace(temporary,file)
import shutil
for suffix in ['', '_LOD1']:
 shutil.copyfile(out/('KIT_pavilion_roof_hex'+suffix+'.glb'),R/'export/kits'/('KIT_pavilion'+suffix+'.glb'))
(R/'export/kits/pavilion/manifest.json').write_text(json.dumps(manifest,indent=2))
print('PAVILION_KIT_COMPLETE',json.dumps(manifest))
