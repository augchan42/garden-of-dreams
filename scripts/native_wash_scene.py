"""Reconstruct saved linked Areas in a temporary canonical GLB bake scene.

No source file is edited. Used by the terminal indirect-spill baker; its
scene setup follows the already verified native backdrop direct pass.
"""
import hashlib
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix


def isolated_wash_scene(root: Path, samples: int) -> dict:
    ROOT = root
    source = ROOT/'export/garden-of-dreams.glb'
    stage = ROOT/'blender/sites/SITE_stage.blend'
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    stage_hash = hashlib.sha256(stage.read_bytes()).hexdigest()
    authoring=ROOT/'blender/authoring.blend'
    authoring_hash=hashlib.sha256(authoring.read_bytes()).hexdigest()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(authoring),link=False) as (available,loaded):
        loaded.objects=[n for n in available.objects if n.endswith('_backdrop_wash') and n.startswith('LGT_')]
    washes=[o for o in loaded.objects if o.data.energy>0]
    assert len(washes)==12 and all(o.data.type=='AREA' for o in washes)
    receiver_set=set(washes[0].light_linking.receiver_collection.objects)
    assert len(receiver_set)==5
    receiver_sources=[]
    for obj in sorted(receiver_set,key=lambda o:o.name):
        assert obj.parent is None
        materials=[m.name for m in obj.data.materials]
        target='SITE_stage_'+'_'.join(materials)
        positions=np.asarray([list(obj.matrix_basis@vertex.co) for vertex in obj.data.vertices])
        receiver_sources.append({'source_object':obj.name,'mesh':target,
                                 'bounds':[positions.min(axis=0).tolist(),positions.max(axis=0).tolist()]})
    lights=[]
    site_hashes={}
    for wash in sorted(washes,key=lambda o:o.name):
        assert wash.parent is None and set(wash.light_linking.receiver_collection.objects)==receiver_set
        slug=wash['wash_site']
        site_hashes[slug]=hashlib.sha256((ROOT/'blender/sites'/('SITE_'+slug+'.blend')).read_bytes()).hexdigest()
        lights.append({'name':wash.name,'site':slug,'type':'AREA','shape':wash.data.shape,
                       'size':wash.data.size,'size_y':wash.data.size_y,'energy':wash.data.energy,
                       'color':list(wash.data.color),'matrix':list(map(list,wash.matrix_basis))})
    lighting={'type':'AREA','lights':lights,'receivers':receiver_sources,'pass_filter':['DIRECT']}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
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
    for saved in lights:
        data=bpy.data.lights.new(saved['name'],'AREA')
        for key in ['shape','size','size_y','energy','color']:setattr(data,key,saved[key])
        wash=bpy.data.objects.new(data.name,data)
        scene.collection.objects.link(wash)
        wash.matrix_world=Matrix(saved['matrix'])
        wash.light_linking.receiver_collection=receivers
    return {name: value for name, value in locals().items() if name in (
        'scene', 'source', 'source_hash', 'stage', 'stage_hash', 'authoring',
        'authoring_hash', 'site_hashes', 'lighting', 'receivers')}
