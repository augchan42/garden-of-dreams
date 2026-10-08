"""Apply the original painted atlas to the saved physical mountain flats.

Only their primary UVs and three materials change. Source geometry, lights,
collisions, cameras and all other materials are checked before saving.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true')
options = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
folder = ROOT / 'textures/backdrops/mountain-paint'
atlas = json.loads((folder / 'atlas.json').read_text())
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
targets = {name for name in atlas['uv_regions']}


def socket_value(value):
    if isinstance(value, (bool, int, float, str)):
        return value
    try:
        return list(value)
    except TypeError:
        return str(value)


def snapshot():
    objects = {}
    for obj in scene.objects:
        record = {'matrix': list(map(list, obj.matrix_world)), 'type': obj.type}
        if obj.type == 'MESH':
            vertices = np.empty(len(obj.data.vertices) * 3, dtype=np.float32)
            obj.data.vertices.foreach_get('co', vertices)
            record['vertices'] = hashlib.sha256(vertices.tobytes()).hexdigest()
            record['faces'] = [list(p.vertices) + [p.material_index] for p in obj.data.polygons]
        if obj.type == 'LIGHT':
            record['light'] = (obj.data.type, obj.data.energy, list(obj.data.color))
        objects[obj.name] = record
    materials = {}
    for mat in bpy.data.materials:
        if mat.name in targets or not mat.use_nodes:
            continue
        materials[mat.name] = [[node.type, [socket_value(s.default_value) for s in node.inputs
                                          if hasattr(s, 'default_value')]] for node in mat.node_tree.nodes]
    return {'objects': objects, 'materials': materials}


before = snapshot()
if options.apply:
    image = bpy.data.images.load(str(folder / 'mountain-paint.png'), check_existing=True)
    image.colorspace_settings.name = 'sRGB'
    image.pack()
    for i in range(3):
        name = 'MAT_painted_mountains_' + str(i)
        mat = bpy.data.materials[name]
        bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        for input_name in ('Base Color', 'Emission Color'):
            for link in list(bsdf.inputs[input_name].links):
                mat.node_tree.links.remove(link)
            bsdf.inputs[input_name].default_value = (1, 1, 1, 1)
        texture = mat.node_tree.nodes.new('ShaderNodeTexImage')
        texture.image = image
        mat.node_tree.links.new(texture.outputs['Color'], bsdf.inputs['Base Color'])
        mat.node_tree.links.new(texture.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = .6
        mat.diffuse_color = (*atlas['mean_linear_rgb'][str(i)], 1)
        mat['paint_source'] = 'textures/backdrops/mountain-paint/atlas.json'
        objects = [o for o in scene.objects if o.type == 'MESH' and o.name.startswith('KIT_stage_painted_mountain_layer')
                   and o.data.materials[0] == mat]
        assert len(objects) == 1
        obj = objects[0]
        assert len(obj.data.uv_layers) == 0, 'Run against the unpainted source; do not append duplicate UVs'
        uv = obj.data.uv_layers.new(name='PaintUV')
        x, y, width, height = atlas['uv_regions'][name]
        z_min = min(v.co.z for v in obj.data.vertices)
        z_max = max(v.co.z for v in obj.data.vertices)
        for polygon in obj.data.polygons:
            points = [obj.data.vertices[obj.data.loops[loop].vertex_index].co for loop in polygon.loop_indices]
            angles = [(math.atan2(p.y, p.x) / math.tau) % 1 for p in points]
            if max(angles) - min(angles) > .5:
                angles = [a + 1 if a < .5 else a for a in angles]
            for loop, point, angle in zip(polygon.loop_indices, points, angles):
                uv.data[loop].uv = (x + angle * width, y + (point.z - z_min) / (z_max - z_min) * height)
        obj['paint_source'] = mat['paint_source']
    bpy.context.view_layer.update()
    assert snapshot() == before, 'Changed geometry, transforms, lights or unrelated materials'
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'blender/authoring.blend'), compress=True)
    bpy.data.libraries.write(str(ROOT / 'blender/sites/SITE_stage.blend'),
                            {bpy.data.collections['SITE_stage']}, fake_user=True, compress=True)
report = {'status': 'saved' if options.apply else 'proposed',
          'texture_sha256': atlas['png_sha256'], 'materials': sorted(targets),
          'unchanged_objects_checked': len(before['objects']),
          'unchanged_materials_checked': len(before['materials']),
          'ordinary_bakes_require_refresh': True,
          'scope': 'Paint/emission/primary-UV source change only. Canonical export, fresh bakes and engine acceptance follow.'}
(ROOT / 'export/mountain-paint-authoring.json').write_text(json.dumps(report, indent=2) + '\n')
print('MOUNTAIN_PAINT_AUTHORING', report['status'], report['unchanged_objects_checked'], 'objects preserved')
