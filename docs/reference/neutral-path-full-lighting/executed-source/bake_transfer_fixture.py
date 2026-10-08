"""Bake a unit-light transfer fixture, separate from all garden scene assets."""
import bpy,numpy as np,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32
s.world=bpy.data.worlds.new('Dark fixture');s.world.use_nodes=True
next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=0
bpy.ops.mesh.primitive_plane_add(size=2)
o=bpy.context.object;o.data.uv_layers.new(name='BakeUV')
for a,b in zip(o.data.uv_layers[0].data,o.data.uv_layers[1].data):b.uv=a.uv
m=bpy.data.materials.new('White diffuse');m.use_nodes=True
shader=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
shader.inputs['Base Color'].default_value=(1,1,1,1);shader.inputs['Roughness'].default_value=1
shader.inputs['Specular IOR Level'].default_value=0
o.data.materials.append(m)
image=bpy.data.images.new('Fixture',width=64,height=64,alpha=False,float_buffer=True);image.colorspace_settings.name='Non-Color'
t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;m.node_tree.nodes.active=t
bpy.ops.object.light_add(type='SUN',location=(0,0,3));light=bpy.context.object;light.data.energy=1;light.data.color=(1,1,1)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.bake(type='DIFFUSE',pass_filter={'DIRECT','INDIRECT'},uv_layer='BakeUV',margin=4)
p=np.empty(64*64*4,dtype=np.float32);image.pixels.foreach_get(p);p=p.reshape(64,64,4)
image.file_format='PNG';image.filepath_raw=str(ROOT/'godot/tests/fixtures/cycles-unit-sun.png');image.save()
record={'linear_mean_rgb':p[8:56,8:56,:3].mean(axis=(0,1)).tolist(),'light_energy':1,'samples':32,'bake_pass':'DIFFUSE DIRECT+INDIRECT, COLOR excluded','blender_version':bpy.app.version_string,'texture_sha256':hashlib.sha256(Path(image.filepath_raw).read_bytes()).hexdigest()}
(ROOT/'godot/tests/fixtures/cycles-unit-sun.json').write_text(json.dumps(record,indent=2)+'\n')
print('BAKE_TRANSFER_FIXTURE',json.dumps(record),flush=True)
