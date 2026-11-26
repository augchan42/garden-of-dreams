"""Shared editable lotus mesh, material and UV construction for the water kit."""
import bpy
from lotus_geometry import cluster

def material():
    m=bpy.data.materials.get('MAT_lotus_leaf')
    if m is None:
        m=bpy.data.materials.new('MAT_lotus_leaf');m.use_nodes=True
        m.diffuse_color=(.05,.095,.066,1)
        shader=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value=m.diffuse_color
        shader.inputs['Roughness'].default_value=.74
    return m

def assign(obj,segments):
    vertices,faces=cluster(segments)
    mesh=bpy.data.meshes.new(obj.name+'_geometry')
    mesh.from_pydata(vertices,[],faces);mesh.update();mesh.materials.append(material())
    obj.data=mesh
    for modifier in list(obj.modifiers):obj.modifiers.remove(modifier)
    for name in ['UVMap','LightmapUV']:mesh.uv_layers.new(name=name)
    x0=min(v.co.x for v in mesh.vertices);y0=min(v.co.y for v in mesh.vertices)
    dx=max(v.co.x for v in mesh.vertices)-x0;dy=max(v.co.y for v in mesh.vertices)-y0
    for loop in mesh.loops:
        co=mesh.vertices[loop.vertex_index].co
        mesh.uv_layers[0].data[loop.index].uv=((co.x-x0)/dx,(co.y-y0)/dy)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
    bpy.context.view_layer.objects.active=obj;mesh.uv_layers.active_index=1
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');obj.select_set(False)
    return mesh
