"""Verify roof winding/Spot changes against the preceding exported assets.

LOD decimation can triangulate the same planar patch differently after a face
flip. Require identical vertex/UV data and bidirectional triangle-area coverage
for those patches, rather than treating a different diagonal as a shape change.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path

import numpy as np

from verify_mountain_export import Glb

ROOT = Path(__file__).resolve().parents[1]
SPOTS = {'LGT_ouxiang-xie_key', 'LGT_ziling-zhou_key'}
ROOF = 'SITE_qinfang-ting_MAT_pavilion_atlas'
LOD_NORMAL_TOLERANCE = 0.0002


def inverted_normal_error(removed, added, allow_retriangulation=False):
    """Check both normal sets; coplanar LOD diagonals can merge near duplicates."""
    assert removed and added, 'Missing corresponding inverted normal'
    assert all(n[1] < -.25 for n in removed), 'Changed unrelated roof normal'
    assert all(n[1] > .25 for n in added), 'Roof normal still faces downward'
    expected = {tuple(-np.asarray(n)) for n in removed}
    if expected == added:
        return 0.0
    assert allow_retriangulation, 'Changed non-inverted roof normals'
    a, b = np.asarray(list(expected)), np.asarray(list(added))
    distances = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    error = float(max(distances.min(axis=0).max(), distances.min(axis=1).max()))
    assert error <= LOD_NORMAL_TOLERANCE, ('Changed LOD roof normal beyond rounding/retriangulation tolerance', error)
    return error


def tri_key(triangle):
    return tuple(sorted(tuple(np.round(v, 6)) for v in triangle))


def area2(points):
    a = np.asarray(points)
    return abs(float(np.sum(a[:, 0] * np.roll(a[:, 1], -1) - a[:, 1] * np.roll(a[:, 0], -1)))) / 2


def intersection(subject, clip):
    polygon = [p.copy() for p in subject]
    signed = sum(clip[i, 0] * clip[(i + 1) % 3, 1] - clip[i, 1] * clip[(i + 1) % 3, 0] for i in range(3))
    sign = 1 if signed > 0 else -1
    for i in range(3):
        a, b = clip[i], clip[(i + 1) % 3]
        def side(p):
            d, q = b - a, p - a
            return sign * (d[0] * q[1] - d[1] * q[0])
        result = []
        for j, end in enumerate(polygon):
            start = polygon[j - 1]
            ds, de = side(start), side(end)
            if (ds >= 0) != (de >= 0):
                result.append(start + (end - start) * ds / (ds - de))
            if de >= 0:
                result.append(end)
        polygon = result
        if not polygon:
            break
    return area2(polygon) if len(polygon) >= 3 else 0.0


def uncovered(old, new):
    maximum = 0.0
    for triangle in old:
        normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
        magnitude = np.linalg.norm(normal)
        if magnitude < 1e-10:
            continue
        normal /= magnitude
        coplanar = new[np.max(np.abs((new - triangle[0]) @ normal), axis=1) < 1e-5]
        assert len(coplanar), 'Changed nonplanar LOD surface'
        keep = [i for i in range(3) if i != int(np.argmax(np.abs(normal)))]
        projected = triangle[:, keep]
        expected = area2(projected)
        actual = sum(intersection(projected, candidate[:, keep]) for candidate in coplanar)
        error = abs(actual - expected)
        maximum = max(maximum, error)
        assert error <= 1e-8 + expected * 1e-4, ('Changed LOD triangle coverage', expected, actual)
    return maximum


def surface_equivalent(a, b):
    ca, cb = Counter(map(tri_key, a)), Counter(map(tri_key, b))
    common = ca & cb
    def leftovers(triangles):
        remaining = common.copy()
        result = []
        for triangle in triangles:
            key = tri_key(triangle)
            if remaining[key]:
                remaining[key] -= 1
            else:
                result.append(triangle)
        return np.asarray(result, dtype=float).reshape(-1, 3, 3)
    aa, bb = leftovers(a), leftovers(b)
    assert len(aa) == len(bb)
    error = max(uncovered(aa, bb), uncovered(bb, aa)) if len(aa) else 0.0
    return {'retriangulated_triangles': len(aa), 'maximum_projected_coverage_error': error}


def compare(before, after):
    old, new = Glb(before), Glb(after)
    for field in ('asset', 'extensionsUsed', 'extensionsRequired', 'scene', 'scenes', 'cameras', 'nodes'):
        assert old.doc.get(field) == new.doc.get(field), ('Scene/camera/node contract changed', field, before)
    extensions = copy.deepcopy(new.doc.get('extensions', {}))
    old_lights = old.doc.get('extensions', {}).get('KHR_lights_punctual', {}).get('lights', [])
    new_lights = extensions.get('KHR_lights_punctual', {}).get('lights', [])
    assert len(old_lights) == len(new_lights)
    changed_lights = []
    for previous, current in zip(old_lights, new_lights):
        if previous.get('name') in SPOTS:
            outer = previous['spot']['outerConeAngle']
            inner = current['spot']['innerConeAngle']
            assert 0 < outer - inner <= outer * .00011
            assert current['spot']['outerConeAngle'] == outer
            changed_lights.append({'name': previous['name'], 'edge_band_radians': outer - inner})
            current['spot']['innerConeAngle'] = previous['spot']['innerConeAngle']
    assert old.doc.get('extensions', {}) == extensions, 'Changed unrelated light or extension'
    assert len(old.doc['materials']) == len(new.doc['materials'])
    assert [old.material(m) for m in old.doc['materials']] == [new.material(m) for m in new.doc['materials']]
    assert [old.image_hash(i) for i in old.doc.get('images', [])] == [new.image_hash(i) for i in new.doc.get('images', [])]
    roof_records = []
    for a, b in zip(old.doc['nodes'], new.doc['nodes']):
        if 'mesh' not in a:
            continue
        name = a['name']
        ma, mb = old.doc['meshes'][a['mesh']], new.doc['meshes'][b['mesh']]
        assert {k: v for k, v in ma.items() if k != 'primitives'} == {k: v for k, v in mb.items() if k != 'primitives'}
        assert len(ma['primitives']) == len(mb['primitives'])
        roof = name == ROOF or name.startswith('KIT_pavilion_roof_')
        for pa, pb in zip(ma['primitives'], mb['primitives']):
            assert {k: v for k, v in pa.items() if k not in ('attributes', 'indices')} == {k: v for k, v in pb.items() if k not in ('attributes', 'indices')}
            assert set(pa['attributes']) == set(pb['attributes'])
            ia, ib = old.accessor(pa['indices']).ravel(), new.accessor(pb['indices']).ravel()
            assert len(ia) == len(ib)
            va = {key: old.accessor(index)[ia] for key, index in pa['attributes'].items()}
            vb = {key: new.accessor(index)[ib] for key, index in pb['attributes'].items()}
            if not roof:
                assert all(np.array_equal(va[key], vb[key]) for key in va), ('Unrelated mesh changed', name)
                continue
            positions_a, positions_b = va['POSITION'].reshape(-1, 3, 3), vb['POSITION'].reshape(-1, 3, 3)
            surface = surface_equivalent(positions_a.astype(float), positions_b.astype(float))
            fields = sorted(key for key in va if key != 'NORMAL' and not (name == ROOF and key == 'TEXCOORD_1'))
            def vertices(values):
                result = defaultdict(set)
                for i in range(len(values['POSITION'])):
                    key = tuple(np.round(np.concatenate([values[field][i] for field in fields]), 6))
                    result[key].add(tuple(np.round(values['NORMAL'][i], 6)))
                return result
            previous, current = vertices(va), vertices(vb)
            assert previous.keys() == current.keys(), ('Changed roof positions/UV ownership', name)
            normal_changes = 0
            normal_error = 0.0
            # Restrict the finite tolerance to an actual alternate-diagonal LOD.
            # The two-way planar coverage and vertex/UV checks above still apply.
            allow_retriangulation = Path(before).name.endswith('_LOD1.glb') and surface['retriangulated_triangles'] > 0
            for key, normals in previous.items():
                removed, added = normals - current[key], current[key] - normals
                if not removed and not added:
                    continue
                normal_error = max(normal_error, inverted_normal_error(removed, added, allow_retriangulation))
                normal_changes += len(removed)
            assert normal_changes > 0
            uv2 = vb.get('TEXCOORD_1')
            assert uv2 is not None and np.isfinite(uv2).all() and uv2.min() >= -1e-5 and uv2.max() <= 1.00001
            roof_records.append({'node': name, 'normal_vectors_reversed': normal_changes,
                                 'maximum_inverted_normal_error': normal_error,
                                 'normal_tolerance': LOD_NORMAL_TOLERANCE if allow_retriangulation else 0.0,
                                 'triangle_count': len(ia) // 3, **surface})
    return {'before_sha256': hashlib.sha256(old.bytes).hexdigest(),
            'after_sha256': hashlib.sha256(new.bytes).hexdigest(),
            'roofs': roof_records, 'spot_changes': changed_lights}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--after-root', type=Path, default=Path('/tmp/garden-roof-cone-export'))
    parser.add_argument('--after-kits', type=Path, default=Path('/tmp/garden-roof-kit-export/export/kits/pavilion'))
    args = parser.parse_args()
    report = {'scope': 'Current export versus preceding scene: only outward roof normals/associated winding and new roof-batch UV2 packing, plus minimum strict Spot inner angles. LOD alternate diagonals require identical vertex/UV data and bidirectional planar coverage. Not lighting/render acceptance.',
              'master': compare('/tmp/garden-roof-cone-before.glb', args.after_root / 'export/garden-of-dreams.glb'),
              'sites': {}, 'kits': {}, 'unchanged_sites': []}
    for old in sorted(Path('/tmp/garden-roof-cone-sites-before').glob('*.glb')):
        new = args.after_root / 'export/sites' / old.name
        if old.name in {'SITE_qinfang-ting.glb', 'SITE_ouxiang-xie.glb', 'SITE_ziling-zhou.glb'}:
            report['sites'][old.name] = compare(old, new)
        else:
            assert old.read_bytes() == new.read_bytes(), ('Unrelated site export changed', old.name)
            report['unchanged_sites'].append(old.name)
    for new in sorted(args.after_kits.glob('*.glb')):
        report['kits'][new.name] = compare(Path('/tmp/garden-roof-kit-exports-before') / new.name, new)
    (ROOT / 'export/roof-cone-export-preservation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('ROOF_CONE_EXPORT_PRESERVATION_PASS', len(report['unchanged_sites']), 'unchanged sites;', len(report['kits']), 'roof/LOD exports')


if __name__ == '__main__':
    main()
