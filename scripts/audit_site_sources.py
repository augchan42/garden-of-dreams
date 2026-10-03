"""Inspect saved source libraries and export coverage without editing scene files.

Run with Blender --background --python-exit-code 1 --python this-file.
This records structural evidence, not visual acceptance or route verification.
"""
import hashlib
import json
import struct
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gltf(path):
    data = path.read_bytes()
    return json.loads(data[20:20 + struct.unpack_from('<I', data, 12)[0]])


def inspect(collection):
    objects = list(collection.all_objects)
    signs = []
    for obj in objects:
        if obj.type == 'FONT':
            signs.append({'name': obj.name, 'text': obj.data.body,
                          'kind': 'typeset geometry', 'finish': obj.get('finish', '')})
        elif obj.get('inscription_text') or ('title' in obj.name.lower() and obj.type == 'MESH'):
            images = sorted({node.image.name for mat in obj.data.materials if mat and mat.use_nodes
                             for node in mat.node_tree.nodes if node.type == 'TEX_IMAGE' and node.image})
            signs.append({'name': obj.name, 'text': obj.get('inscription_text', ''),
                          'kind': 'textured mesh' if images else 'mesh', 'images': images})
    structural = {}
    for obj in objects:
        if obj.name.startswith(('TRG_', 'COL_', 'CAM_', 'LGT_')):
            structural[obj.name] = {
                'type': obj.type,
                'matrix': [round(value, 6) for row in obj.matrix_world for value in row],
                'room_id': obj.get('room_id'),
            }
            if obj.type == 'CAMERA':
                structural[obj.name]['projection'] = {
                    'lens_mm': obj.data.lens,
                    'sensor_fit': obj.data.sensor_fit,
                    'sensor_width': obj.data.sensor_width,
                    'sensor_height': obj.data.sensor_height,
                    'clip_start': obj.data.clip_start,
                    'clip_end': obj.data.clip_end,
                    'runtime_fov': obj.get('runtime_camera_fov'),
                    'runtime_fit': obj.get('runtime_camera_fit'),
                    'runtime_viewport': list(obj['runtime_camera_viewport'])
                        if 'runtime_camera_viewport' in obj else None,
                }
    return {
        'object_count': len(objects),
        'signs': signs,
        'triggers': [{'name': obj.name, 'room_id': obj.get('room_id')}
                     for obj in objects if obj.name.startswith('TRG_')],
        'cameras': [{'name': obj.name, 'lens_mm': obj.data.lens,
                     'position': list(obj.location)} for obj in objects if obj.type == 'CAMERA'],
        'colliders': sum(obj.name.startswith('COL_') for obj in objects),
        'structural': structural,
    }


source = ROOT / 'export/garden-of-dreams.glb'
source_hash = sha(source)
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'blender/authoring.blend'))
authoring = {c.name.removeprefix('SITE_'): inspect(c) for c in bpy.data.collections
             if c.name.startswith('SITE_') and (ROOT / 'docs/sites' / (c.name[5:] + '.md')).exists()}
assert len(authoring) == 14, sorted(authoring)
records = [json.loads(path.read_text()) for path in (ROOT / 'export/lightmaps').glob('*.json')]
fresh = {r['mesh'] for r in records if r.get('source_glb_sha256') == source_hash
         and (ROOT / 'export/lightmaps' / r['texture']).exists()}
report = {'source_glb_sha256': source_hash, 'authoring_sha256': sha(ROOT / 'blender/authoring.blend'),
          'scope': 'Saved library structure, sign implementation, and source-matched bake records. '
                   'Does not prove art quality, routes, runtime bake application, references, or performance.',
          'sites': {}}
for slug in sorted(authoring):
    path = ROOT / 'blender/sites' / ('SITE_' + slug + '.blend')
    bpy.ops.wm.open_mainfile(filepath=str(path))
    saved = inspect(bpy.data.collections['SITE_' + slug])
    master = authoring[slug]
    saved_structure = saved.pop('structural')
    master_structure = master.pop('structural')
    differing = sorted(name for name in set(saved_structure) | set(master_structure)
                       if saved_structure.get(name) != master_structure.get(name))
    doc = gltf(ROOT / 'export/sites' / ('SITE_' + slug + '.glb'))
    expected = []
    for node in doc.get('nodes', []):
        if 'mesh' not in node or node.get('name', '').startswith('COL_'):
            continue
        mats = [doc['materials'][p['material']] for p in doc['meshes'][node['mesh']]['primitives']]
        if node['name'] != 'HERO_gate_water_drips.001' and any(m.get('alphaMode', 'OPAQUE') != 'OPAQUE' for m in mats):
            continue
        if any(m['name'] in ('MAT_water', 'MAT_aojing_water', 'MAT_fog_plane', 'MAT_stage_backstage')
               or m['name'].startswith('MAT_stage_cyclorama_') for m in mats):
            continue
        expected.append(node['name'])
    saved.update({
        'library_sha256': sha(path),
        'sheet_sha256': sha(ROOT / 'docs/sites' / (slug + '.md')),
        'export_sha256': sha(ROOT / 'export/sites' / ('SITE_' + slug + '.glb')),
        'master_object_count': master['object_count'],
        'structural_differences_from_authoring': differing,
        'signs_match_authoring': saved['signs'] == master['signs'],
        'source_matched_bakes': len(set(expected) & fresh),
        'expected_opaque_bake_meshes': len(expected),
        'missing_current_bakes': sorted(set(expected) - fresh),
        'triggers_without_room_id': [t['name'] for t in saved['triggers'] if not t['room_id']],
    })
    report['sites'][slug] = saved
    print('SITE_AUDIT', slug, 'typeset', sum(s['kind'] == 'typeset geometry' for s in saved['signs']),
          'bakes', saved['source_matched_bakes'], '/', len(expected), 'structural differences', len(differing))
(ROOT / 'export/site-source-audit.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
assert sha(ROOT / 'export/garden-of-dreams.glb') == source_hash
assert sha(ROOT / 'blender/authoring.blend') == report['authoring_sha256']
print('SITE_SOURCE_AUDIT_RECORDED', len(report['sites']), 'sites; scene files unchanged')
