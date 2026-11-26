"""Check that visible canvas floor no longer contributes a green-dominant base."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
material = bpy.data.materials['MAT_stage_canvas']
node = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
red, green, blue, alpha = node.inputs['Base Color'].default_value
users = sorted(o.name for o in bpy.data.objects if o.type == 'MESH' and material in list(o.data.materials))
errors = []
if not red >= green >= blue:
    errors.append('The broad painted canvas floor must use a warm neutral base rather than a dominant green channel.')
if max(red, green, blue) > 1.5 * min(red, green, blue):
    errors.append('Visible canvas RGB channels must remain within a restrained neutral range.')
if not .035 <= min(red, green, blue) <= max(red, green, blue) <= .12:
    errors.append('The canvas must retain its dark non-emissive stage-floor range.')
if node.inputs['Base Color'].is_linked or node.inputs['Emission Strength'].default_value != 0:
    errors.append('The existing plain, non-emissive canvas treatment changed.')
if abs(node.inputs['Roughness'].default_value - .7) > 1e-6:
    errors.append('Canvas roughness changed.')
if material.diffuse_color[:] != node.inputs['Base Color'].default_value[:]:
    errors.append('Viewport and Principled base colors differ.')
if users != ['AOJING_ground', 'AOJING_ground.001', 'AOJING_ground.002', 'AOJING_ground.003', 'KIT_stage_painted_canvas.001']:
    errors.append('The five inspected visible canvas floor users changed.')
report = {'status': 'saved_canvas_palette_passed' if not errors else 'saved_canvas_palette_rejected',
          'source_authoring_sha256': hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
          'linear_rgb': [red, green, blue], 'roughness': node.inputs['Roughness'].default_value,
          'canvas_users': users, 'errors': errors,
          'scope': 'Actual saved visible canvas palette contract only. Black backstage, geometry/collision, matching export/bakes, native appearance and whole-site acceptance require separate preservation and review.'}
args.report.parent.mkdir(parents=True, exist_ok=True)
args.report.write_text(json.dumps(report, indent=2) + '\n')
print('SAVED_CANVAS_PALETTE_RESULT', len(errors), 'failures;', [red, green, blue], flush=True)
assert not errors, '; '.join(errors)
