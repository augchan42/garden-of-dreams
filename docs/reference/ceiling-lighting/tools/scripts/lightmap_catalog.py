"""Eligibility shared by complete-garden lightmap installation and verification."""
import json
from pathlib import Path
import struct


def glb_document(path: Path) -> dict:
    data = path.read_bytes()
    size = struct.unpack_from('<I', data, 12)[0]
    return json.loads(data[20:20 + size])


def eligible_meshes(document: dict) -> set[str]:
    names = set()
    for node in document['nodes']:
        if 'mesh' not in node or node.get('name', '').startswith('COL_'):
            continue
        materials = [document['materials'][p['material']]
                     for p in document['meshes'][node['mesh']]['primitives']]
        if node['name'] != 'HERO_gate_water_drips.001' and any(
                m.get('alphaMode', 'OPAQUE') != 'OPAQUE' for m in materials):
            continue
        if any(m['name'] in ('MAT_water', 'MAT_aojing_water', 'MAT_fog_plane',
                              'MAT_stage_backstage', 'MAT_stage_canopy_paint') or
               m['name'].startswith('MAT_stage_cyclorama_') for m in materials):
            continue
        assert node['name'] not in names, 'Duplicate bake target'
        names.add(node['name'])
    return names
