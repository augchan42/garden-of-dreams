"""Exact painted receivers shared by source bakes and wash installation.

The ceiling is optional only when absent from the actual exported scene. A
six-surface source cannot accept a five-surface bake or a substituted receiver.
"""
from collections import Counter

SOURCE_MESHES = {
    'KIT_stage_cyclorama': 'SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas',
    'KIT_stage_painted_moon': 'SITE_stage_MAT_painted_moon',
    'KIT_stage_painted_mountain_layer': 'SITE_stage_MAT_painted_mountains_0',
    'KIT_stage_painted_mountain_layer.001': 'SITE_stage_MAT_painted_mountains_1',
    'KIT_stage_painted_mountain_layer.002': 'SITE_stage_MAT_painted_mountains_2',
}
CANOPY_OBJECT = 'KIT_stage_painted_canopy'
CANOPY_MESH = 'SITE_stage_MAT_stage_canopy_paint'


def expected_receivers(document: dict) -> dict[str, str]:
    meshes = [n for n in document['nodes'] if 'mesh' in n]
    counts = Counter(n['name'] for n in meshes)
    expected = dict(SOURCE_MESHES)
    if counts[CANOPY_MESH]:
        expected[CANOPY_OBJECT] = CANOPY_MESH
        canopy = next(n for n in meshes if n['name'] == CANOPY_MESH)
        assert canopy.get('extras', {}).get('godot_cast_shadow') is False, 'Ceiling shadow intent missing'
        primitives = document['meshes'][canopy['mesh']]['primitives']
        assert all(document['materials'][p['material']]['name'] == 'MAT_stage_canopy_paint'
                   for p in primitives), 'Ceiling paint material changed'
    for name in expected.values():
        assert counts[name] == 1, ('Missing or duplicate painted receiver', name, counts[name])
    painted = {n['name'] for n in meshes if n['name'].startswith((
        'SITE_stage_MAT_stage_cyclorama_', 'SITE_stage_MAT_cyclorama',
        'SITE_stage_MAT_painted_mountain', 'SITE_stage_MAT_painted_moon',
        'SITE_stage_MAT_stage_canopy_'))}
    assert painted == set(expected.values()), ('Unexpected painted receiver', painted ^ set(expected.values()))
    return expected


def validate_source_receivers(objects, document: dict) -> dict[str, str]:
    expected = expected_receivers(document)
    actual = [o.name for o in objects]
    assert Counter(actual) == Counter(expected.keys()), ('Saved wash receiver set differs from export', actual, expected)
    for obj in objects:
        assert obj.type == 'MESH' and obj.parent is None, ('Invalid source receiver', obj.name)
        target = 'SITE_stage_' + '_'.join(m.name for m in obj.data.materials)
        assert target == expected[obj.name], ('Source paint batch differs from export', obj.name, target)
        if obj.name == CANOPY_OBJECT:
            assert obj.visible_shadow is False and obj.get('godot_cast_shadow') is False
    return expected


def validate_manifest_receivers(manifest: dict, document: dict) -> set[str]:
    expected = expected_receivers(document)
    receivers = manifest['lighting']['receivers']
    actual = [(r['source_object'], r['mesh']) for r in receivers]
    assert Counter(actual) == Counter(expected.items()), ('Bake receiver list differs from export', actual, expected)
    names = set(expected.values())
    assert set(manifest['records']) == names, 'Missing or substituted receiver maps'
    flags = {n['name']: n['extras']['godot_cast_shadow'] for n in document['nodes']
             if 'mesh' in n and 'godot_cast_shadow' in n.get('extras', {})}
    assert all(type(value) is bool for value in flags.values()), 'Invalid exported shadow flag'
    assert manifest.get('shadow_intent', {}) == flags, 'Wash scene shadow intent differs from export'
    assert all(r.get('shadow_intent', {}) == flags for r in manifest['records'].values()), 'Wash map shadow intent differs from export'
    return names
