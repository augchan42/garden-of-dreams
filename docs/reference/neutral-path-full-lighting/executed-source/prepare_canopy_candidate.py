"""Save a painted coved ceiling in a separate Blender candidate.

The exact existing canvas rim supplies the geometry and paint UVs. This is
not source adoption: exported shadow semantics, fresh lighting and final
paint quality still require verification before installation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from moon_paint_contract import ROOT, snapshot, check as check_moon

parser = argparse.ArgumentParser()
parser.add_argument('--output-root', type=Path, required=True)
parser.add_argument('--uv-treatment', choices=('rim-convergent', 'planar-sky'), default='planar-sky')
options = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
destination = options.output_root.resolve()
assert destination != ROOT and ROOT not in destination.parents, 'Use a separate scratch directory'
destination.mkdir(parents=True, exist_ok=True)
assert not (destination / 'authoring.blend').exists(), 'Do not overwrite a prior candidate'
source_file = Path(bpy.data.filepath)
source_digest = hashlib.sha256(source_file.read_bytes()).hexdigest()
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
bpy.context.view_layer.update()
before = snapshot()
moon_before = check_moon()
canvas = bpy.data.objects['KIT_stage_cyclorama']
assert canvas.parent is None
assert 'KIT_stage_painted_canopy' not in bpy.data.objects
paint_index = next(i for i, m in enumerate(canvas.data.materials)
                   if m.name == 'MAT_stage_cyclorama_moonlit')
source_uv = canvas.data.uv_layers[0]
rings = [(1.0, 20.0), (.875, 27.0), (.625, 33.0), (.3125, 37.0), (0.0, 38.0)]
vertices, faces, coordinates, rim_edges = [], [], [], []
for polygon in canvas.data.polygons:
    if polygon.material_index != paint_index:
        continue
    rim = [i for i in polygon.loop_indices
           if abs(canvas.data.vertices[canvas.data.loops[i].vertex_index].co.z - 20) < .001
           and abs(canvas.data.vertices[canvas.data.loops[i].vertex_index].co.xy.length - 48) < .02]
    if len(rim) != 2:
        continue
    edge = [(canvas.data.vertices[canvas.data.loops[i].vertex_index].co.copy(),
             source_uv.data[i].uv.copy()) for i in rim]
    rim_edges.append([[list(point), list(uv)] for point, uv in edge])
    for band in range(len(rings) - 1):
        points, uvs = [], []
        for end, ring in [(0, band), (1, band), (1, band + 1), (0, band + 1)]:
            point, uv = edge[end]
            ratio, height = rings[ring]
            points.append(Vector((point.x * ratio, point.y * ratio, height)))
            if options.uv_treatment == 'rim-convergent':
                uvs.append((.35 + (uv.x - .35) * ratio, uv.y))
            else:
                # Retain the exact wall join, then use a world-planar patch
                # from the moon-free upper sky. This avoids radial UV rays.
                blend = min(1.0, (1.0 - ratio) / .125)
                planar = Vector((.35 + .30 * point.x * ratio / 48,
                                 .90 + .09 * point.y * ratio / 48))
                mapped = uv.lerp(planar, blend)
                uvs.append(tuple(mapped))
        triangles = [(0, 1, 2)] if band == len(rings) - 2 else [(0, 1, 2), (0, 2, 3)]
        for triangle in triangles:
            order = list(triangle)
            normal = (points[order[1]] - points[order[0]]).cross(points[order[2]] - points[order[0]])
            assert normal.length > 1e-8, 'Degenerate canopy face'
            if normal.z > 0:
                order.reverse()
            offset = len(vertices)
            vertices.extend(tuple(points[i]) for i in order)
            faces.append((offset, offset + 1, offset + 2))
            coordinates.append([uvs[i] for i in order])
assert len(rim_edges) == 320, ('Source rim differs from verified native prototype', len(rim_edges))
mesh = bpy.data.meshes.new('Painted coved ceiling candidate')
mesh.from_pydata(vertices, [], faces)
mesh.update()
assert len(mesh.polygons) == 2240 and all(p.normal.z < 0 for p in mesh.polygons)
material = canvas.data.materials[paint_index].copy()
material.name = 'MAT_stage_canopy_paint'
mesh.materials.append(material)
uv = mesh.uv_layers.new(name='UVMap')
for polygon, values in zip(mesh.polygons, coordinates):
    for loop, value in zip(polygon.loop_indices, values):
        uv.data[loop].uv = value
canopy = bpy.data.objects.new('KIT_stage_painted_canopy', mesh)
bpy.data.collections['SITE_stage'].objects.link(canopy)
canopy.matrix_basis = canvas.matrix_basis.copy()
canopy.visible_shadow = False
canopy['godot_cast_shadow'] = False
canopy['canopy_candidate'] = 'exact-rim-cove-' + options.uv_treatment
canopy['paint_quality'] = 'prototype; final paint and fresh wash pending'
receivers = bpy.data.objects['LGT_stage_backdrop_wash'].light_linking.receiver_collection
assert len(receivers.objects) == 5 and canvas in list(receivers.objects)
receivers.objects.link(canopy)
bpy.context.view_layer.update()
after = snapshot()
assert set(after['objects']) - set(before['objects']) == {canopy.name}
assert set(after['materials']) - set(before['materials']) == {material.name}
assert {k: v for k, v in after['materials'].items() if k != material.name} == before['materials']
changed_washes = []
for name, previous in before['objects'].items():
    current = dict(after['objects'][name])
    if previous.get('receivers') and canopy.name in current['receivers']:
        current['receivers'] = [n for n in current['receivers'] if n != canopy.name]
        changed_washes.append(name)
    assert current == previous, ('Existing scene object changed', name)
assert check_moon() == moon_before
bpy.ops.wm.save_as_mainfile(filepath=str(destination / 'authoring.blend'), compress=True)
bpy.data.libraries.write(str(destination / 'SITE_stage.blend'),
                         {bpy.data.collections['SITE_stage']}, fake_user=True, compress=True)
assert hashlib.sha256(source_file.read_bytes()).hexdigest() == source_digest
report = {
    'status': 'scratch_only', 'source_authoring_sha256': source_digest,
    'scope': 'Separately saved exact-rim coved ceiling with inward normals and inherited paint. Existing objects/materials/moon preserved; only linked receiver lists gain canopy. Not installed, freshly baked, exported-shadow verified or final paint acceptance.',
    'unchanged_objects': len(before['objects']), 'unchanged_materials': len(before['materials']),
    'object': canopy.name, 'material': material.name, 'triangles': len(faces),
    'uv_treatment': options.uv_treatment,
    'rim_edges': rim_edges, 'rings_radius_ratio_height': rings,
    'wash_receiver_count': len(receivers.objects), 'changed_wash_receivers': changed_washes,
    'native_shadow_visibility': canopy.visible_shadow,
    'export_shadow_metadata': canopy['godot_cast_shadow'],
    'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.glob('*.blend')},
}
(destination / 'authoring-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
print('CANOPY_AUTHORING_CANDIDATE_PASS', destination, len(faces), len(before['objects']))
