"""Verify physical export preservation for the four plain-material colors."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from garden_material_palette import COMMON_BASE_COLORS
from verify_mountain_export import Glb

parser = argparse.ArgumentParser()
parser.add_argument('--before', type=Path, required=True)
parser.add_argument('--after', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
old, new = Glb(args.before), Glb(args.after)
for key in ['asset', 'extensionsUsed', 'extensionsRequired', 'extensions', 'scene', 'scenes', 'cameras']:
    assert old.doc.get(key) == new.doc.get(key), ('Scene contract changed', key)
assert old.doc['nodes'] == new.doc['nodes'], 'Node/camera/collision/marker/light contract changed'
triangles = 0
for node in old.doc['nodes']:
    if 'mesh' not in node:
        continue
    a, b = old.doc['meshes'][node['mesh']], new.doc['meshes'][node['mesh']]
    assert {k:v for k,v in a.items() if k != 'primitives'} == {k:v for k,v in b.items() if k != 'primitives'}
    assert len(a['primitives']) == len(b['primitives'])
    for pa, pb in zip(a['primitives'], b['primitives']):
        assert {k:v for k,v in pa.items() if k not in ('attributes','indices')} == {k:v for k,v in pb.items() if k not in ('attributes','indices')}
        assert pa['attributes'].keys() == pb['attributes'].keys()
        ia, ib = old.accessor(pa['indices']).ravel(), new.accessor(pb['indices']).ravel()
        assert len(ia) == len(ib)
        triangles += len(ia)//3
        for attr in pa['attributes']:
            assert np.array_equal(old.accessor(pa['attributes'][attr])[ia], new.accessor(pb['attributes'][attr])[ib]), ('Physical attribute changed', node['name'], attr)
om = {m['name']:old.material(m) for m in old.doc['materials']}
nm = {m['name']:new.material(m) for m in new.doc['materials']}
assert om.keys() == nm.keys()
changed = []
for name in om:
    a, b = om[name], nm[name]
    if name in COMMON_BASE_COLORS:
        previous = a['pbrMetallicRoughness'].pop('baseColorFactor')
        color = b['pbrMetallicRoughness'].pop('baseColorFactor')
        assert np.allclose(color, [*COMMON_BASE_COLORS[name],1], atol=1e-7, rtol=0)
        assert previous != color
        changed.append(name)
    assert a == b, ('Other material property changed', name)
assert set(changed) == set(COMMON_BASE_COLORS)
assert {i['name']:old.image_hash(i) for i in old.doc['images']} == {i['name']:new.image_hash(i) for i in new.doc['images']}
report = {'status':'palette_export_geometry_and_material_contract_passed',
          'before_sha256':hashlib.sha256(old.bytes).hexdigest(),
          'after_sha256':hashlib.sha256(new.bytes).hexdigest(),
          'nodes_checked':len(old.doc['nodes']), 'indexed_triangles_checked':triangles,
          'changed_material_base_colors':sorted(changed), 'embedded_images_unchanged':True,
          'scope':'All expanded geometry/indexed attributes including both UVs and every node contract unchanged; only four exact baseColorFactors differ. Roughness, emission, texture references and other materials are preserved.'}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('GARDEN_PALETTE_EXPORT_PRESERVATION_PASS', report['after_sha256'])
