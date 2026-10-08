"""Save reviewed plain-material colors to an isolated Blender source candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from garden_material_palette import COMMON_BASE_COLORS, PREVIOUS_BASE_COLORS

parser = argparse.ArgumentParser()
parser.add_argument('--output-root', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
root = args.output_root.resolve()
production = Path('/Users/auchan/projects/garden-of-dreams')
assert root != production and production not in root.parents, 'Separate source candidate required'
source = Path(bpy.data.filepath).resolve()
assert source != root/'blender/authoring.blend', 'Do not overwrite the input source'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
report = {'status': 'saved_neutral_material_candidate_export_pending',
          'input_authoring_sha256': digest, 'materials': {},
          'scope': 'Four plain shared colors only; source geometry, textures, roughness, lighting, emissive practicals and all other materials retained. Complete fresh source lighting required before adoption.'}
for name, color in COMMON_BASE_COLORS.items():
    material = bpy.data.materials[name]
    node = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    assert not node.inputs['Base Color'].is_linked and node.inputs['Emission Strength'].default_value == 0
    old = list(node.inputs['Base Color'].default_value)
    assert all(abs(a-b) < 1e-6 for a,b in zip(old[:3], PREVIOUS_BASE_COLORS[name])), name
    material.diffuse_color = (*color, 1)
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Emission Color'].default_value = (*color, 1)
    report['materials'][name] = {'old_linear_rgba': old, 'new_linear_rgb': list(color),
                               'roughness': node.inputs['Roughness'].default_value,
                               'emission_strength': 0}
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
(root/'blender/sites').mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/authoring.blend'), compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
report['candidate_authoring_sha256'] = hashlib.sha256((root/'blender/authoring.blend').read_bytes()).hexdigest()
(root/'material-palette-application.json').write_text(json.dumps(report, indent=2)+'\n')
sys.argv = ['export_garden.py', '--', '--output-root', str(root)]
runpy.run_path(str(Path(__file__).resolve().parent/'export_garden.py'), run_name='__main__')
report['candidate_glb_sha256'] = hashlib.sha256((root/'export/garden-of-dreams.glb').read_bytes()).hexdigest()
report['status'] = 'saved_neutral_material_candidate_exported_not_adopted'
(root/'material-palette-application.json').write_text(json.dumps(report, indent=2)+'\n')
print('GARDEN_NEUTRAL_MATERIAL_SOURCE_PASS', report['candidate_glb_sha256'])
