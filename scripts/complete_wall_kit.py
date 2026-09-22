"""Build all specified wall modules at local origins, with 40% LOD companions."""
import bpy, math, ast, json
from pathlib import Path
from mathutils import Vector
import io_scene_gltf2
R=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(R/'scripts'))
from pavilion_material import apply_atlas
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'whitewash','roofmat':'rooftile'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
fmt=next(i[0] for i in io_scene_gltf2.get_format_items(None,bpy.context) if i[0]=='GLB')
out=R/'export/kits/wall';out.mkdir(parents=True,exist_ok=True)
manifest={'units':'metres','variants':{}}
collections=[];scenes=[]
def prism(name,poly,material):
 n=len(poly);vs=[(x,y,z) for y in [-.12,.12] for x,z in poly]
 fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,material)
def cap():
 # Closed tiled coping with repeated tile seams.
 prism('KIT_wall_cap',[(-1.55,2.6),(-1.55,2.68),(0,2.84),(1.55,2.68),(1.55,2.6)],roofmat)
 for i in range(25):box('KIT_wall_tile',(-1.5+i*.125,0,2.73),(.035,.34,.065),roofmat)
def opening(variant):
 if variant=='moon_gate':
  height=2.2
  def width(z):return math.sqrt(max(0,1.1**2-(z-1.1)**2))
 elif variant=='vase_gate':
  height=2.2
  profile=[(0,.65),(.2,.85),(.7,1.02),(1.1,.94),(1.5,.68),(1.8,.58),(2.05,.72),(2.2,.78)]
  def width(z):
   for (a,x),(b,y) in zip(profile,profile[1:]):
    if a<=z<=b:return x+(y-x)*(z-a)/(b-a)
   return profile[-1][1]
 else:
  height=2.15
  def width(z):return .85 if .8<=z<=2.15 else 0
 steps=44
 for i in range(steps):
  a=height*i/steps;b=height*(i+1)/steps
  wa=width(a);wb=width(b)
  for sign in [-1,1]:
   poly=[(sign*wa,a),(sign*1.5,a),(sign*1.5,b),(sign*wb,b)]
   prism('KIT_wall_plaster',poly,stone)
   w=max(wa,wb)
   collision('wall_side',(sign*(1.5+w)/2,0,(a+b)/2),(1.5-w,.24,b-a))
 box('KIT_wall_lintel',(0,0,(height+2.6)/2),(3,.24,2.6-height),stone)
 collision('wall_lintel',(0,0,(height+2.6)/2),(3,.24,2.6-height))
 if variant.startswith('window_'):
  # Timber frame around a through-opening; no opaque backing plane.
  for x in [-.85,.85]:box('KIT_wall_window_frame',(x,0,1.475),(.07,.3,1.42),wood)
  # Butt the horizontal rails against the jambs; overlapping corner faces
  # cause z-fighting and overlapping lightmap islands after site batching.
  for z in [.8,2.15]:box('KIT_wall_window_frame',(0,0,z),(1.63,.3,.07),wood)
  def line(a,b):beam('KIT_wall_lattice',(a[0],0,a[1]),(b[0],0,b[1]),.022,wood)
  pattern=variant[7:]
  if pattern=='square':
   for x in [-.55,-.275,0,.275,.55]:line((x,.84),(x,2.11))
   for z in [1.1,1.4,1.7,2]:line((-.81,z),(.81,z))
  elif pattern=='diamond':
   for sign in [-1,1]:
    for k in range(-4,5):
     points=[]
     for x in [-.81,.81]:
      z=sign*x+k*.33+1.475
      if .84<=z<=2.11:points.append((x,z))
     for z in [.84,2.11]:
      x=(z-k*.33-1.475)/sign
      if -.81<=x<=.81:points.append((x,z))
     if len(points)==2:line(*points)
  elif pattern=='ice':
   for a,b in [((-.81,1.1),(.81,1.85)),((-.81,1.85),(.81,1.2)),((-.4,.84),(-.2,2.11)),((.6,.84),(.15,2.11)),((-.81,1.5),(-.25,1.75)),((.38,1.45),(.81,2.05))]:line(a,b)
  else:
   for cx,cz in [(-.43,1.16),(.43,1.16),(0,1.78)]:
    ring=[(cx+.33*math.cos(i*math.pi/3),cz+.29*math.sin(i*math.pi/3)) for i in range(6)]
    for a,b in zip(ring,ring[1:]+ring[:1]):line(a,b)
   line((-.81,1.16),(.81,1.16));line((0,.84),(0,2.11))
  collision('wall_window',(0,0,1.475),(1.7,.24,1.35))
variants=['bay','moon_gate','vase_gate','window_square','window_diamond','window_ice','window_hex','roof_cap']
for variant in variants:
 scene=bpy.data.scenes.new('Wall '+variant);scenes.append(scene);bpy.context.window.scene=scene
 scene.unit_settings.system='METRIC'
 C=bpy.data.collections.new('KIT_wall_'+variant);scene.collection.children.link(C);collections.append(C)
 ports=[]
 if variant=='bay':
  # Segmented render face retains shape under the shared LOD pass.
  for i in range(16):box('KIT_wall_bay',(-1.40625+i*.1875,0,1.3),(.1875,.24,2.6),stone)
  collision('wall_bay',(0,0,1.3),(3,.24,2.6))
 elif variant!='roof_cap':opening(variant)
 cap()
 if variant=='roof_cap':collision('wall_cap',(0,0,2.69),(3.1,.34,.18))
 if variant in ['moon_gate','vase_gate']:ports=[('front',(0,-.5,0)),('back',(0,.5,0))]
 for name,p in ports:
  marker=empty('PORT_'+name,p);marker['connection']='wall_gate';marker['elevation']=0
 # One static collision mesh per module, preserving the actual gate aperture.
 if variant not in ['bay','roof_cap']:
  for o in list(C.objects):
   if o.name.startswith('COL_'):bpy.data.objects.remove(o,do_unlink=True)
  if variant.startswith('window_'):
   collision('wall_window',(0,0,1.3),(3,.24,2.6))
  else:
   bpy.ops.object.select_all(action='DESELECT')
   copies=[]
   for o in list(C.objects):
    if o.name.startswith(('KIT_wall_plaster','KIT_wall_lintel')):
     clone=o.copy();clone.data=o.data.copy();C.objects.link(clone);copies.append(clone)
   for o in copies:o.select_set(True)
   bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join()
   collider=bpy.context.object;collider.name='COL_wall_gate';collider.data.materials.clear()
   import bmesh
   bm=bmesh.new();bm.from_mesh(collider.data)
   groups={}
   for f in bm.faces:
    key=tuple(sorted(tuple(round(v,5) for v in vert.co) for vert in f.verts))
    groups.setdefault(key,[]).append(f)
   bmesh.ops.delete(bm,geom=[f for faces in groups.values() if len(faces)==2 for f in faces],context='FACES_ONLY')
   bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
   bmesh.ops.dissolve_limit(bm,angle_limit=.001,verts=list(bm.verts),edges=list(bm.edges))
   bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
   bm.to_mesh(collider.data);bm.free()
 # Join render pieces for reliable per-piece triangle and LOD budgets; colliders stay separate.
 bpy.ops.object.select_all(action='DESELECT')
 render=[o for o in C.objects if o.type=='MESH' and not o.name.startswith('COL_')]
 for o in render:o.select_set(True)
 bpy.context.view_layer.objects.active=render[0];bpy.ops.object.join();model=bpy.context.object;model.name='KIT_wall_'+variant+'_render'
 # Remove paired internal segment faces before welding and simplifying.
 import bmesh
 bm=bmesh.new();bm.from_mesh(model.data)
 groups={}
 for f in bm.faces:
  key=tuple(sorted(tuple(round(v,5) for v in vert.co) for vert in f.verts))
  groups.setdefault(key,[]).append(f)
 internal=[f for faces in groups.values() if len(faces)==2 for f in faces]
 bmesh.ops.delete(bm,geom=internal,context='FACES_ONLY')
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 bm.to_mesh(model.data);bm.free()
 for channel in ['UVMap','LightmapUV']:
  model.data.uv_layers.new(name=channel);model.data.uv_layers.active_index=len(model.data.uv_layers)-1
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 apply_atlas(model,R,'wall')
 base_tris=sum(len(p.vertices)-2 for p in model.data.polygons)
 model['variant']=variant;model['lod_ratio']=1.0
 for o in C.objects:
  if o.name.startswith('COL_'):o.name+='-colonly';o.hide_render=False;o['collision_only']=True
 bpy.ops.export_scene.gltf(filepath=str(out/('KIT_wall_'+variant+'.glb')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 # Independent LOD1 geometry with the same collision/connector transforms.
 lodscene=bpy.data.scenes.new('Wall '+variant+' LOD1');scenes.append(lodscene)
 lodC=bpy.data.collections.new('KIT_wall_'+variant+'_LOD1');lodscene.collection.children.link(lodC)
 for obj in C.objects:
  o=obj.copy()
  if o.type=='MESH':o.data=obj.data.copy()
  lodC.objects.link(o)
  if o==obj:raise AssertionError('LOD must be independent')
  if o.type=='MESH' and not o.name.startswith('COL_'):
   mod=o.modifiers.new('LOD1_40_percent','DECIMATE');mod.ratio=.4;mod.use_collapse_triangulate=True;o['lod_ratio']=.4
 bpy.context.window.scene=lodscene;bpy.context.view_layer.update()
 lodmodel=next(o for o in lodC.objects if o.type=='MESH' and not o.name.startswith('COL_'))
 evaluated=lodmodel.evaluated_get(bpy.context.evaluated_depsgraph_get());lod_tris=sum(len(p.vertices)-2 for p in evaluated.data.polygons)
 bpy.ops.export_scene.gltf(filepath=str(out/('KIT_wall_'+variant+'_LOD1.glb')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':base_tris,'triangles_lod1':lod_tris,'ratio':lod_tris/base_tris,'connectors':{name:list(p) for name,p in ports},'colliders':len([o for o in C.objects if o.name.startswith('COL_')]),'within_2000_triangle_target':base_tris<=2000}
 collections.append(lodC)
# The main kit file contains a showroom and every editable module scene.
gallery=bpy.data.scenes.new('Wall kit showroom');bpy.context.window.scene=gallery
root=bpy.data.collections.new('KIT_wall');gallery.collection.children.link(root)
# Collection instances preserve source origins while displaying modules separately.
kind=next(i.identifier for i in bpy.types.Object.bl_rna.properties['instance_type'].enum_items if i.identifier=='COLLECTION')
for index,C in enumerate(collections):
 o=bpy.data.objects.new(C.name,None);root.objects.link(o);o.instance_type=kind;o.instance_collection=C;o.location=((index//2)%4*4,(index//2)//4*4+(index%2)*9,0)
C=root
camera('CAM_wall_gallery',(19,-24,22),(6,6,1),43)
gallery.camera=next(o for o in root.objects if o.type=='CAMERA')
light('LGT_wall_preview',(3,-8,12),2.5,(.7,1,.7),'SUN',(6,2,0))
gallery.world=bpy.data.worlds.new('Wall preview world');gallery.world.use_nodes=True
next(n for n in gallery.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.08,.1,.08,1)
gallery.render.resolution_x=1600;gallery.render.resolution_y=900;gallery.render.resolution_percentage=100
for col in collections:
 for o in col.objects:
  if o.name.startswith('COL_'):o.hide_render=True;o.hide_viewport=True
file=R/'blender/kits/KIT_wall.blend'
bpy.data.libraries.write(str(file),set(scenes+[gallery]),fake_user=True,compress=True)
# Package a normal editable file, preserving all module scenes.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.scenes=src.scenes
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.name=='Wall kit showroom')
temporary=file.with_name('KIT_wall-packaged.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
import os
os.replace(temporary,file)
import shutil
for suffix in ['', '_LOD1']:
 shutil.copyfile(out/('KIT_wall_bay'+suffix+'.glb'),R/'export/kits'/('KIT_wall'+suffix+'.glb'))
(R/'export/kits/wall/manifest.json').write_text(json.dumps(manifest,indent=2))
print('WALL_KIT_COMPLETE',json.dumps(manifest))
