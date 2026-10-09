"""Verify that only the canvas base color changes in the candidate exports."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import numpy as np

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette'
candidate = work / 'candidate'
sys.path.insert(0, str(repo / 'scripts'))
from verify_mountain_export import Glb
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
a = Glb(repo / 'export/garden-of-dreams.glb')
b = Glb(candidate / 'export/garden-of-dreams.glb')
am = {m['name']: a.material(m) for m in a.doc['materials']}
bm = {m['name']: b.material(m) for m in b.doc['materials']}
assert am.keys() == bm.keys()
target = 'MAT_stage_canvas'
old_color = am[target]['pbrMetallicRoughness']['baseColorFactor']
new_color = bm[target]['pbrMetallicRoughness']['baseColorFactor']
assert np.allclose(old_color, [.055, .095, .037, 1], atol=1e-6, rtol=0)
assert np.allclose(new_color, [.065, .060, .055, 1], atol=1e-6, rtol=0)
normal = copy.deepcopy(bm)
normal[target]['pbrMetallicRoughness']['baseColorFactor'] = old_color
assert am == normal, 'Other material/texture properties changed'
for key in ['cameras', 'extensionsUsed', 'extensionsRequired', 'extensions']:
    assert a.doc.get(key) == b.doc.get(key), key
an = {n['name']: n for n in a.doc['nodes']}
bn = {n['name']: n for n in b.doc['nodes']}
assert an.keys() == bn.keys()


def node_contract(n, g):
    result = {k: v for k, v in n.items() if k not in ['mesh', 'children']}
    if 'children' in n:
        result['children_names'] = [g.doc['nodes'][i]['name'] for i in n['children']]
    return result


mesh_nodes = 0
for name, node in an.items():
    other = bn[name]
    assert node_contract(node, a) == node_contract(other, b), name
    if 'mesh' not in node:
        continue
    old_primitives = a.doc['meshes'][node['mesh']]['primitives']
    new_primitives = b.doc['meshes'][other['mesh']]['primitives']
    assert len(old_primitives) == len(new_primitives)
    for old, new in zip(old_primitives, new_primitives):
        assert old['attributes'].keys() == new['attributes'].keys()
        assert {k: v for k, v in old.items() if k not in ['attributes', 'indices', 'material']} == {k: v for k, v in new.items() if k not in ['attributes', 'indices', 'material']}
        if 'material' in old:
            assert a.doc['materials'][old['material']]['name'] == b.doc['materials'][new['material']]['name']
        else:
            assert 'material' not in new
        oi = a.accessor(old['indices']).reshape(-1)
        ni = b.accessor(new['indices']).reshape(-1)
        assert len(oi) == len(ni)
        for attribute in old['attributes']:
            x = a.accessor(old['attributes'][attribute])[oi]
            y = b.accessor(new['attributes'][attribute])[ni]
            assert x.shape == y.shape and np.allclose(x, y, atol=1e-6, rtol=0), (name, attribute)
    mesh_nodes += 1
sites = {}
for path in sorted((candidate / 'export/sites').glob('*.glb')):
    same = sha(path) == sha(repo / 'export/sites' / path.name)
    assert same == (path.name != 'SITE_stage.glb'), path.name
    sites[path.name] = {'sha256': sha(path), 'unchanged': same}
assert len(sites) == 15 and sum(p['unchanged'] for p in sites.values()) == 14
counts = {'cameras': sum('camera' in n for n in bn.values()),
          'colliders': sum(n.startswith('COL_') for n in bn),
          'markers': sum(n.startswith('TRG_') for n in bn)}
assert counts == {'cameras': 42, 'colliders': 454, 'markers': 71}
manifest = json.loads((candidate / 'export/manifest.json').read_text())
assert manifest['total_triangles'] == 266336 and manifest['total_render_meshes'] == 167
report = {'status': 'canvas_palette_export_preservation_passed',
          'baseline_glb_sha256': sha(a.path), 'candidate_glb_sha256': sha(b.path),
          'candidate_authoring_sha256': sha(candidate / 'blender/authoring.blend'),
          'material': target, 'old_linear_rgba': old_color, 'new_linear_rgba': new_color,
          'preserved_mesh_nodes': mesh_nodes, 'counts': counts,
          'triangles': 266336, 'render_meshes': 167, 'site_exports': sites,
          'scope': 'Only visible canvas base color changes. All expanded mesh position/normal/UV attributes, cameras, lights, hierarchy, COL/markers and other material/texture contracts preserved; fourteen non-stage site GLBs byte-exact. No native appearance or matching fresh lighting acceptance.'}
(candidate / 'export-preservation.json').write_text(json.dumps(report, indent=2) + '\n')
print('CANVAS_PALETTE_EXPORT_PRESERVATION', mesh_nodes, 'meshes;', 14, 'byte-exact non-stage site GLBs')
