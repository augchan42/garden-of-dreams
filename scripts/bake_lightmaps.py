"""Bake diffuse lighting to exported UV2, without altering authoring assets.

Run in a separate Blender process. Output is experimental until inspected in Godot.
Each material batch has its own image because its UV2 chart occupies the unit square.
"""
import bpy,sys,argparse,json,hashlib,math,struct
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser();p.add_argument('--site');p.add_argument('--mesh',default='SITE_qinfang-ting_MAT_plaster_rock');p.add_argument('--size',type=int,default=1024);p.add_argument('--samples',type=int,default=32);options=p.parse_args(args)
bpy.ops.wm.read_factory_settings(use_empty=True)
source=R/'export/garden-of-dreams.glb'
source_digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.import_scene.gltf(filepath=str(source))
s=bpy.context.scene
try:s.render.engine='CYCLES'
except TypeError as error:raise RuntimeError('Cycles unavailable') from error
s.cycles.samples=options.samples
s.cycles.use_denoising=False
world=bpy.data.worlds.new('Bake stage ambient');world.use_nodes=True
background=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
background.inputs[0].default_value=(.025,.045,.022,1);background.inputs[1].default_value=.3;s.world=world
for o in s.objects:
 if o.name.startswith('COL_') or (o.type=='MESH' and any(m and m.name=='MAT_fog_plane' for m in o.data.materials)):o.hide_render=True
 if o.type=='LIGHT' and o.data.type=='POINT':o.data.energy=0
# Point practicals stay dynamic in Godot; their emissive geometry remains visible.
def read_glb(path):
 data=path.read_bytes();length=struct.unpack_from('<I',data,12)[0]
 return json.loads(data[20:20+length])
site_for_mesh={}
if options.site:
 files=sorted((R/'export/sites').glob('SITE_*.glb')) if options.site=='all' else [R/'export/sites'/('SITE_'+options.site+'.glb')]
 names=[]
 for file in files:
  doc=read_glb(file)
  for node in doc['nodes']:
   if 'mesh' in node and not node.get('name','').startswith('COL_'):
    name=node['name'];assert name not in site_for_mesh
    site_for_mesh[name]=file.stem.removeprefix('SITE_');names.append(name)
 targets=[bpy.data.objects.get(name) for name in names]
 assert all(targets),'Some site nodes do not match the assembly'
else:targets=[bpy.data.objects.get(options.mesh)]
assert all(o and o.type=='MESH' for o in targets)
line_variants=[o for o in s.objects if o.name.startswith('HERO_table_line_')]
for o in targets:
 if any(m and m.name in ['MAT_water','MAT_aojing_water','MAT_fog_plane'] for m in o.data.materials):continue
 # Mutually exclusive line meshes must never shade each other. Bake each line
 # on its own, and leave changing-line shadows out of static table lighting.
 for variant in line_variants:variant.hide_render=variant!=o
 size=options.size if len(o.data.polygons)>512 or max(o.dimensions)>6 else min(256,options.size)
 assert len(o.data.uv_layers)>=2,'Missing UV2: '+o.name
 out=R/'export/lightmaps';out.mkdir(exist_ok=True)
 image=bpy.data.images.new('BAKE_'+o.name,width=size,height=size,alpha=False,float_buffer=True)
 image.colorspace_settings.name='Non-Color'
 for index,material in enumerate(list(o.data.materials)):
  material=material.copy();o.data.materials[index]=material
  material.use_nodes=True
  node=material.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
  material.node_tree.nodes.active=node
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 o.data.uv_layers.active_index=1
 bpy.ops.object.bake(type='DIFFUSE',pass_filter={'DIRECT','INDIRECT'},uv_layer=o.data.uv_layers[1].name,margin=4,use_clear=True)
 pixels=np.empty(size*size*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(-1,4)
 assert np.isfinite(pixels).all()
 scale=max(1.0,float(pixels[:,:3].max()))
 nonzero=float((pixels[:,:3].max(axis=1)>1e-5).mean())
 assert nonzero>.01,'Bake is empty'
 pixels[:,:3]/=scale;pixels[:,3]=1;image.pixels.foreach_set(pixels.ravel())
 image.file_format='PNG';image.filepath_raw=str(out/(o.name+'.png'));image.save()
 uv=np.empty(len(o.data.uv_layers[1].data)*2,dtype=np.float32);o.data.uv_layers[1].data.foreach_get('uv',uv)
 record={'mesh':o.name,'site':site_for_mesh.get(o.name),'texture':o.name+'.png','scale':scale,'size':size,'samples':options.samples,'uv_channel':1,'uv_sha256':hashlib.sha256(uv.tobytes()).hexdigest(),'source_glb_sha256':source_digest,'nonzero_fraction':nonzero,'point_lights_baked':False,'status':'Cycles bake produced; engine look verification pending'}
 (out/(o.name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
 print('LIGHTMAP_BAKED',json.dumps(record))
