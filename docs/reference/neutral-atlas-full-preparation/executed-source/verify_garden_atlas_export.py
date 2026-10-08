"""Verify a scene export in which only two architectural color images change."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
from verify_mountain_export import Glb

ATLAS_MATERIALS = {'MAT_pavilion_atlas': 'pavilion', 'MAT_wall_atlas': 'wall'}


def compare(before, after, baseline_root, candidate_root, require_both=True):
    old, new = Glb(before), Glb(after)
    for key in ('asset', 'extensionsUsed', 'extensionsRequired', 'extensions',
                'scene', 'scenes', 'cameras', 'animations', 'skins'):
        assert old.doc.get(key) == new.doc.get(key), ('Scene contract changed', key)
    assert old.doc['nodes'] == new.doc['nodes'], 'Node/camera/collision/light contract changed'
    assert len(old.doc['meshes']) == len(new.doc['meshes'])
    triangles = 0
    for a, b in zip(old.doc['meshes'], new.doc['meshes']):
        assert {k:v for k,v in a.items() if k != 'primitives'} == {
            k:v for k,v in b.items() if k != 'primitives'}
        assert len(a['primitives']) == len(b['primitives'])
        for pa, pb in zip(a['primitives'], b['primitives']):
            assert {k:v for k,v in pa.items() if k not in ('attributes', 'indices')} == {
                k:v for k,v in pb.items() if k not in ('attributes', 'indices')}
            assert pa['attributes'].keys() == pb['attributes'].keys()
            ia, ib = old.accessor(pa['indices']).ravel(), new.accessor(pb['indices']).ravel()
            assert len(ia) == len(ib) and len(ia) % 3 == 0
            triangles += len(ia) // 3
            for attribute in pa['attributes']:
                assert np.array_equal(old.accessor(pa['attributes'][attribute])[ia],
                                      new.accessor(pb['attributes'][attribute])[ib]), (
                                          'Physical attribute changed', a.get('name'), attribute)
    om = {m['name']: old.material(m) for m in old.doc['materials']}
    nm = {m['name']: new.material(m) for m in new.doc['materials']}
    assert om.keys() == nm.keys()
    target_materials = om.keys() & ATLAS_MATERIALS.keys()
    if require_both:
        assert target_materials == ATLAS_MATERIALS.keys(), 'Expected both atlas materials'
    else:
        assert target_materials, 'Expected at least one atlas material'
    changed = {}
    for name in om:
        a, b = copy.deepcopy(om[name]), copy.deepcopy(nm[name])
        if name in ATLAS_MATERIALS:
            kind = ATLAS_MATERIALS[name]
            channel = kind + '_basecolor.png'
            expected_old = hashlib.sha256((baseline_root/'textures/atlases'/kind/channel).read_bytes()).hexdigest()
            expected_new = hashlib.sha256((candidate_root/'textures/atlases'/kind/channel).read_bytes()).hexdigest()
            assert expected_old != expected_new, 'An actual color change is required'
            old_texture = a['pbrMetallicRoughness']['baseColorTexture']['index']
            new_texture = b['pbrMetallicRoughness']['baseColorTexture']['index']
            assert old_texture['source'] == expected_old, ('Unexpected baseline image', name)
            assert new_texture['source'] == expected_new, ('Wrong candidate color image', name)
            old_texture['source'] = new_texture['source']
            changed[kind + '_basecolor'] = {'before_sha256':expected_old, 'after_sha256':expected_new}
        assert a == b, ('Other material or texture property changed', name)
    old_images = {i['name']:old.image_hash(i) for i in old.doc['images']}
    new_images = {i['name']:new.image_hash(i) for i in new.doc['images']}
    assert len(old_images) == len(old.doc['images']) and len(new_images) == len(new.doc['images']), 'Duplicate image names'
    assert old_images.keys() == new_images.keys(), 'Image inventory changed'
    old_metadata = {i['name']:{k:v for k,v in i.items() if k != 'bufferView'} for i in old.doc['images']}
    new_metadata = {i['name']:{k:v for k,v in i.items() if k != 'bufferView'} for i in new.doc['images']}
    assert old_metadata == new_metadata, 'Image metadata changed'
    assert old.doc.get('samplers') == new.doc.get('samplers'), 'Sampler inventory changed'
    assert len(old.doc['textures']) == len(new.doc['textures']), 'Texture inventory changed'
    replacements = {row['before_sha256']:row['after_sha256'] for row in changed.values()}
    for index in range(len(old.doc['textures'])):
        a, b = old.texture(index), new.texture(index)
        a['source'] = replacements.get(a['source'], a['source'])
        assert a == b, ('Texture binding changed', index)
    assert set(changed) == {ATLAS_MATERIALS[name]+'_basecolor' for name in target_materials}
    assert {name for name in old_images if old_images[name] != new_images[name]} == set(changed), 'Other embedded image changed'
    for name, row in changed.items():
        assert old_images[name] == row['before_sha256'] and new_images[name] == row['after_sha256']
    return {'status':'architecture_atlas_export_preservation_passed',
            'before_sha256':hashlib.sha256(old.bytes).hexdigest(),
            'after_sha256':hashlib.sha256(new.bytes).hexdigest(),
            'nodes_checked':len(old.doc['nodes']), 'meshes_checked':len(old.doc['meshes']),
            'indexed_triangles_checked':triangles, 'changed_images':changed,
            'unchanged_images':len(old_images)-len(changed),
            'scope':'Every expanded indexed attribute, both UVs, node, material, sampler and unrelated embedded image preserved. Only two exact atlas color images change. Fresh lighting and native visual acceptance remain required.'}


def main():
    parser = argparse.ArgumentParser()
    for flag in ('before', 'after', 'baseline-root', 'candidate-root', 'output'):
        parser.add_argument('--'+flag, type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.before, args.after, args.baseline_root, args.candidate_root)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('GARDEN_ATLAS_EXPORT_PRESERVATION_PASS', report['after_sha256'])


if __name__ == '__main__':
    main()
