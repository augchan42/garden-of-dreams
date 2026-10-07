"""Check outer roof-shell winding in saved Blender sources.

--scratch-fix flips the identified shell in memory to test the correction.
This script never saves a Blender file or changes canonical exports/bakes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--kind', choices=('source', 'kit'), default='source')
parser.add_argument('--scratch-fix', action='store_true')
parser.add_argument('--report', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])


def components(mesh):
    adjacency = [set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    remaining = set(range(len(mesh.vertices)))
    while remaining:
        pending = [next(iter(remaining))]
        vertices = set()
        while pending:
            index = pending.pop()
            if index in vertices:
                continue
            vertices.add(index)
            pending.extend(adjacency[index] - vertices)
        remaining -= vertices
        yield vertices, [p for p in mesh.polygons if p.vertices[0] in vertices]


def outer_shell(mesh):
    # Both shells have the same five-ring silhouette. The upper shell uses
    # the roof atlas cell; the lower shell uses the timber cell.
    x, y, width, height = json.loads(
        (ROOT / 'textures/atlases/pavilion/atlas.json').read_text()
    )['uv_regions']['MAT_rooftile']
    candidates = []
    for vertices, faces in components(mesh):
        if len(vertices) not in (20, 30) or len(faces) != len(vertices) * 4 // 5 + 1:
            continue
        z = [mesh.vertices[i].co.z for i in vertices]
        if abs(min(z)) > 1e-5 or abs(max(z) - 1.5) > 1e-5:
            continue
        uv = [mesh.uv_layers[0].data[i].uv for p in faces for i in p.loop_indices]
        if all(x <= p.x <= x + width and y <= p.y <= y + height for p in uv):
            candidates.append(faces)
    assert len(candidates) == 1, ('Outer roof shell must be unambiguous', len(candidates))
    return candidates[0]


def face_uv_signature(mesh):
    return [sorted((mesh.loops[i].vertex_index,
                    tuple(tuple(layer.data[i].uv) for layer in mesh.uv_layers))
                   for i in p.loop_indices) for p in mesh.polygons]


if args.kind == 'source':
    objects = [o for o in bpy.data.objects if o.type == 'MESH'
               and not o.name.startswith('COL_')
               and o.get('kit_placement') == 'qinfang_pavilion'
               and o.get('kit_part') == 'roof_hex']
    assert len(objects) == 1, [o.name for o in objects]
else:
    objects = []
    for variant in ('roof_hex', 'roof_square'):
        render = [o for o in bpy.data.collections['KIT_pavilion_' + variant].objects
                  if o.type == 'MESH' and not o.name.startswith('COL_')]
        assert len(render) == 1, (variant, [o.name for o in render])
        objects.extend(render)

records = []
for obj in objects:
    mesh = obj.data
    faces = outer_shell(mesh)
    before = {'vertices': [tuple(v.co) for v in mesh.vertices],
              'uv_by_face_vertex': face_uv_signature(mesh),
              'transform': [list(row) for row in obj.matrix_world]}
    down_before = sum(p.normal.z < -.25 for p in faces)
    if args.scratch_fix:
        for face in faces:
            if face.normal.z < 0:
                face.flip()
        mesh.update()
        assert before['vertices'] == [tuple(v.co) for v in mesh.vertices]
        assert before['uv_by_face_vertex'] == face_uv_signature(mesh)
        assert before['transform'] == [list(row) for row in obj.matrix_world]
    record = {'object': obj.name, 'outer_shell_faces': len(faces),
              'downward_before': down_before,
              'upward_after': sum(p.normal.z > .25 for p in faces),
              'downward_after': sum(p.normal.z < -.25 for p in faces)}
    record['passed'] = record['upward_after'] == len(faces)
    records.append(record)

report = {'source_blend_sha256': hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
          'kind': args.kind, 'scratch_fix': args.scratch_fix,
          'scope': 'Saved outer shell winding; optional in-memory correction preserves vertices, face/vertex UVs and transforms. No source saved or lighting rebaked.',
          'records': records, 'passed': all(r['passed'] for r in records)}
args.report.parent.mkdir(parents=True, exist_ok=True)
args.report.write_text(json.dumps(report, indent=2) + '\n')
print('PAVILION_ROOF_ORIENTATION', json.dumps(records), flush=True)
assert report['passed'], 'Outer painted roof shell points away from the sky'
