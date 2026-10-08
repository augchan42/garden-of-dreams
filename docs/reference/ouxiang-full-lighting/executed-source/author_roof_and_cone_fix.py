"""Correct native outer roof winding and hard Spot export cones.

Run against authoring.blend with --kind source, or KIT_pavilion.blend with
--kind kit. Saving requires --apply. Geometry positions, UV assignments,
materials, cameras, collisions and unrelated lights must remain unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pavilion_roof_geometry import orient_outer_shell, face_uv_signature

parser = argparse.ArgumentParser()
parser.add_argument('--kind', choices=('source', 'kit'), required=True)
parser.add_argument('--apply', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
spot_names = {'LGT_ouxiang-xie_key', 'LGT_ziling-zhou_key'} if args.kind == 'source' else set()


def simple_properties(data, exclude=()):
    result = {}
    for prop in data.bl_rna.properties:
        if prop.is_readonly or prop.identifier in exclude or prop.type not in ('BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'):
            continue
        value = getattr(data, prop.identifier)
        result[prop.identifier] = (sorted(value) if isinstance(value, set)
                                   else list(value) if getattr(prop, 'is_array', False) else value)
    return result


def fingerprint(mesh):
    values = {'positions': [tuple(v.co) for v in mesh.vertices],
              'faces': [tuple(p.vertices) for p in mesh.polygons],
              'uv': face_uv_signature(mesh),
              'materials': [m.name if m else None for m in mesh.materials],
              'indices': [p.material_index for p in mesh.polygons]}
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


if args.kind == 'source':
    roofs = [o for o in bpy.data.objects if o.type == 'MESH'
             and not o.name.startswith('COL_')
             and o.get('kit_placement') == 'qinfang_pavilion'
             and o.get('kit_part') == 'roof_hex']
    assert len(roofs) == 1
else:
    roofs = []
    for variant in ('roof_hex', 'roof_square'):
        for suffix in ('', '_LOD1'):
            objects = [o for o in bpy.data.collections['KIT_pavilion_' + variant + suffix].objects
                       if o.type == 'MESH' and not o.name.startswith('COL_')]
            assert len(objects) == 1
            roofs.extend(objects)
    assert len({o.data.as_pointer() for o in roofs}) == 4

roof_names = {o.name for o in roofs}


def snapshot():
    result = {}
    for obj in bpy.data.objects:
        record = {'type': obj.type, 'matrix': [list(row) for row in obj.matrix_world],
                  'hidden': [obj.hide_viewport, obj.hide_render],
                  'modifiers': [simple_properties(m) for m in obj.modifiers]}
        if obj.type == 'MESH' and obj.name not in roof_names:
            record['mesh'] = fingerprint(obj.data)
        elif obj.type == 'LIGHT':
            record['light'] = simple_properties(obj.data, ('spot_blend',) if obj.name in spot_names else ())
            receivers = obj.light_linking.receiver_collection
            record['receivers'] = sorted(o.name for o in receivers.objects) if receivers else None
        elif obj.type == 'CAMERA':
            record['camera'] = simple_properties(obj.data)
        result[obj.name] = record
    return result


input_path = Path(bpy.data.filepath)
input_digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
before = snapshot()
roof_records = [orient_outer_shell(obj) for obj in roofs]
light_records = []
for name in sorted(spot_names):
    light = bpy.data.objects[name].data
    assert light.type == 'SPOT'
    old = light.spot_blend
    assert old in (0, .0001) or abs(old - .0001) < 1e-8
    light.spot_blend = .0001
    light_records.append({'name': name, 'before_blend': old, 'after_blend': light.spot_blend,
                          'spot_size_radians': light.spot_size,
                          'edge_band_degrees': light.spot_size * .5 * light.spot_blend * 180 / 3.141592653589793})
bpy.context.view_layer.update()
assert before == snapshot(), 'Changed unrelated mesh/light/camera/collision/placement data'

saved_paths = []
if args.apply:
    bpy.ops.wm.save_as_mainfile(filepath=str(input_path), compress=True)
    saved_paths.append(input_path)
    if args.kind == 'source':
        for slug in ('qinfang-ting', 'ouxiang-xie', 'ziling-zhou'):
            path = ROOT / 'blender/sites' / ('SITE_' + slug + '.blend')
            bpy.data.libraries.write(str(path), {bpy.data.collections['SITE_' + slug]},
                                     fake_user=True, compress=True)
            saved_paths.append(path)

report = {'kind': args.kind, 'status': 'saved' if args.apply else 'scratch_only',
          'source_before_sha256': input_digest,
          'roofs': roof_records, 'lights': light_records,
          'unchanged_object_records_checked': len(before),
          'saved_files': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in saved_paths},
          'scope': 'Native winding and minimum hard-cone edge band. Positions, UV ownership, material assignment, transforms, camera/collision and unrelated mesh/light data preserved. Exports and fresh lighting remain required.'}
output = ROOT / 'export' / ('roof-cone-authoring-' + args.kind + '.json')
output.write_text(json.dumps(report, indent=2) + '\n')
print('ROOF_CONE_AUTHORING', report['status'], args.kind, len(roof_records),
      'roof meshes;', len(light_records), 'spots;', len(before), 'preserved records', flush=True)
