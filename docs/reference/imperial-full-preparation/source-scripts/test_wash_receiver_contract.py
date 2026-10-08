"""Exercise actual five/six-surface exports and reject mismatched catalogs.

Constructed manifest corruptions test validation only; they are never installed
or presented as fresh bake evidence.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from lightmap_catalog import eligible_meshes, glb_document
from wash_receiver_contract import CANOPY_MESH, expected_receivers, validate_manifest_receivers

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--candidate', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
current = glb_document(root/'export/garden-of-dreams.glb')
candidate = glb_document(args.candidate)
base_manifest = json.loads((root/'export/lightmaps/backdrop-wash/manifest.json').read_text())
assert len(expected_receivers(current)) == 5
assert len(validate_manifest_receivers(base_manifest, current)) == 5
assert len(expected_receivers(candidate)) == 6
assert CANOPY_MESH not in eligible_meshes(candidate)
assert len(eligible_meshes(candidate)) == len(eligible_meshes(current)) == 124

rejected = []
def reject(label, function):
    try:
        function()
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError(('Invalid receiver contract accepted', label))

reject('five-map catalog on six-surface export', lambda: validate_manifest_receivers(base_manifest, candidate))
fixture = {'lighting': {'receivers': [
    {'source_object': obj, 'mesh': mesh} for obj, mesh in expected_receivers(candidate).items()]},
    'shadow_intent': {CANOPY_MESH:False},
    'records': {name: {'shadow_intent':{CANOPY_MESH:False}} for name in expected_receivers(candidate).values()}}
assert len(validate_manifest_receivers(fixture, candidate)) == 6
for label, mutate in [
    ('omitted receiver', lambda m: m['lighting']['receivers'].pop()),
    ('duplicate receiver', lambda m: m['lighting']['receivers'].append(m['lighting']['receivers'][0])),
    ('substituted source object', lambda m: m['lighting']['receivers'][0].update(source_object='KIT_building')),
    ('missing map', lambda m: m['records'].pop(CANOPY_MESH)),
    ('foreign map', lambda m: m['records'].update(SITE_building={})),
    ('missing scene shadow intent', lambda m: m.pop('shadow_intent')),
    ('wrong map shadow intent', lambda m: m['records'][CANOPY_MESH].update(shadow_intent={CANOPY_MESH:True})),
]:
    bad = copy.deepcopy(fixture)
    mutate(bad)
    reject(label, lambda: validate_manifest_receivers(bad, candidate))
for label, mutate in [
    ('omitted exported moon', lambda d: d['nodes'].remove(next(n for n in d['nodes'] if n['name']=='SITE_stage_MAT_painted_moon'))),
    ('duplicate exported receiver', lambda d: d['nodes'].append(copy.deepcopy(next(n for n in d['nodes'] if n['name']==CANOPY_MESH)))),
    ('unknown painted batch', lambda d: d['nodes'].append({**copy.deepcopy(next(n for n in d['nodes'] if n['name']==CANOPY_MESH)), 'name':'SITE_stage_MAT_stage_canopy_other'})),
    ('missing ceiling flag', lambda d: next(n for n in d['nodes'] if n['name']==CANOPY_MESH)['extras'].pop('godot_cast_shadow')),
    ('nonboolean ceiling flag', lambda d: next(n for n in d['nodes'] if n['name']==CANOPY_MESH)['extras'].update(godot_cast_shadow=0)),
]:
    bad = copy.deepcopy(candidate)
    mutate(bad)
    reject(label, lambda: expected_receivers(bad))
report = {'scope':'Exact receiver validation on actual source exports plus constructed rejection cases. Not fresh lighting or scene acceptance.',
          'current_source_sha256':hashlib.sha256((root/'export/garden-of-dreams.glb').read_bytes()).hexdigest(),
          'candidate_source_sha256':hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
          'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'helper_sha256':hashlib.sha256((root/'scripts/wash_receiver_contract.py').read_bytes()).hexdigest(),
          'ordinary_receivers':124,'current_wash_receivers':5,'candidate_wash_receivers':6,'rejected':rejected}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('WASH_RECEIVER_CONTRACT_PASS', len(rejected), 'rejections; 124 ordinary, 5/6 wash surfaces')
