"""Prepare matching visible/collision floor joints in a separate saved scene.

Never modifies the canonical scene, libraries, exports or lighting. Adoption
requires fresh exports, lighting and actual imported traversal/visual checks.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from moon_paint_contract import ROOT, snapshot, check as check_moon

parser = argparse.ArgumentParser()
parser.add_argument('--output-root', type=Path, required=True)
parser.add_argument('--surface-lift', type=float, default=0.0,
                    help='Small matching visible/collider lift to avoid coplanar overlap')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
destination = args.output_root.resolve()
assert 0 <= args.surface_lift <= .005, 'Floor inserts allow at most a 5 mm lift'
assert ROOT not in destination.parents and destination != ROOT, 'Use a separate scratch directory'
destination.mkdir(parents=True, exist_ok=True)
assert not (destination / 'authoring.blend').exists(), 'Do not overwrite a prior candidate'
input_file = Path(bpy.data.filepath)
input_digest = hashlib.sha256(input_file.read_bytes()).hexdigest()
proposal_file = ROOT / 'docs/reference/full-garden-traversal/candidate-seams.json'
proposal = json.loads(proposal_file.read_text())
bounds = json.loads((proposal_file.parent / 'source-bounds.json').read_text())
assert bounds['authoring_sha256'] == input_digest, 'Diagnosed source differs from this saved source'
assert proposal['status'] == 'proposal_only' and len(proposal['seams']) == 8
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
bpy.context.view_layer.update()
before = snapshot()
moon_before = check_moon()
records = []
created = set()
faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
corners = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
           (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
for seam in proposal['seams']:
    x, height, godot_z = seam['position_godot']
    sx, thickness, godot_depth = seam['size_godot']
    position = Vector((x, -godot_z, height + args.surface_lift))
    size = Vector((sx, godot_depth, thickness))
    assert abs(height + thickness / 2) < 1e-6, 'Floor top must remain at zero'
    collection = bpy.data.collections['SITE_' + seam['site']]
    for collision in (False, True):
        name = ('COL_' if collision else 'KIT_') + 'floor_joint_' + seam['name']
        assert name not in bpy.data.objects
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata([tuple(position[i] + c[i] * size[i] / 2 for i in range(3))
                          for c in corners], [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        obj['floor_joint_proposal'] = seam['name']
        obj['floor_surface_lift'] = args.surface_lift
        if collision:
            obj.hide_render = True
            obj.display_type = 'WIRE'
            obj['godot_collision'] = 'box'
        else:
            mesh.materials.append(bpy.data.materials[seam['visible_material']])
            uv = mesh.uv_layers.new(name='UVMap')
            # Metre-scale planar UVs on each box face; the exporter separately
            # packs lightmap UVs with the other site/material surfaces.
            for face in mesh.polygons:
                axes = (0, 1) if abs(face.normal.z) > .5 else (0, 2) if abs(face.normal.y) > .5 else (1, 2)
                for loop_index in face.loop_indices:
                    vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
                    uv.data[loop_index].uv = (vertex[axes[0]], vertex[axes[1]])
        created.add(name)
        records.append({'name': name, 'site': seam['site'], 'collision': collision,
                        'position_source_z_up': list(position), 'size_source_z_up': list(size),
                        'top_height': args.surface_lift, 'material': None if collision else seam['visible_material']})
bpy.context.view_layer.update()
after = snapshot()
assert set(after['objects']) - set(before['objects']) == created
assert {k: v for k, v in after['objects'].items() if k not in created} == before['objects'], 'Existing scene objects changed'
assert after['materials'] == before['materials'], 'Existing materials changed'
assert check_moon() == moon_before, 'Moon painting changed'
bpy.ops.wm.save_as_mainfile(filepath=str(destination / 'authoring.blend'), compress=True)
for slug in ('terminal-cells', 'qinfang-ting'):
    bpy.data.libraries.write(str(destination / ('SITE_' + slug + '.blend')),
                             {bpy.data.collections['SITE_' + slug]}, fake_user=True, compress=True)
assert hashlib.sha256(input_file.read_bytes()).hexdigest() == input_digest, 'Canonical source was modified'
report = {'status': 'scratch_only', 'source_authoring_sha256': input_digest,
          'proposal_sha256': hashlib.sha256(proposal_file.read_bytes()).hexdigest(),
          'scope': 'Eight visible floor inserts with matching colliders in a separate saved candidate. Existing objects/materials/moon preserved. Not adopted or rendered; new geometry requires export, fresh lighting and engine verification.',
          'unchanged_objects': len(before['objects']), 'added_objects': records,
          'surface_lift': args.surface_lift,
          'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.glob('*.blend')}}
(destination / 'authoring-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
print('FLOOR_SEAM_AUTHORING_CANDIDATE_PASS', destination, len(before['objects']), len(records))
