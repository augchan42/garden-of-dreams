"""Build the eight specified flora modules with a shared atlas and independent LODs.
Run with Blender --background --python-exit-code 1 --python scripts/complete_flora_kit.py.
"""
import bpy, bmesh, math, json, random, shutil, sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from make_flora_atlas import CELLS
bpy.ops.wm.read_factory_settings(use_empty=True)
out=R/'export/kits/flora';out.mkdir(parents=True,exist_ok=True)
atlas=bpy.data.images.load(str(R/'textures/kits/flora/flora-basecolor.png'));atlas.pack()
mat=bpy.data.materials.new('MAT_flora_atlas');mat.use_nodes=True;mat.use_backface_culling=False
mat.surface_render_method='DITHERED'
nt=mat.node_tree;shader=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
shader.inputs['Roughness'].default_value=.85
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=atlas
nt.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
clip=nt.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.45
nt.links.new(tex.outputs['Alpha'],clip.inputs[0]);nt.links.new(clip.outputs[0],shader.inputs['Alpha'])

class Geometry:
 def __init__(self,quality=1):self.vertices=[];self.faces=[];self.uv=[];self.quality=quality
 def face(self,points,cell,uv=None):
  start=len(self.vertices);self.vertices.extend(points);self.faces.append(tuple(range(start,start+len(points))))
  i=CELLS[cell];x=i%4;y=i//4
  if uv is None:uv=[(0,0),(1,0),(1,1),(0,1)][:len(points)]
  self.uv.append([((x+.025+.95*u)/4,1-(y+.025+.95*(1-v))/4) for u,v in uv])
 def stem(self,a,b,r,cell='bark',n=8,tip=None):
  if self.quality<1:n=max(3,round((n-1)*self.quality+1))
  a=Vector(a);b=Vector(b);axis=(b-a).normalized();side=axis.cross(Vector((0,1,0)))
  if side.length<.01:side=axis.cross(Vector((1,0,0)))
  side.normalize();other=axis.cross(side);top=r if tip is None else tip
  lo=[a+r*(side*math.cos(j*math.tau/n)+other*math.sin(j*math.tau/n)) for j in range(n)]
  hi=[b+top*(side*math.cos(j*math.tau/n)+other*math.sin(j*math.tau/n)) for j in range(n)]
  for j in range(n):k=(j+1)%n;self.face([lo[j],lo[k],hi[k],hi[j]],cell)
  for ring,reverse in ([] if self.quality<1 and r<.025 else [(lo,True),(hi,False)]):
   for j in range(1,n-1):
    p=[ring[0],ring[j],ring[j+1]];self.face(list(reversed(p)) if reverse else p,cell,[(.1,.1),(.9,.1),(.5,.9)])
 def leaf(self,a,b,width,cell,segments=3,angle=0,bend=.08):
  segments=max(1,round(segments*self.quality))
  a=Vector(a);b=Vector(b);direction=(b-a).normalized();side=direction.cross(Vector((0,0,1)))
  if side.length<.01:side=Vector((1,0,0))
  side.normalize();side=side*math.cos(angle)+direction.cross(side)*math.sin(angle)
  rings=[]
  for j in range(segments+1):
   t=j/segments;p=a.lerp(b,t)+Vector((0,0,bend*math.sin(t*math.pi)))
   rings.append([p-side*width/2,p+side*width/2])
  for j in range(segments):self.face([*rings[j],rings[j+1][1],rings[j+1][0]],cell,[(0,j/segments),(1,j/segments),(1,(j+1)/segments),(0,(j+1)/segments)])
 def blossom(self,p,r,angle):
  p=Vector(p);u=Vector((math.cos(angle),math.sin(angle),0))*r;v=Vector((0,0,r))
  self.face([p-u-v,p+u-v,p+u+v,p-u+v],'blossom')
 def object(self,name,col):
  data=bpy.data.meshes.new(name);data.from_pydata(self.vertices,[],self.faces);data.update()
  data.materials.append(mat);uv=data.uv_layers.new(name='UVMap')
  for p,coords in zip(data.polygons,self.uv):
   for idx,co in zip(p.loop_indices,coords):uv.data[idx].uv=co
  # Weld adjacent stem and card faces while keeping each face's atlas UVs.
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.to_mesh(data);bm.free()
  o=bpy.data.objects.new(name,data);col.objects.link(o)
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  data.uv_layers.new(name='LightmapUV');data.uv_layers.active_index=1
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
  data.uv_layers.active_index=0;o.select_set(False)
  return o

def build_geometry(variant,index,quality=1):
 random.seed(83+index)
 g=Geometry(quality);collider=None
 if variant.startswith('bamboo'):
  n,height={'bamboo_small':(3,2.2),'bamboo_medium':(5,3.2),'bamboo_large':(7,4.3)}[variant]
  for i in range(n):
   a=i*2.399;x=.38*math.cos(a)*math.sqrt((i+1)/n);y=.38*math.sin(a)*math.sqrt((i+1)/n);h=height*(.8+random.random()*.2)
   for j in range(3):
    z0=h*j/3;z1=h*(j+1)/3;g.stem((x,y,z0),(x+.08*(j+1),y,z1),.032,'culm',6)
    p=Vector((x+.08*(j+1),y,z1));g.stem(p-Vector((0,0,.015)),p+Vector((0,0,.015)),.043,'culm',6)
    for k in range(6):
     angle=a+k*.72+j*.9;length=.42+random.random()*.28
     end=p+Vector((math.cos(angle)*length,math.sin(angle)*length,random.uniform(-.16,.24)))
     g.leaf(p,end,.18,'bamboo',3,angle=k*.3)
 elif variant in ('plum','willow'):
  willow=variant=='willow';h=2.65 if willow else 2.25
  g.stem((0,0,0),(.12,0,h),.13,'bark',10,.055);collider=(.26,h)
  count=7 if willow else 6
  for j in range(count):
   angle=j*math.tau/count;root=Vector((.08,0,h*.55));tip=Vector((math.cos(angle)*1.2,math.sin(angle)*1.2,h+random.uniform(-.2,.4)))
   mid=root.lerp(tip,.55)+Vector((0,0,.2));g.stem(root,mid,.045,'bark',6,.026);g.stem(mid,tip,.026,'bark',6,.01)
   if willow:
    for k in range(3):
     top=mid.lerp(tip,.4+k*.3);bottom=top-Vector((.12*math.cos(angle),.12*math.sin(angle),1.3))
     g.stem(top,bottom,.008,'bark',4,.003)
     for m in range(5):
      p=top.lerp(bottom,(m+.2)/5);end=p+Vector((.25*math.cos(angle+(m%2)*2),.25*math.sin(angle+(m%2)*2),-.22))
      g.leaf(p,end,.105,'willow',3,angle=.6)
   else:
    for k in range(7):
     p=mid.lerp(tip,.3+k*.1);a=angle+k*1.5
     g.leaf(p,p+Vector((.28*math.cos(a),.28*math.sin(a),.1)),.19,'plum',3,angle=k*.3)
     if k%2==0:g.blossom(p+Vector((.14*math.cos(a),.14*math.sin(a),.1)),.11,a)
 elif variant=='banana':
  for j in range(7):
   a=j*2.399;p=Vector((.12*math.cos(a),.12*math.sin(a),.8+random.random()*.45));tip=p+Vector((math.cos(a)*1.25,math.sin(a)*1.25,.4))
   g.stem((0,0,0),p,.035,'reed_stem',6,.018);g.leaf(p,tip,.6,'banana',8,angle=.12,bend=.38)
 elif variant=='reed':
  for j in range(14):
   a=j*2.399;r=.3*math.sqrt((j+1)/14);p=Vector((r*math.cos(a),r*math.sin(a),0));h=.95+random.random()*.65
   tip=p+Vector((.22*math.cos(a),.22*math.sin(a),h));g.stem(p,tip*.8,.008,'reed_stem',4,.004)
   g.leaf(p,tip,.12,'reed',7,angle=a*.4,bend=.1)
 else:
  # Open terracotta planter with a dark soil disk, rather than a solid top cap.
  n=16 if quality==1 else 6;bottom=[Vector((.21*math.cos(j*math.tau/n),.21*math.sin(j*math.tau/n),.02)) for j in range(n)]
  top=[Vector((.32*math.cos(j*math.tau/n),.32*math.sin(j*math.tau/n),.48)) for j in range(n)]
  inner=[Vector((.285*math.cos(j*math.tau/n),.285*math.sin(j*math.tau/n),.48)) for j in range(n)]
  for j in range(n):k=(j+1)%n;g.face([bottom[j],bottom[k],top[k],top[j]],'pot');g.face([top[j],top[k],inner[k],inner[j]],'pot');g.face([(0,0,.445),inner[j]-Vector((0,0,.035)),inner[k]-Vector((0,0,.035))],'soil',[(.5,.5),(0,0),(1,0)])
  collider=(.6,.48)
  for j in range(8):
   a=j*2.399;p=Vector((0,0,.45));tip=Vector((.5*math.cos(a),.5*math.sin(a),1.05+random.random()*.35));g.stem(p,tip,.014,'culm',6,.006);g.leaf(p.lerp(tip,.4),tip,.25,'plum',5,angle=.3)
 return g,collider

variants=['bamboo_small','bamboo_medium','bamboo_large','plum','willow','banana','reed','potted']
scenes=[];collections=[];manifest={'units':'metres','atlas':'flora-basecolor.png','atlas_size':2048,'variants':{}}
for index,variant in enumerate(variants):
 random.seed(83+index);s=bpy.data.scenes.new('Flora '+variant);s.unit_settings.system='METRIC';scenes.append(s);bpy.context.window.scene=s
 col=bpy.data.collections.new('KIT_flora_'+variant);s.collection.children.link(col);collections.append(col)
 g,collider=build_geometry(variant,index)
 model=g.object('KIT_flora_'+variant+'_render',col);model['variant']=variant;model['lod_ratio']=1.0
 marker=bpy.data.objects.new('PORT_ground',None);col.objects.link(marker);marker['connection']='plant_ground';marker['elevation']=0
 if collider:
  diameter,height=collider
  bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,height/2));o=bpy.context.object;o.name='COL_flora_'+variant+'-colonly';o.scale=(diameter,diameter,height)
  for old in list(o.users_collection):old.objects.unlink(o)
  col.objects.link(o);o['collision_only']=True
 base=sum(len(p.vertices)-2 for p in model.data.polygons)
 bpy.ops.export_scene.gltf(filepath=str(out/f'KIT_flora_{variant}.glb'),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 lodscene=bpy.data.scenes.new('Flora '+variant+' LOD1');scenes.append(lodscene);lodcol=bpy.data.collections.new(col.name+'_LOD1');lodscene.collection.children.link(lodcol);collections.append(lodcol)
 for obj in col.objects:
  o=obj.copy()
  if o.type=='MESH':o.data=obj.data.copy()
  lodcol.objects.link(o)
  if obj==model:
   bpy.data.objects.remove(o,do_unlink=True)
 bpy.context.window.scene=lodscene
 lodgeometry,_=build_geometry(variant,index,.4);lodmodel=lodgeometry.object('KIT_flora_'+variant+'_render_LOD1',lodcol);lodmodel['variant']=variant;lodmodel['lod_ratio']=.4
 bpy.context.view_layer.update();ev=lodmodel.evaluated_get(bpy.context.evaluated_depsgraph_get());lod=sum(len(p.vertices)-2 for p in ev.data.polygons)
 bpy.ops.export_scene.gltf(filepath=str(out/f'KIT_flora_{variant}_LOD1.glb'),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':base,'triangles_lod1':lod,'ratio':lod/base,'colliders':int(collider is not None),'connectors':{'ground':[0,0,0]}}
# Editable scene library and overview. Geometry remains at local origins in module scenes.
gallery=bpy.data.scenes.new('Flora kit showroom');bpy.context.window.scene=gallery
root=bpy.data.collections.new('KIT_flora');gallery.collection.children.link(root)
for index,col in enumerate(collections):
 o=bpy.data.objects.new(col.name,None);root.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=col;o.location=((index//2)%4*4,(index//2)//4*5+(index%2)*13,0)
 for obj in col.objects:
  if obj.name.startswith('COL_'):obj.hide_render=True;obj.hide_viewport=True
cam=bpy.data.cameras.new('CAM_flora');o=bpy.data.objects.new('CAM_flora',cam);root.objects.link(o);o.location=(15,-20,17);o.rotation_euler=(Vector((6,5,1.5))-o.location).to_track_quat('-Z','Y').to_euler();gallery.camera=o
sun=bpy.data.lights.new('LGT_flora_preview','SUN');sun.energy=2;sun.color=(1,.93,.84);o=bpy.data.objects.new(sun.name,sun);root.objects.link(o);o.rotation_euler=(.45,-.5,-.4)
gallery.world=bpy.data.worlds.new('Flora preview');gallery.world.use_nodes=True;gallery.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.28,.32,1)
gallery.render.resolution_x=1600;gallery.render.resolution_y=1000;gallery.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/kits/KIT_flora.blend'),compress=True)
shutil.copyfile(R/'textures/kits/flora/flora-basecolor.png',out/'flora-basecolor.png')
for suffix in ('','_LOD1'):shutil.copyfile(out/f'KIT_flora_bamboo_medium{suffix}.glb',R/f'export/kits/KIT_flora{suffix}.glb')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('FLORA_KIT_COMPLETE',json.dumps(manifest))
