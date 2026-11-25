"""Require one canvas infill and preserve every original physical triangle."""
from pathlib import Path
import argparse, collections, hashlib, json, sys
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_mountain_export import Glb

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--before', type=Path, required=True)
parser.add_argument('--after', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
target = 'SITE_stage_MAT_stage_canvas'
report = {'status': 'failed', 'before': str(args.before), 'after': str(args.after),
          'scope': 'Canonical geometry/material/camera/collider preservation and one added canvas box. No lighting, native collision, visual acceptance or adoption.'}

def expanded(glb, primitive, attr):
    return glb.accessor(primitive['attributes'][attr])[glb.accessor(primitive['indices']).ravel()]

def triangle_rows(glb, primitive):
    attrs = sorted(set(primitive['attributes']) - {'TEXCOORD_1'})
    arrays = [expanded(glb, primitive, attr).reshape(-1, 3, expanded(glb, primitive, attr).shape[1]) for attr in attrs]
    rows = []
    for i in range(len(arrays[0])):
        vertices = [b''.join(a[i, v].tobytes() for a in arrays) for v in range(3)]
        # Cyclic rotation retains winding while allowing a different start index.
        rows.append(min(tuple(vertices[j:] + vertices[:j]) for j in range(3)))
    return rows

try:
    old, new = Glb(args.before), Glb(args.after)
    for key in ['asset', 'extensionsUsed', 'extensionsRequired', 'extensions', 'scene', 'scenes', 'cameras', 'nodes']:
        assert old.doc.get(key) == new.doc.get(key), ('Scene/node/light/camera/collider contract changed', key)
    assert len(old.doc['meshes']) == len(new.doc['meshes'])
    assert old.doc['materials'] == new.doc['materials'], 'Material changed'
    assert old.doc.get('samplers') == new.doc.get('samplers') and old.doc.get('textures') == new.doc.get('textures')
    assert {i['name']: old.image_hash(i) for i in old.doc['images']} == {i['name']: new.image_hash(i) for i in new.doc['images']}
    preserved = 0
    added_positions = []
    found = 0
    for node in old.doc['nodes']:
        if 'mesh' not in node:
            continue
        a, b = old.doc['meshes'][node['mesh']], new.doc['meshes'][node['mesh']]
        assert {k: v for k, v in a.items() if k != 'primitives'} == {k: v for k, v in b.items() if k != 'primitives'}, node['name']
        assert len(a['primitives']) == len(b['primitives'])
        for pa, pb in zip(a['primitives'], b['primitives']):
            assert {k: v for k, v in pa.items() if k not in ('attributes', 'indices')} == {k: v for k, v in pb.items() if k not in ('attributes', 'indices')}
            assert pa['attributes'].keys() == pb['attributes'].keys()
            if node['name'] != target:
                for attr in pa['attributes']:
                    assert np.array_equal(expanded(old, pa, attr), expanded(new, pb, attr)), ('Unrelated attribute changed', node['name'], attr)
                preserved += len(old.accessor(pa['indices'])) // 3
                continue
            found += 1
            before_rows, after_rows = triangle_rows(old, pa), triangle_rows(new, pb)
            before_count, after_count = collections.Counter(before_rows), collections.Counter(after_rows)
            assert not (before_count - after_count), 'Original canvas triangle changed or removed'
            extra = after_count - before_count
            assert sum(extra.values()) == 12, ('Expected twelve added box triangles', sum(extra.values()))
            available = extra.copy()
            position = expanded(new, pb, 'POSITION').reshape(-1, 3, 3)
            for i, row in enumerate(after_rows):
                if available[row] > 0:
                    added_positions.extend(position[i]); available[row] -= 1
            assert not any(available.values())
            uv = expanded(new, pb, 'TEXCOORD_1')
            assert np.isfinite(uv).all() and uv.min() >= 0 and uv.max() <= 1, 'Invalid canvas UV2'
            preserved += len(before_rows)
            # Exported positions are local to the unchanged canvas node.
            q = np.asarray(node.get('rotation', [0, 0, 0, 1])); xyz, w = q[:3], q[3]
            rotation = (w*w - xyz@xyz)*np.eye(3) + 2*np.outer(xyz, xyz) + 2*w*np.array([[0,-xyz[2],xyz[1]],[xyz[2],0,-xyz[0]],[-xyz[1],xyz[0],0]])
            assert 'matrix' not in node, 'Handle an explicit canvas matrix before proceeding'
            world = np.asarray(added_positions) @ (rotation @ np.diag(node.get('scale', [1,1,1]))).T + node.get('translation', [0,0,0])
            lo, hi = world.min(axis=0), world.max(axis=0)
            assert np.allclose(lo, [18,-.63,14], atol=1e-5, rtol=0) and np.allclose(hi, [20.2,-.13,21], atol=1e-5, rtol=0), ('Wrong exported infill bounds', lo, hi)
            faces = collections.defaultdict(list)
            edges = collections.Counter()
            for triangle in world.reshape(-1, 3, 3):
                vertices = [tuple(np.round(v, 5)) for v in triangle]
                assert len(set(vertices)) == 3
                plane = [(axis, side) for axis in range(3) for side, bound in enumerate([lo[axis], hi[axis]]) if np.allclose(triangle[:, axis], bound, atol=1e-5, rtol=0)]
                assert len(plane) == 1, ('Triangle is not on one box face', triangle.tolist())
                axis, side = plane[0]
                normal = np.cross(triangle[1]-triangle[0], triangle[2]-triangle[0])
                assert normal[axis] * (-1 if side == 0 else 1) > 0, 'Inward or degenerate box face'
                faces[(axis, side)].append((vertices, float(np.linalg.norm(normal) / 2)))
                for j in range(3): edges[tuple(sorted([vertices[j], vertices[(j+1)%3]]))] += 1
            assert len(faces) == 6 and all(len(rows) == 2 for rows in faces.values())
            assert all(count == 2 for count in edges.values()), 'Exported infill is not a closed manifold'
            for (axis, side), rows in faces.items():
                assert len({v for vertices, area in rows for v in vertices}) == 4
                area = sum(area for vertices, area in rows)
                expected = np.prod([hi[i]-lo[i] for i in range(3) if i != axis])
                assert abs(area-expected) < 1e-5, 'Wrong box face area'
            top_area = sum(area for vertices, area in faces[(1,1)])
            assert abs(top_area - 15.4) < 1e-5
            report.update(added_triangle_count=12, added_world_bounds_min=lo.tolist(), added_world_bounds_max=hi.tolist(),
                          added_closed_manifold=True, added_outward_faces=6, added_top_area_m2=top_area)
    assert found == 1, ('Canvas primitive count changed', found)
    report.update(status='ground_export_preservation_passed', original_triangles_preserved=preserved,
                  before_sha256=hashlib.sha256(old.bytes).hexdigest(), after_sha256=hashlib.sha256(new.bytes).hexdigest(),
                  exact_nodes_materials_cameras_colliders=True, embedded_images_exact=True)
except BaseException as error:
    report['error'] = str(error)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    raise
args.output.write_text(json.dumps(report, indent=2) + '\n')
print('AOJING_GROUND_EXPORT_PRESERVATION_PASS', report['original_triangles_preserved'], report['after_sha256'])
