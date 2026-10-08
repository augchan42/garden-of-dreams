"""Restore explicit mesh shadow intent after Blender imports a GLB.

glTF extras carry the flag; Blender's ray visibility does not transfer itself.
Only explicitly flagged meshes change. Validate all targets before mutation.
"""
import hashlib
import json
from pathlib import Path
import struct


def apply_shadow_intent(source: Path, scene) -> dict:
    blob = source.read_bytes()
    length = struct.unpack_from('<I', blob, 12)[0]
    document = json.loads(blob[20:20 + length])
    requested = {}
    for node in document['nodes']:
        extras = node.get('extras', {})
        if 'godot_cast_shadow' not in extras:
            continue
        assert 'mesh' in node and type(extras['godot_cast_shadow']) is bool, 'Invalid mesh shadow intent'
        name = node['name']
        assert name not in requested, 'Duplicate shadow-intent target'
        obj = scene.objects.get(name)
        assert obj is not None and obj.type == 'MESH', ('Missing shadow-intent mesh', name)
        requested[name] = extras['godot_cast_shadow']
    before = {o.name: o.visible_shadow for o in scene.objects if o.type == 'MESH'}
    for name, value in requested.items():
        scene.objects[name].visible_shadow = value
    after = {o.name: o.visible_shadow for o in scene.objects if o.type == 'MESH'}
    assert all(after[name] == requested.get(name, value) for name, value in before.items())
    return {'source_glb_sha256': hashlib.sha256(blob).hexdigest(),
            'explicit_meshes': requested, 'unchanged_unflagged_meshes': len(before) - len(requested)}
