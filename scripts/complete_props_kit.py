"""Build the complete prop library with one PBR atlas and semantic LODs."""
import bpy,bmesh,math,json,shutil,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from make_props_atlas import CELLS
bpy.ops.wm.read_factory_settings(use_empty=True)
material=bpy.data.materials.new('MAT_props_atlas');material.use_nodes=True;material.use_backface_culling=True
nt=material.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
textures={}
for key in ['basecolor','orm','emission']:
 node=nt.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(R/f'textures/kits/props/props-{key}.png'));node.image.pack()
 if key=='orm':node.image.colorspace_settings.name='Non-Color'
 textures[key]=node
nt.links.new(textures['basecolor'].outputs['Color'],bsdf.inputs['Base Color'])
channels=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(textures['orm'].outputs['Color'],channels.inputs['Color'])
nt.links.new(channels.outputs['Green'],bsdf.inputs['Roughness']);nt.links.new(channels.outputs['Blue'],bsdf.inputs['Metallic'])
nt.links.new(textures['emission'].outputs['Color'],bsdf.inputs['Emission Color']);bsdf.inputs['Emission Strength'].default_value=1.0
class Geometry:
 def __init__(self,quality):self.quality=quality;self.v=[];self.f=[];self.uv=[]
 def face(self,points,cell,uv=None):
  first=len(self.v);self.v.extend(points);self.f.append(tuple(range(first,first+len(points))))
  if uv is None:uv=[(0,0),(1,0),(1,1),(0,1)][:len(points)]
  index=CELLS[cell];x=index%4;y=index//4
  self.uv.append([((x+.025+.95*u)/4,1-(y+.025+.95*(1-v))/4) for u,v in uv])
 def box(self,p,size,cell,angle=0,front=None):
  p=Vector(p);x,y,z=[v/2 for v in size]
  points=[Vector(v) for v in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]]
  points=[p+Vector((v.x*math.cos(angle)-v.y*math.sin(angle),v.x*math.sin(angle)+v.y*math.cos(angle),v.z)) for v in points]
  for i,face in enumerate([(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]):
   uv=[(.3,0),(.7,0),(.7,1),(.3,1)] if i==1 and front=='calligraphy' else None
   self.face([points[j] for j in face],front if i==1 and front else cell,uv)
 def lathe(self,p,profile,cell,n=24):
  n=max(6,round(n*self.quality));p=Vector(p);rings=[]
  for r,z in profile:rings.append([p+Vector((max(.001,r)*math.cos(j*math.tau/n),max(.001,r)*math.sin(j*math.tau/n),z)) for j in range(n)])
  for k in range(len(rings)-1):
   for j in range(n):self.face([rings[k][j],rings[k][(j+1)%n],rings[k+1][(j+1)%n],rings[k+1][j]],cell)
  for ring,reverse in [(rings[0],True),(rings[-1],False)]:
   for j in range(1,n-1):
    face=[ring[0],ring[j],ring[j+1]];self.face(list(reversed(face)) if reverse else face,cell,[(.1,.1),(.9,.1),(.5,.9)])
 def stem(self,a,b,r,cell,n=12):
  n=max(4,round(n*self.quality));a=Vector(a);b=Vector(b);axis=(b-a).normalized();side=axis.cross(Vector((0,1,0)))
  if side.length<.01:side=axis.cross(Vector((1,0,0)))
  side.normalize();other=axis.cross(side);rings=[]
  for p in [a,b]:rings.append([p+r*(side*math.cos(j*math.tau/n)+other*math.sin(j*math.tau/n)) for j in range(n)])
  for j in range(n):self.face([rings[0][j],rings[0][(j+1)%n],rings[1][(j+1)%n],rings[1][j]],cell)
  for ring,rev in [(rings[0],True),(rings[1],False)]:
   for j in range(1,n-1):
    points=[ring[0],ring[j],ring[j+1]];self.face(list(reversed(points)) if rev else points,cell,[(.1,.1),(.9,.1),(.5,.9)])
 def object(self,name,col):
  data=bpy.data.meshes.new(name);data.from_pydata(self.v,[],self.f);data.update();data.materials.append(material)
  uv=data.uv_layers.new(name='UVMap')
  for poly,coords in zip(data.polygons,self.uv):
   for loop,co in zip(poly.loop_indices,coords):uv.data[loop].uv=co
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
  o=bpy.data.objects.new(name,data);col.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
  data.uv_layers.new(name='LightmapUV');data.uv_layers.active_index=1
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');data.uv_layers.active_index=0;o.select_set(False)
  return o

def build(variant,quality):
 g=Geometry(quality);ports={'ground':(0,0,0)};collisions=[]
 if variant in ['lantern_hanging','lantern_standing']:
  height=.0 if variant=='lantern_hanging' else 1.2
  if height:
   g.lathe((0,0,0),[(.27,0),(.3,.05),(.21,.12),(.11,.16)],'stone');g.lathe((0,0,.16),[(.06,0),(.06,1.15)],'wood')
   collisions.append(((0,0,.62),(.28,.28,1.24),0))
   collisions.append(((0,0,1.78),(.64,.64,.7),0))
  z=.28+height
  g.lathe((0,0,z),[(.2,0),(.3,.13),(.32,.34),(.26,.55),(.16,.62)],'paper_lit',24)
  for level,r in [(0,.21),(.15,.3),(.55,.26),(.63,.18)]:g.lathe((0,0,z+level),[(r,0),(r,.03)],'bronze',20)
  for j in range(8 if quality==1 else 4):
   a=j*math.tau/(8 if quality==1 else 4)
   g.stem((.22*math.cos(a),.22*math.sin(a),z),(.26*math.cos(a),.26*math.sin(a),z+.57),.012,'wood')
  g.lathe((0,0,z+.66),[(.32,0),(.23,.1),(.06,.15)],'wood',16)
  g.stem((0,0,z+.8),(0,0,z+1.03),.025,'bronze')
  ports['light']=(0,0,z+.3);ports['hang']=(0,0,z+1.03)
  if quality>0:
   for j in range(4):
    a=j*math.pi/2;g.stem((.13*math.cos(a),.13*math.sin(a),z),(.16*math.cos(a),.16*math.sin(a),z-.22),.008,'lacquer',8)
 elif variant in ['brazier','incense_burner']:
  large=variant=='brazier';r=.4 if large else .23;z=.65 if large else .28
  g.lathe((0,0,z),[(r*.4,0),(r*.8,.06),(r,.22),(r,.28),(r*.84,.28),(r*.65,.09),(r*.25,.07)],'bronze')
  for j in range(3):
   a=j*math.tau/3;g.stem((r*.8*math.cos(a),r*.8*math.sin(a),.03),(r*.5*math.cos(a),r*.5*math.sin(a),z+.07),.045 if large else .028,'bronze')
  if large:
   g.lathe((0,0,z+.1),[(r*.55,0),(r*.55,.015)],'coals',20)
   for j in range(7 if quality==1 else 3):
    x=(j-(3 if quality==1 else 1))*(.09 if quality==1 else .18);length=math.sqrt(max(.005,(r*.83)**2-x*x))
    g.stem((x,-length,z+.3),(x,length,z+.3),.012,'bronze',8)
  else:
   g.lathe((0,0,z+.1),[(r*.6,0),(r*.6,.014)],'ash',20)
   for x in [-.06,0,.06]:g.stem((x,0,z+.12),(x+.035,0,z+.52),.007,'wood',8)
   for side in [-1,1]:g.stem((side*r*.8,0,z+.12),(side*(r+.08),0,z+.22),.016,'bronze',12)
  collisions.append(((0,0,(z+.3)/2),(r*2,r*2,z+.3),0))
 elif variant=='stone_table':
  g.lathe((0,0,0),[(.38,0),(.4,.08),(.28,.15)],'stone');g.lathe((0,0,.15),[(.18,0),(.14,.44),(.25,.51)],'stone')
  g.lathe((0,0,.66),[(.7,0),(.75,.04),(.75,.13),(.7,.16)],'stone',32)
  if quality==1:
   for j in range(8):
    a=j*math.tau/8;g.box((.2*math.cos(a),.2*math.sin(a),.42),(.065,.065,.28),'stone',a)
  collisions=[((0,0,.41),(1.5,1.5,.82),0)];ports['top']=(0,0,.82)
 elif variant=='stone_stool':
  g.lathe((0,0,0),[(.24,0),(.27,.06),(.19,.1),(.17,.3),(.26,.36),(.27,.43),(.24,.46)],'stone',24)
  if quality==1:
   for j in range(8):
    a=j*math.tau/8;g.box((.195*math.cos(a),.195*math.sin(a),.23),(.04,.04,.16),'stone',a)
  collisions=[((0,0,.23),(.54,.54,.46),0)];ports['seat']=(0,0,.46)
 elif variant=='folding_chair':
  # Open wooden folding chair: crossed side legs, slatted seat and raked back.
  for x in [-.235,.235]:
   g.stem((x,-.255,.025),(x,.245,.88),.025,'wood',16)
   g.stem((x,.255,.025),(x,-.205,.46),.025,'wood',16)
   g.stem((x-.012,0,.255),(x+.012,0,.255),.041,'bronze',24)
   g.stem((x,-.21,.435),(x,.21,.435),.024,'wood',12)
  for y in [-.255,.255]:g.stem((-.235,y,.065),(.235,y,.065),.018,'wood',12)
  count=6 if quality==1 else 3
  for j in range(count):
   y=-.18+j*.36/(count-1)
   g.box((0,y,.4425),(.45,.36/count-.006,.035),'wood')
  for z,y in [(.63,.095),(.87,.24)]:g.stem((-.255,y,z),(.255,y,z),.025,'wood',16)
  count=4 if quality==1 else 2
  for j in range(count):
   x=-.15+j*.3/(count-1)
   g.stem((x,.105,.64),(x,.235,.855),.018,'wood',12)
  collisions=[((0,0,.23),(.53,.56,.46),0),((0,.17,.69),(.53,.22,.46),0)]
  ports['seat']=(0,0,.46);ports['back']=(0,.24,.88);ports['hinge']=(0,0,.255)
 elif variant=='scroll':
  g.box((0,0,.78),(.62,.025,1.4),'linen',front='calligraphy')
  for z in [.05,1.51]:g.stem((-.37,0,z),(.37,0,z),.032,'wood',32)
  for z in [.05,1.51]:
   for x in [-.39,.39]:g.stem((x-.025,0,z),(x+.025,0,z),.042,'bronze',12)
  g.stem((-.23,0,1.53),(0,0,1.82),.007,'wood',12);g.stem((0,0,1.82),(.23,0,1.53),.007,'wood',12)
  ports['wall']=(0,.04,.78);ports['hang']=(0,0,1.82)
 else:
  width=.58;hinge=Vector((-.87,0,0))
  for panel,angle in enumerate([-.22,0,.22]):
   tangent=Vector((math.cos(angle),math.sin(angle),0));center=hinge+tangent*width/2
   g.box(center+Vector((0,0,1.05)),(.51,.04,1.45),'linen',angle,front='screen')
   for end in [0,width]:g.box(hinge+tangent*end+Vector((0,0,1.05)),(.055,.08,1.6),'wood',angle)
   for z in [.28,1.82]:g.box(center+Vector((0,0,z)),(.64,.08,.075),'wood',angle)
   g.box(center+Vector((0,0,.1)),(.36,.3,.1),'wood',angle)
   for j in range(10 if quality==1 else 1):
    z=.4+j*.13 if quality==1 else .4;g.box(center+Vector((0,-.04,z)),(.49,.02,.013),'wood',angle)
   collisions.append((tuple(center+Vector((0,0,.95))),(.64,.12,1.8),angle));hinge+=tangent*width
  ports['hinge']=(0,0,.28)
 return g,ports,collisions

out=R/'export/kits/props';out.mkdir(parents=True,exist_ok=True);manifest={'units':'metres','atlas_size':2048,'variants':{}}
variants=['lantern_hanging','lantern_standing','brazier','stone_table','stone_stool','incense_burner','scroll','screen','folding_chair'];collections=[]
for variant in variants:
 counts=[]
 lod_quality={'lantern_hanging':.5,'lantern_standing':.5,'stone_table':.48,'stone_stool':.5,'brazier':.47,'folding_chair':.45}.get(variant,.4)
 for suffix,quality in [('',1),('_LOD1',lod_quality)]:
  s=bpy.data.scenes.new('Props '+variant+suffix);s.unit_settings.system='METRIC';bpy.context.window.scene=s
  col=bpy.data.collections.new('KIT_props_'+variant+suffix);s.collection.children.link(col);collections.append(col)
  g,ports,colliders=build(variant,quality);model=g.object('KIT_props_'+variant+'_render'+suffix,col);model['variant']=variant;model['lod_ratio']=quality
  for port,p in ports.items():
   o=bpy.data.objects.new('PORT_'+port,None);o.location=p;o['connection']='prop_mount';col.objects.link(o)
  for index,(p,size,angle) in enumerate(colliders):
   bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name='COL_props_'+variant+'_'+str(index)+suffix+'-colonly';o.scale=size;o.rotation_euler.z=angle;o['collision_only']=True
   for old in list(o.users_collection):old.objects.unlink(o)
   col.objects.link(o)
  counts.append(sum(len(p.vertices)-2 for p in model.data.polygons));model['lod_ratio']=counts[-1]/counts[0];model['detail_quality']=quality
  bpy.ops.export_scene.gltf(filepath=str(out/f'KIT_props_{variant}{suffix}.glb'),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':counts[0],'triangles_lod1':counts[1],'ratio':counts[1]/counts[0],'connectors':ports,'colliders':len(colliders)}
gallery=bpy.data.scenes.new('Props kit showroom');bpy.context.window.scene=gallery;root=bpy.data.collections.new('KIT_props');gallery.collection.children.link(root)
for index,col in enumerate(collections):
 o=bpy.data.objects.new(col.name,None);root.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=col;o.location=((index//2)%4*3,(index//2)//4*4+(index%2)*10,0)
 for obj in col.objects:
  if obj.name.startswith('COL_'):obj.hide_render=True;obj.hide_viewport=True
cam=bpy.data.cameras.new('CAM_props_gallery');o=bpy.data.objects.new(cam.name,cam);root.objects.link(o);o.location=(12,-14,12);o.rotation_euler=(Vector((4.5,3,1))-o.location).to_track_quat('-Z','Y').to_euler();gallery.camera=o
sun=bpy.data.lights.new('LGT_props_preview','SUN');sun.energy=2;sun.color=(1,.94,.84);o=bpy.data.objects.new(sun.name,sun);root.objects.link(o);o.rotation_euler=(.5,-.5,-.4)
gallery.world=bpy.data.worlds.new('Props preview world');gallery.world.use_nodes=True;gallery.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.25,.29,1)
gallery.render.resolution_x=1600;gallery.render.resolution_y=1000;gallery.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/kits/KIT_props.blend'),compress=True)
for suffix in ['','_LOD1']:shutil.copyfile(out/f'KIT_props_lantern_hanging{suffix}.glb',R/f'export/kits/KIT_props{suffix}.glb')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('PROPS_KIT_COMPLETE',json.dumps(manifest))
