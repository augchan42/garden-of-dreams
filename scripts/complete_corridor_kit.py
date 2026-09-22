"""Build all specified corridor modules at local origins, with 40% LOD companions."""
import bpy, math, ast, json
from pathlib import Path
from mathutils import Vector
import io_scene_gltf2
R=Path(__file__).resolve().parents[1]
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','roofmat':'rooftile'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
fmt=next(i[0] for i in io_scene_gltf2.get_format_items(None,bpy.context) if i[0]=='GLB')
out=R/'export/kits/corridor';out.mkdir(parents=True,exist_ok=True)
manifest={'units':'metres','connector_clear_width':1.8,'variants':{}}
collections=[];scenes=[]
def slab(name,poly,top=0,bottom=-.2):
 vs=[(x,y,bottom) for x,y in poly]+[(x,y,top) for x,y in poly];n=len(poly)
 fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,stone)
def railing(a,b,rise):
 a=Vector((*a,rise(a[1])));b=Vector((*b,rise(b[1])))
 for h in [.4,.9]:beam('KIT_corridor_rail',a+Vector((0,0,h)),b+Vector((0,0,h)),.035,wood)
 n=max(2,int((b-a).length/.42))
 for j in range(n+1):
  p=a.lerp(b,j/n);beam('KIT_corridor_baluster',p+Vector((0,0,.15)),p+Vector((0,0,.88)),.022,wood)
 # Lattice back above the west balustrade, leaving the other side open.
 if abs(a.x+.86)<.02 and abs(b.x+.86)<.02:
  for h in [1.25,2.35]:beam('KIT_corridor_lattice_frame',a+Vector((0,0,h)),b+Vector((0,0,h)),.025,wood)
  for j in range(n):
   p=a.lerp(b,j/n);q=a.lerp(b,(j+1)/n)
   beam('KIT_corridor_lattice',p+Vector((0,0,1.3)),q+Vector((0,0,2.3)),.013,wood)
   beam('KIT_corridor_lattice',p+Vector((0,0,2.3)),q+Vector((0,0,1.3)),.013,wood)
 # A simplified full side collider keeps visitors behind rails.
 d=b-a;o=box('COL_corridor_side',(0,0,0),(.09,d.length,1),None)
 o.location=(a+b)/2+Vector((0,0,.5));o.rotation_euler=(d.to_track_quat('Y','Z')).to_euler();o.hide_render=True

def profile(v):
 v=abs(v)
 return 3.45-v*.65/.9 if v<=.9 else 2.8+(v-.9)*.5
for variant in ['straight','corner','tee','stair']:
 scene=bpy.data.scenes.new('Corridor '+variant);scenes.append(scene);bpy.context.window.scene=scene
 scene.unit_settings.system='METRIC'
 C=bpy.data.collections.new('KIT_corridor_'+variant);scene.collection.children.link(C);collections.append(C)
 rise=(lambda y:(y+1.5)*.2) if variant=='stair' else (lambda y:0)
 if variant in ['straight','stair']:
  poly=[(-.9,-1.5),(.9,-1.5),(.9,1.5),(-.9,1.5)]
  rails=[((-.86,-1.5),(-.86,1.5)),((.86,-1.5),(.86,1.5))]
  ports=[('south',(0,-1.5,0)),('north',(0,1.5,.6 if variant=='stair' else 0))]
 elif variant=='corner':
  poly=[(-.9,-1.5),(.9,-1.5),(.9,-.9),(1.5,-.9),(1.5,.9),(-.9,.9)]
  rails=[((-.86,-1.5),(-.86,.86)),((-.86,.86),(1.5,.86))]
  ports=[('south',(0,-1.5,0)),('east',(1.5,0,0))]
 else:
  poly=[(-.9,-1.5),(.9,-1.5),(.9,-.9),(1.5,-.9),(1.5,.9),(.9,.9),(.9,1.5),(-.9,1.5)]
  rails=[((-.86,-1.5),(-.86,1.5))]
  ports=[('south',(0,-1.5,0)),('north',(0,1.5,0)),('east',(1.5,0,0))]
 if variant=='stair':
  for j in range(6):box('KIT_corridor_tread',(0,-1.25+j*.5,(j+1)*.05-.1),(1.8,.5,(j+1)*.1+.2),stone)
  vs=[(x,y,z+rise(y)) for z in [-.2,0] for x,y in poly]
  o=mesh('COL_corridor_floor',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],None);o.hide_render=True
 else:
  slab('KIT_corridor_floor',poly)
  # Convex floor sections avoid concave collision hulls at branch junctions.
  for p,size in ([((0,0,-.1),(1.8,3,.2))] if variant=='straight' else ([((0,-.3,-.1),(1.8,2.4,.2)),((1.2,0,-.1),(.6,1.8,.2))] if variant=='corner' else [((0,0,-.1),(1.8,3,.2)),((1.2,0,-.1),(.6,1.8,.2))])):collision('corridor_floor',p,size)
 for a,b in rails:railing(a,b,rise)
 posts=[(-.86,-1.5),(.86,-1.5)]
 if variant=='corner':posts += [(-.86,.86),(1.5,.86)]
 if variant=='tee':posts += [(-.86,1.5),(.86,1.5)]
 for x,y in posts:
  z=rise(y);cyl('KIT_corridor_post',(x,y,z+1.45),.065,2.9,wood,8)
  box('KIT_corridor_bracket',(x,y,z+2.8),(.36,.28,.12),wood)
  collision('corridor_post',(x,y,z+1.45),(.15,.15,2.9))
 # A single gridded roof surface follows merged branch ridges without intersecting shells.
 xs=[-1.2,-.9,0,.9,1.2]+([1.65] if variant in ['corner','tee'] else [])
 ys=[-1.65,-1.2,-.9,0,.9,1.2]+([] if variant=='corner' else [1.65])
 def contains(x,y):
  if variant in ['straight','stair']:return abs(x)<=1.2 and abs(y)<=1.65
  return (abs(x)<=1.2 and (y<=0 if variant=='corner' else True)) or (x>=0 and abs(y)<=1.2)
 def roof_z(x,y):
  values=[]
  if abs(x)<=1.2001 and (variant!='corner' or y<=.0001):values.append(profile(x))
  if variant in ['corner','tee'] and x>=-.0001 and abs(y)<=1.2001:values.append(profile(y))
  return max(values)+rise(max(-1.5,min(1.5,y)))
 vs=[];fs=[]
 for i in range(len(xs)-1):
  for j in range(len(ys)-1):
   if not contains((xs[i]+xs[i+1])/2,(ys[j]+ys[j+1])/2):continue
   base=len(vs)
   for x,y in [(xs[i],ys[j]),(xs[i+1],ys[j]),(xs[i+1],ys[j+1]),(xs[i],ys[j+1])]:vs.append((x,y,roof_z(x,y)))
   fs.append((base,base+1,base+2,base+3))
 mesh('KIT_corridor_roof',vs,fs,roofmat)
 for name,p in ports:
  marker=empty('PORT_'+name,p);marker['connection']='corridor_1.8m';marker['elevation']=p[2]
 # Join render pieces for reliable per-piece triangle and LOD budgets; colliders stay separate.
 bpy.ops.object.select_all(action='DESELECT')
 render=[o for o in C.objects if o.type=='MESH' and not o.name.startswith('COL_')]
 for o in render:o.select_set(True)
 bpy.context.view_layer.objects.active=render[0];bpy.ops.object.join();model=bpy.context.object;model.name='KIT_corridor_'+variant+'_render'
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
 bpy.ops.export_scene.gltf(filepath=str(out/('KIT_corridor_'+variant+'.glb')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 # Independent LOD1 geometry with the same collision/connector transforms.
 lodscene=bpy.data.scenes.new('Corridor '+variant+' LOD1');scenes.append(lodscene)
 lodC=bpy.data.collections.new('KIT_corridor_'+variant+'_LOD1');lodscene.collection.children.link(lodC)
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
 bpy.ops.export_scene.gltf(filepath=str(out/('KIT_corridor_'+variant+'_LOD1.glb')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':base_tris,'triangles_lod1':lod_tris,'ratio':lod_tris/base_tris,'connectors':{name:list(p) for name,p in ports},'colliders':len([o for o in C.objects if o.name.startswith('COL_')]),'within_2000_triangle_target':base_tris<=2000}
 collections.append(lodC)
# The main kit file contains a showroom and every editable module scene.
gallery=bpy.data.scenes.new('Corridor kit showroom');bpy.context.window.scene=gallery
root=bpy.data.collections.new('KIT_corridor');gallery.collection.children.link(root)
# Collection instances preserve source origins while displaying modules separately.
kind=next(i.identifier for i in bpy.types.Object.bl_rna.properties['instance_type'].enum_items if i.identifier=='COLLECTION')
for index,C in enumerate(collections):
 o=bpy.data.objects.new(C.name,None);root.objects.link(o);o.instance_type=kind;o.instance_collection=C;o.location=((index//2)*4.5,(index%2)*5,0)
C=root
camera('CAM_corridor_gallery',(17,-17,15),(6.75,2,1),45)
gallery.camera=next(o for o in root.objects if o.type=='CAMERA')
light('LGT_corridor_preview',(3,-8,12),2.5,(.7,1,.7),'SUN',(6,2,0))
gallery.world=bpy.data.worlds.new('Corridor preview world');gallery.world.use_nodes=True
next(n for n in gallery.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.08,.1,.08,1)
gallery.render.resolution_x=1600;gallery.render.resolution_y=900;gallery.render.resolution_percentage=100
for col in collections:
 for o in col.objects:
  if o.name.startswith('COL_'):o.hide_render=True;o.hide_viewport=True
file=R/'blender/kits/KIT_corridor.blend'
bpy.data.libraries.write(str(file),set(scenes+[gallery]),fake_user=True,compress=True)
# Package a normal editable file, preserving all module scenes.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.scenes=src.scenes
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.name=='Corridor kit showroom')
temporary=file.with_name('KIT_corridor-packaged.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
import os
os.replace(temporary,file)
import shutil
for suffix in ['', '_LOD1']:
 shutil.copyfile(out/('KIT_corridor_straight'+suffix+'.glb'),R/'export/kits'/('KIT_corridor'+suffix+'.glb'))
(R/'export/kits/corridor/manifest.json').write_text(json.dumps(manifest,indent=2))
print('CORRIDOR_KIT_COMPLETE',json.dumps(manifest))
