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


sys.path.insert(0, str(ROOT / 'scripts'))
from pavilion_roof_geometry import outer_shell, face_uv_signature


if args.kind == 'source':
    objects = [o for o in bpy.data.objects if o.type == 'MESH'
               and not o.name.startswith('COL_')
               and o.get('kit_placement') == 'qinfang_pavilion'
               and o.get('kit_part') == 'roof_hex']
    assert len(objects) == 1, [o.name for o in objects]
else:
    objects = []
    for variant in ('roof_hex', 'roof_square'):
        for suffix in ('', '_LOD1'):
            render = [o for o in bpy.data.collections['KIT_pavilion_' + variant + suffix].objects
                      if o.type == 'MESH' and not o.name.startswith('COL_')]
            assert len(render) == 1, (variant, suffix, [o.name for o in render])
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
