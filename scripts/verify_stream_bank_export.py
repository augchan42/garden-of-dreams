"""Prove that a bank lighting repair changes only its visible faces' UV2."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from verify_canopy_candidate import Document
from verify_stream_bank_uv import measure

TARGET = 'SITE_qinfang-ting_MAT_pavilion_atlas'


def verify(previous, candidate):
    a, b = Document(previous), Document(candidate)
    assert a.nodes.keys() == b.nodes.keys()
    for field in ('scene', 'scenes', 'extensions', 'cameras'):
        assert a.data.get(field) == b.data.get(field), field
    for name in a.nodes:
        if name != TARGET:
            assert a.node(name) == b.node(name), ('Non-bank receiver changed', name)
    old, new = a.node(TARGET), b.node(TARGET)
    am, bm = old.pop('mesh'), new.pop('mesh')
    assert old == new and len(am) == len(bm) == 1
    assert am[0]['material'] == bm[0]['material']
    measurements = [measure(path, details=True) for path in (previous, candidate)]
    expanded = []
    for _, selected, indices, g in measurements:
        node = next(n for n in g.doc['nodes'] if n.get('name') == TARGET)
        primitive = g.doc['meshes'][node['mesh']]['primitives'][0]
        expanded.append({k: g.accessor(v)[indices] for k, v in primitive['attributes'].items()})
    assert expanded[0].keys() == expanded[1].keys()
    for attribute in expanded[0]:
        if attribute != 'TEXCOORD_1':
            assert np.array_equal(expanded[0][attribute], expanded[1][attribute]), attribute
    mask = measurements[0][1]
    assert np.array_equal(mask, measurements[1][1]) and int(mask.sum()) == 3240
    old_uv, new_uv = (x['TEXCOORD_1'] for x in expanded)
    changed = (old_uv != new_uv).any(axis=(1, 2))
    assert np.array_equal(changed, mask), 'UV2 changed outside the visible banks or omitted a face'
    assert measurements[1][0]['minimum_triangle_texels'] >= 3
    # glTF's V is flipped relative to Blender. The new cells occupy the unused
    # right end of the tile-strip reservation, and no unchanged triangle enters it.
    assert (new_uv[mask, :, 0] >= 672/1024).all()
    assert (new_uv[mask, :, 1] >= 1-140/1024).all()
    other = new_uv[~mask]
    assert not ((other[:, :, 0].max(axis=1) > 672/1024) &
                (other[:, :, 1].max(axis=1) > 1-144/1024)).any(), 'Reserved bank space overlaps another chart'
    return {'status': 'passed', 'previous_source_glb_sha256': hashlib.sha256(a.blob).hexdigest(),
            'source_glb_sha256': hashlib.sha256(b.blob).hexdigest(),
            'unchanged_other_nodes': len(a.nodes)-1, 'changed_uv2_triangles': int(mask.sum()),
            'geometry_normals_primary_uvs_materials_lights_cameras_preserved': True,
            'other_receiver_uv2_preserved': True, 'bank_coverage': measurements[1][0],
            'scope': 'Only 3240 visible bank triangles change UV2. The Qinfang atlas requires a fresh bake; all other receivers can retain their original lighting with explicit compatibility provenance.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('previous', type=Path)
    p.add_argument('candidate', type=Path)
    p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    report = verify(args.previous, args.candidate)
    args.report.write_text(json.dumps(report, indent=2)+'\n')
    print('STREAM_BANK_EXPORT_PASS', report['unchanged_other_nodes'], report['changed_uv2_triangles'])
