"""Bake the saved linked Area wash to the canonical assembly's UV2.

The glTF exporter omits Area lights. Reconstruct only the saved stage wash,
with its exact transform and receiver list, then bake DIRECT diffuse alone.
The ordinary scene lightmaps remain independent and are not overwritten.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
import bmesh
import numpy as np
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--samples', type=int, default=128)
parser.add_argument('--size', type=int, default=512)
parser.add_argument('--output', type=Path, default=ROOT/'export/lightmaps/backdrop-wash')
parser.add_argument('--inspect', action='store_true')
options = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source = ROOT/'export/garden-of-dreams.glb'
stage = ROOT/'blender/sites/SITE_stage.blend'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
stage_hash = hashlib.sha256(stage.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(stage), link=False) as (available, loaded):
    loaded.objects = [n for n in available.objects if n == 'LGT_stage_backdrop_wash']
wash = loaded.objects[0]
assert wash and wash.data.type == 'AREA' and wash.light_linking.receiver_collection
# Library objects are not evaluated until linked to a scene. matrix_basis
# contains the saved local transform; none of these stage objects has a parent.
assert wash.parent is None
receiver_sources = []
for obj in wash.light_linking.receiver_collection.objects:
    assert obj.parent is None
    materials = [m.name for m in obj.data.materials]
    target = 'SITE_stage_' + '_'.join(materials)
    positions = np.asarray([list(obj.matrix_basis @ vertex.co) for vertex in obj.data.vertices])
    receiver_sources.append({'source_object': obj.name, 'mesh': target,
                             'bounds': [positions.min(axis=0).tolist(), positions.max(axis=0).tolist()]})
assert len(receiver_sources) == 5
lighting = {'type': 'AREA', 'shape': wash.data.shape, 'size': wash.data.size,
            'size_y': wash.data.size_y, 'energy': wash.data.energy,
            'color': list(wash.data.color), 'matrix': list(map(list, wash.matrix_basis)),
            'receivers': receiver_sources, 'pass_filter': ['DIRECT']}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = options.samples
scene.cycles.use_denoising = False
world = bpy.data.worlds.new('Wash bake black world')
world.use_nodes = True
world.node_tree.nodes.get('Background').inputs['Strength'].default_value = 0
scene.world = world
# Emissive CRTs and lantern geometry can also contribute to a DIRECT bake.
# Exclude those sources so this map contains only the linked Area light.
for material in bpy.data.materials:
    if not material.use_nodes: continue
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            node.inputs['Emission Strength'].default_value = 0
        elif node.type == 'EMISSION':
            node.inputs['Strength'].default_value = 0
for obj in scene.objects:
    if obj.type == 'LIGHT': obj.hide_render = True
    if obj.name.startswith('COL_') or (obj.type == 'MESH' and any(
            m and (m.name == 'MAT_fog_plane' or m.name.startswith('MAT_stage_fog'))
            for m in obj.data.materials)):
        obj.hide_render = True
receivers = bpy.data.collections.new('LINK_native_wash_receivers')
for record in receiver_sources:
    obj = bpy.data.objects.get(record['mesh'])
    assert obj and obj.type == 'MESH', record
    positions = np.asarray([list(obj.matrix_world @ vertex.co) for vertex in obj.data.vertices])
    assert np.allclose(np.asarray(record['bounds']), [positions.min(axis=0), positions.max(axis=0)], atol=1e-4), ('Source/export receiver geometry differs', record)
    assert len(obj.data.uv_layers) >= 2
    receivers.objects.link(obj)
data = bpy.data.lights.new('LGT_native_backdrop_wash', 'AREA')
for key in ['shape', 'size', 'size_y', 'energy', 'color']: setattr(data, key, lighting[key])
wash = bpy.data.objects.new(data.name, data)
scene.collection.objects.link(wash)
wash.matrix_world = Matrix(lighting['matrix'])
wash.light_linking.receiver_collection = receivers
if options.inspect:
    bpy.context.view_layer.update()
    print('WASH_DIAGNOSTIC_LIGHT', lighting, flush=True)
    for obj in receivers.objects:
        transform = obj.matrix_world.to_3x3().inverted().transposed()
        facing = [(transform @ poly.normal).normalized().dot(
            (wash.location - obj.matrix_world @ poly.center).normalized()) for poly in obj.data.polygons]
        print('WASH_DIAGNOSTIC_MESH', obj.name, 'normal_facing_range', min(facing), max(facing),
              'nodes', [[(n.type, [(i.name, str(i.default_value)) for i in n.inputs if hasattr(i,'default_value') and i.name in ['Emission Strength','Base Color']]) for n in m.node_tree.nodes] for m in obj.data.materials], flush=True)
    sys.exit(0)
options.output.mkdir(parents=True, exist_ok=True)
records = {}
sys.path.insert(0, str(ROOT/'scripts'))
from lightmap_catalog import glb_document
document = glb_document(source)
double_sided = {node['name'] for node in document['nodes'] if 'mesh' in node and any(
    p.get('material') is not None and document['materials'][p['material']].get('doubleSided',False)
    for p in document['meshes'][node['mesh']]['primitives'])}

def reverse_faces(obj):
    def uv_mapping():
        layer=obj.data.uv_layers[1]
        return sorted((loop.vertex_index,tuple(layer.data[loop.index].uv)) for loop in obj.data.loops)
    before=uv_mapping()
    mesh=bmesh.new()
    mesh.from_mesh(obj.data)
    bmesh.ops.reverse_faces(mesh,faces=list(mesh.faces))
    mesh.to_mesh(obj.data)
    mesh.free()
    obj.data.update()
    assert uv_mapping()==before, ("Back-face bake changed UV-to-vertex mapping",obj.name)


def bake(obj):
    image = bpy.data.images.new('WASH_'+obj.name, width=options.size, height=options.size, alpha=False, float_buffer=True)
    image.colorspace_settings.name = 'Non-Color'
    for index, original in enumerate(list(obj.data.materials)):
        material = original.copy()
        material.use_nodes = True
        obj.data.materials[index] = material
        node = material.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = image
        material.node_tree.nodes.active = node
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.data.uv_layers.active_index = 1
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT'}, uv_layer=obj.data.uv_layers[1].name, margin=4, use_clear=True)
    pixels = np.empty(options.size*options.size*4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    return image, pixels.reshape(-1,4)

# Native linking control: a real building must get no direct wash contribution.
control = bpy.data.objects['SITE_qinfang-ting_MAT_plaster_rock']
image, pixels = bake(control)
control_max = float(pixels[:,:3].max())
assert control_max <= 1e-7, ('Area light spilled onto a building', control_max)
bpy.data.images.remove(image)
for obj in receivers.objects:
    uv = np.empty(len(obj.data.uv_layers[1].data)*2, dtype=np.float32)
    obj.data.uv_layers[1].data.foreach_get('uv', uv)
    sides = ['front','back'] if obj.name in double_sided else ['front']
    images = {}
    for side in sides:
        print('WASH_BAKE_TARGET', obj.name, side, flush=True)
        if side == 'back': reverse_faces(obj)
        image, pixels = bake(obj)
        assert np.isfinite(pixels).all()
        maximum = float(pixels[:,:3].max())
        scale = max(1.0, maximum)
        pixels[:,:3] /= scale
        pixels[:,3] = 1
        image.pixels.foreach_set(pixels.ravel())
        filename = obj.name+'-'+side+'.png'
        image.file_format = 'PNG'
        image.filepath_raw = str(options.output/filename)
        image.save()
        images[side] = {'texture':filename,'scale':scale,'linear_max':maximum,
                        'nonzero_fraction':float((pixels[:,:3].max(axis=1)>1e-5).mean()),
                        'png_sha256':hashlib.sha256((options.output/filename).read_bytes()).hexdigest()}
        bpy.data.images.remove(image)
        if side == 'back': reverse_faces(obj)
    unoccluded_max = None
    if max(side['linear_max'] for side in images.values()) <= 1e-5:
        # Test the correct inward face without the other concentric flats.
        # Keep the black, shadowed result as the delivered bake.
        hidden={other:other.hide_render for other in receivers.objects if other != obj}
        for other in hidden:other.hide_render=True
        if obj.name in double_sided:reverse_faces(obj)
        probe, probe_pixels=bake(obj)
        unoccluded_max=float(probe_pixels[:,:3].max())
        bpy.data.images.remove(probe)
        if obj.name in double_sided:reverse_faces(obj)
        for other,state in hidden.items():other.hide_render=state
        assert unoccluded_max>1e-5, ('No wash even on isolated inward face',obj.name,unoccluded_max)
    record = {'mesh': obj.name, 'texture':images['front']['texture'], 'scale':images['front']['scale'],
              'sides':images,'double_sided':obj.name in double_sided,'backface_uv_mapping_verified':True,'unoccluded_control_max':unoccluded_max,
              'size':options.size, 'samples':options.samples, 'uv_channel':1,
              'uv_sha256':hashlib.sha256(uv.tobytes()).hexdigest(),
              'source_glb_sha256':source_hash, 'stage_blend_sha256':stage_hash,
              'point_lights_baked':False,'pass_filter':['DIRECT']}
    (options.output/(obj.name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    records[obj.name] = record
    print('WASH_BAKED',json.dumps(record),flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
assert hashlib.sha256(stage.read_bytes()).hexdigest()==stage_hash
assert any(side['linear_max']>1e-5 for record in records.values() for side in record['sides'].values())
manifest = {'source_glb_sha256': source_hash, 'stage_blend_sha256': stage_hash,
            'lighting': lighting, 'building_control_max': control_max,
            'records': records}
(options.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('NATIVE_BACKDROP_WASH_PASS',len(records),'building direct maximum',control_max,flush=True)
