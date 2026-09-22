"""Build six pierced plaster rock modules with collision and independent LODs."""
import bpy, bmesh, math, ast, json, sys, os, shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import io_scene_gltf2
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from pavilion_material import apply_atlas
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
stone=bpy.data.materials['MAT_plaster_rock']
fmt=next(i[0] for i in io_scene_gltf2.get_format_items(None,bpy.context) if i[0]=='GLB')
out=R/'export/kits/rockery';out.mkdir(parents=True,exist_ok=True)
manifest={'units':'metres','variants':{}};collections=[];scenes=[]
def normals(obj):
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
def drill(obj,x,z,radius):
 cutter=cyl('temporary_piercing',(0,0,0),radius,8,None,16)
 cutter.location=(x,0,z);cutter.rotation_euler.x=math.pi/2;cutter.scale.x=1.15
 mod=obj.modifiers.new('Pierced plaster','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
def standing(height,width,depth):
 n=18;levels=9;vs=[]
 for j in range(levels):
  z=height*j/(levels-1);factor=.72+.2*math.sin(j*(1.18+.04*height))+.07*math.cos(j*2.7)
  for k in range(n):
   a=k*math.tau/n;f=factor*(1+.1*math.sin(k*3+j*.7))
   vs.append((width*f*math.cos(a)+.07*width*math.sin(j),depth*f*math.sin(a),z))
 fs=[tuple(reversed(range(n))),tuple(range((levels-1)*n,levels*n))]
 fs += [(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(levels-1) for k in range(n)]
 return mesh('KIT_rockery_stone',vs,fs,stone)
def passage(length,slices):
 steps=20
 inner=[(-1.1,0)]+[(1.1*math.cos(math.pi-i*math.pi/steps)*(1+.035*math.sin(i*1.7)),1.5+1.1*math.sin(math.pi-i*math.pi/steps)+.055*math.sin(i*1.3)) for i in range(steps+1)]+[(1.1,0)]
 outer=[(-2.3,0)]+[(2.3*math.cos(math.pi-i*math.pi/steps)*(1+.12*math.sin(i*1.1)),1.6+1.9*math.sin(math.pi-i*math.pi/steps)+.23*math.sin(i*1.4)) for i in range(steps+1)]+[(2.3,0)]
 n=len(inner);vs=[];fs=[]
 for j in range(slices):
  y=-length/2+length*j/(slices-1)
  for ring in [inner,outer]:
   for i,(x,z) in enumerate(ring):
    bulge=math.sin(math.pi*j/(slices-1))*(.11*math.sin(i*.8+j*1.4)) if ring is outer else 0
    vs.append((x*(1+bulge),y,z*(1+bulge*.6)))
 for j in range(slices-1):
  a=j*2*n;b=a+2*n
  for i in range(n-1):fs.extend([(a+i,b+i,b+i+1,a+i+1),(a+n+i,a+n+i+1,b+n+i+1,b+n+i)])
  fs.extend([(a,a+n,b+n,b),(a+n-1,b+n-1,b+2*n-1,a+2*n-1)])
 for j in [0,slices-1]:
  a=j*2*n
  for i in range(n-1):fs.append((a+i,a+i+1,a+n+i+1,a+n+i))
 return mesh('KIT_rockery_passage',vs,fs,stone)
def cliff():
 nx,nz=18,10;vs=[];fs=[]
 for side in [0,1]:
  for j in range(nz+1):
   for i in range(nx+1):
    x=-3+6*i/nx;z=(3.6+.25*math.sin(i*.7)+.12*math.cos(i*1.6))*j/nz
    y=.4 if side else -.4-.18*math.sin(i*.9+j*.6)-.1*math.cos(j*1.4)
    vs.append((x,y,z))
 count=(nx+1)*(nz+1)
 for side in [0,1]:
  for j in range(nz):
   for i in range(nx):
    a=side*count+j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
 for j in range(nz):
  for i in [0,nx]:
   a=j*(nx+1)+i;fs.append((a,a+nx+1,a+nx+1+count,a+count))
 for i in range(nx):
  for j in [0,nz]:
   a=j*(nx+1)+i;fs.append((a,a+1,a+1+count,a+count))
 return mesh('KIT_rockery_cliff',vs,fs,stone)
variants=['small','medium','large','arch','tunnel','cliff']
for variant in variants:
 scene=bpy.data.scenes.new('Rockery '+variant);scenes.append(scene);bpy.context.window.scene=scene;scene.unit_settings.system='METRIC'
 C=bpy.data.collections.new('KIT_rockery_'+variant);scene.collection.children.link(C);collections.append(C)
 holes=[];ports=[]
 if variant in ['small','medium','large']:
  height,width,depth={'small':(1.1,.65,.42),'medium':(2.2,1,.65),'large':(3.3,1.4,.9)}[variant]
  model=standing(height,width,depth)
  holes={'small':[(0,.58,.17)],'medium':[(-.22,.65,.22),(.2,1.4,.23)],'large':[(-.35,.75,.28),(.36,1.65,.3),(-.2,2.65,.26)]}[variant]
 elif variant in ['arch','tunnel']:
  length=1.4 if variant=='arch' else 4
  model=passage(length,4 if variant=='arch' else 9)
  ports=[('front',(0,-length/2,0)),('back',(0,length/2,0))]
  if variant=='arch':holes=[(-1.75,1.15,.18),(1.7,.75,.18)]
 else:
  model=cliff();holes=[(-1.6,1.3,.3),(1.5,2.2,.35)]
 normals(model)
 for x,z,radius in holes:drill(model,x,z,radius)
 normals(model);model.name='KIT_rockery_'+variant+'_render'
 collider=model.copy();collider.data=model.data.copy();C.objects.link(collider)
 collider.name='COL_rockery_'+variant+'-colonly';collider.data.materials.clear();collider['collision_only']=True
 for name,p in ports:
  marker=empty('PORT_'+name,p);marker['connection']='rockery_passage_2.2m';marker['elevation']=0
 bpy.ops.object.select_all(action='DESELECT');model.select_set(True);bpy.context.view_layer.objects.active=model
 for channel in ['UVMap','LightmapUV']:
  model.data.uv_layers.new(name=channel);model.data.uv_layers.active_index=len(model.data.uv_layers)-1
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(30),island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 apply_atlas(model,R);base_tris=sum(len(p.vertices)-2 for p in model.data.polygons)
 assert 200<=base_tris<=2000,(variant,base_tris)
 model['variant']=variant;model['lod_ratio']=1.0
 bpy.ops.export_scene.gltf(filepath=str(out/f'KIT_rockery_{variant}.glb'),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 lodscene=bpy.data.scenes.new('Rockery '+variant+' LOD1');scenes.append(lodscene)
 lodC=bpy.data.collections.new('KIT_rockery_'+variant+'_LOD1');lodscene.collection.children.link(lodC);collections.append(lodC)
 for obj in C.objects:
  o=obj.copy()
  if o.type=='MESH':o.data=obj.data.copy()
  lodC.objects.link(o)
  if o.type=='MESH' and not o.name.startswith('COL_'):
   mod=o.modifiers.new('LOD1_40_percent','DECIMATE');mod.ratio=.4;mod.use_collapse_triangulate=True;o['lod_ratio']=.4
 bpy.context.window.scene=lodscene;bpy.context.view_layer.update()
 lodmodel=next(o for o in lodC.objects if o.type=='MESH' and not o.name.startswith('COL_'))
 evaluated=lodmodel.evaluated_get(bpy.context.evaluated_depsgraph_get());lod_tris=sum(len(p.vertices)-2 for p in evaluated.data.polygons)
 # Piercings must remain visibly open in both render LODs, not only in collision.
 for active,obj in [(scene,model),(lodscene,lodmodel)]:
  bpy.context.window.scene=active;bpy.context.view_layer.update()
  tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
  for x,z,radius in holes:
   assert tree.ray_cast(Vector((x,-5,z)),Vector((0,1,0)),10)[0] is None,(variant,'blocked piercing')
  if ports:
   for x in [-.65,0,.65]:
    for z in [.2,1,1.8]:assert tree.ray_cast(Vector((x,-5,z)),Vector((0,1,0)),10)[0] is None,(variant,'blocked passage')
 bpy.context.window.scene=lodscene
 bpy.ops.export_scene.gltf(filepath=str(out/f'KIT_rockery_{variant}_LOD1.glb'),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':base_tris,'triangles_lod1':lod_tris,'ratio':lod_tris/base_tris,'connectors':dict(ports),'holes':holes,'colliders':1,'render_piercing_rays_pass':True}
gallery=bpy.data.scenes.new('Rockery kit showroom');bpy.context.window.scene=gallery
root=bpy.data.collections.new('KIT_rockery');gallery.collection.children.link(root)
kind=next(i.identifier for i in bpy.types.Object.bl_rna.properties['instance_type'].enum_items if i.identifier=='COLLECTION')
for index,col in enumerate(collections):
 o=bpy.data.objects.new(col.name,None);root.objects.link(o);o.instance_type=kind;o.instance_collection=col
 o.location=((index//2)%3*7,(index//2)//3*7+(index%2)*17,0)
C=root;camera('CAM_rockery_gallery',(23,-28,24),(7,10,1.3),43);gallery.camera=next(o for o in root.objects if o.type=='CAMERA')
light('LGT_rockery_preview',(3,-8,12),2.5,(.7,1,.7),'SUN',(6,2,0))
gallery.world=bpy.data.worlds.new('Rockery preview world');gallery.world.use_nodes=True
next(n for n in gallery.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.08,.1,.08,1)
gallery.render.resolution_x=1600;gallery.render.resolution_y=900;gallery.render.resolution_percentage=100
for col in collections:
 for o in col.objects:
  if o.name.startswith('COL_'):o.hide_render=True;o.hide_viewport=True
file=R/'blender/kits/KIT_rockery.blend';bpy.data.libraries.write(str(file),set(scenes+[gallery]),fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.scenes=src.scenes
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.name=='Rockery kit showroom')
tmp=file.with_name('KIT_rockery-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
for suffix in ['', '_LOD1']:shutil.copyfile(out/f'KIT_rockery_medium{suffix}.glb',R/f'export/kits/KIT_rockery{suffix}.glb')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('ROCKERY_KIT_COMPLETE',json.dumps(manifest))
