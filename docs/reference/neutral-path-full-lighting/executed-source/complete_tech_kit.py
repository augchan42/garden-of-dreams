"""Build all six tech modules with atlas PBR maps and semantic LOD companions."""
import bpy,math,json,shutil,sys,io_scene_gltf2
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from kit_geometry import Geometry
from make_tech_atlas import CELLS
bpy.ops.wm.read_factory_settings(use_empty=True)
material=bpy.data.materials.new('MAT_tech_atlas');material.use_nodes=True;material.use_backface_culling=True
export_format=next(item[0] for item in io_scene_gltf2.get_format_items(None,bpy.context) if item[0]=='GLB')
nt=material.node_tree;bsdf=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');textures={}
for key in ['basecolor','orm','emission']:
 node=nt.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(R/f'textures/kits/tech/tech-{key}.png'));node.image.pack()
 if key=='orm':node.image.colorspace_settings.name='Non-Color'
 textures[key]=node
nt.links.new(textures['basecolor'].outputs['Color'],bsdf.inputs['Base Color'])
channels=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(textures['orm'].outputs['Color'],channels.inputs['Color'])
nt.links.new(channels.outputs['Green'],bsdf.inputs['Roughness']);nt.links.new(channels.outputs['Blue'],bsdf.inputs['Metallic'])
nt.links.new(textures['emission'].outputs['Color'],bsdf.inputs['Emission Color']);bsdf.inputs['Emission Strength'].default_value=4.0

def crt(g,position,phosphor,low=False,bank=False):
 p=Vector(position)
 def box(q,size,cell):g.box(p+Vector(q),size,cell)
 box((0,0,.025),(.28,.32,.05),'steel');box((0,.03,.09),(.16,.15,.09),'steel')
 g.case(p+Vector((0,0,.36)),(.64,.54,.48),'case',1 if low else 4)
 columns,rows=((5,3) if low else (8,6)) if bank else ((7,4) if low else (12,8))
 for row in range(rows):
  for col in range(columns):
   coords=[(col/columns,row/rows),((col+1)/columns,row/rows),((col+1)/columns,(row+1)/rows),(col/columns,(row+1)/rows)]
   points=[]
   for u,v in coords:
    x=(u-.5)*.49;z=(v-.5)*.34+.37;y=-.286-.017*(1-(2*u-1)**2)*(1-(2*v-1)**2)
    points.append(p+Vector((x,y,z)))
   g.face(points,phosphor,coords)
 for x in [-.20,-.10,.18]:g.stem(p+Vector((x,-.275,.16)),p+Vector((x,-.31,.16)),.018,'bronze',4 if low else 8)
 for i in range(3 if low else 6):box((.318,.15-i*.052,.38),(.012,.025,.21),'black')
 box((0,.274,.34),(.24,.014,.15),'black')
 if not low:
  for x in [-.10,0,.10]:box((x,.286,.34),(.024,.025,.08),'steel')

def build(variant,low):
 g=Geometry(material,CELLS,.4 if low else 1);ports={'ground':(0,0,0)};collisions=[]
 if variant.startswith('crt_'):
  crt(g,(0,0,0),variant[4:],low);collisions=[((0,0,.30),(.66,.56,.60))]
  ports.update(screen=(0,-.31,.37),cable=(0,.29,.24))
 elif variant=='monitor_bank':
  for x in [-.36,.36]:
   for z in [0,.65]:crt(g,(x,0,z),'amber',low,True)
  for z in [.03,.68,1.30]:g.box((0,.18,z),(1.45,.4,.055),'steel')
  for x in [-.72,.72]:g.box((x,.23,.665),(.06,.08,1.33),'steel')
  collisions=[((0,.02,.665),(1.51,.60,1.33))];ports.update(screen=(0,-.31,.69),cable=(0,.29,.665),stack=(0,0,1.33))
 elif variant=='cable_run':
  count=12 if low else 20
  points=[Vector((3*i/count,.10*math.sin(i/count*math.tau),.07+.06*math.sin(i/count*math.pi))) for i in range(count+1)]
  for a,b in zip(points,points[1:]):g.stem(a,b,.027,'cable',8 if low else 12)
  for i in range(3 if low else 6):
   t=(i+1)/(4 if low else 7);g.box((3*t,.10*math.sin(t*math.tau),.065+.06*math.sin(t*math.pi)),(.055,.075,.075),'steel')
  ports.update(start=tuple(points[0]),end=tuple(points[-1]))
 elif variant=='cell_door':
  for x in [-.61,.61]:
   g.case((x,0,1.19),(.14,.18,2.38),'steel',1 if low else 4)
  g.case((0,0,2.39),(1.36,.18,.14),'steel',1 if low else 4)
  for x in [-.61,.61]:
   for z in [.2,.8,1.5,2.2]:g.stem((x,-.095,z),(x,-.12,z),.027,'bronze',4 if low else 8)
  collisions=[((x,0,1.19),(.14,.18,2.38)) for x in [-.61,.61]]+[((0,0,2.39),(1.36,.18,.14))]
  ports.update(threshold=(0,0,0),opening=(0,0,1.1))
 else:
  g.box((0,0,.755),(1.35,.74,.09),'wood')
  for x in [-.55,.55]:
   for y in [-.26,.26]:
    g.box((x,y,.355),(.055,.055,.71),'steel');g.box((x,y,.025),(.11,.11,.05),'black')
  for y in [-.26,.26]:g.box((0,y,.18),(1.12,.035,.035),'steel')
  g.box((0,.26,.60),(1.12,.04,.2),'wood')
  for x in [-.48,.48]:
   if low:g.box((x,0,.64),(.23,.62,.11),'wood')
   else:g.case((x,0,.64),(.23,.62,.11),'wood',4)
   g.box((x,-.32,.65),(.09,.025,.025),'bronze')
  g.box((0,-.05,.815),(.54,.20,.025),'keyboard')
  cols,rows=(3,2) if low else (5,4)
  for row in range(rows):
   for col in range(cols):g.box(((col-(cols-1)/2)*(.10 if low else .095),-.05+(row-(rows-1)/2)*(.065 if low else .043),.837),(.075,.03,.018),'black')
  collisions=[((0,0,.4),(1.35,.74,.8))];ports.update(top=(0,0,.8),screen=(0,.12,.8),cable=(0,.38,.64))
 return g,ports,collisions

variants=['crt_amber','crt_green','monitor_bank','cable_run','cell_door','terminal_desk'];out=R/'export/kits/tech';out.mkdir(parents=True,exist_ok=True);manifest={'units':'metres','atlas_size':2048,'variants':{}};collections=[]
for variant in variants:
 counts=[]
 for low in [False,True]:
  suffix='_LOD1' if low else '';s=bpy.data.scenes.new('Tech '+variant+suffix);s.unit_settings.system='METRIC';bpy.context.window.scene=s
  col=bpy.data.collections.new('KIT_tech_'+variant+suffix);s.collection.children.link(col);collections.append(col)
  g,ports,colliders=build(variant,low);model=g.object('KIT_tech_'+variant+'_render'+suffix,col);counts.append(sum(len(p.vertices)-2 for p in model.data.polygons));model['variant']=variant;model['lod_ratio']=counts[-1]/counts[0]
  for key,p in ports.items():
   o=bpy.data.objects.new('PORT_'+key,None);o.location=p;o['connection']='tech_mount';col.objects.link(o)
  for index,(p,size) in enumerate(colliders):
   bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name='COL_tech_'+variant+'_'+str(index)+suffix+'-colonly';o.scale=size;o['collision_only']=True
   for old in list(o.users_collection):old.objects.unlink(o)
   col.objects.link(o)
  bpy.ops.export_scene.gltf(filepath=str(out/f'KIT_tech_{variant}{suffix}.glb'),export_format=export_format,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
 manifest['variants'][variant]={'triangles_lod0':counts[0],'triangles_lod1':counts[1],'ratio':counts[1]/counts[0],'connectors':ports,'colliders':len(colliders)}
gallery=bpy.data.scenes.new('Tech kit showroom');bpy.context.window.scene=gallery;root=bpy.data.collections.new('KIT_tech');gallery.collection.children.link(root)
for index,col in enumerate(collections):
 o=bpy.data.objects.new(col.name,None);root.objects.link(o);o.instance_type='COLLECTION';o.instance_collection=col;o.location=((index//2)%3*3.5,(index//2)//3*4+(index%2)*10,0)
 for obj in col.objects:
  if obj.name.startswith('COL_'):obj.hide_render=True;obj.hide_viewport=True
camera=bpy.data.cameras.new('CAM_tech_gallery');o=bpy.data.objects.new(camera.name,camera);root.objects.link(o);o.location=(9,-12,8);o.rotation_euler=(Vector((3.5,2,1))-o.location).to_track_quat('-Z','Y').to_euler();gallery.camera=o
sun=bpy.data.lights.new('LGT_tech_preview','SUN');sun.energy=2;o=bpy.data.objects.new(sun.name,sun);root.objects.link(o);o.rotation_euler=(.5,-.5,-.4)
gallery.world=bpy.data.worlds.new('Tech preview world');gallery.world.use_nodes=True;next(n for n in gallery.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.22,.25,.29,1)
gallery.render.resolution_x=1600;gallery.render.resolution_y=1000;gallery.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/kits/KIT_tech.blend'),compress=True)
for suffix in ['','_LOD1']:shutil.copyfile(out/f'KIT_tech_crt_amber{suffix}.glb',R/f'export/kits/KIT_tech{suffix}.glb')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('TECH_KIT_COMPLETE',json.dumps(manifest))
