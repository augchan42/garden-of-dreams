"""Change only the inspected visible canvas base color in a separate source."""
from pathlib import Path
import copy
import hashlib
import json
import runpy
import sys
import bpy

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette'
root = work / 'candidate'
source = repo / 'blender/authoring.blend'
expected = '2b07ce48ffa3011f9a2da01535a3fc84171bdc00b2ced2abad0ce8f338fd49ed'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert Path(bpy.data.filepath) == source and sha(source) == expected
assert not root.exists()
assert json.loads((work / 'canvas-red.json').read_text())['status'] == 'saved_canvas_palette_rejected'
sys.path.insert(0, str(repo / 'scripts'))
from moon_paint_contract import snapshot, check

scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
bpy.context.view_layer.update()
before = snapshot()
moon = check()
material = bpy.data.materials['MAT_stage_canvas']
node = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
old = list(node.inputs['Base Color'].default_value)
assert all(abs(a - b) < 1e-6 for a, b in zip(old, [.055, .095, .037, 1]))
assert not node.inputs['Base Color'].is_linked
assert node.inputs['Emission Strength'].default_value == 0
new = [.065, .060, .055, 1]
material.diffuse_color = new
node.inputs['Base Color'].default_value = new
bpy.context.view_layer.update()
after = snapshot()
assert before['objects'] == after['objects'], 'Geometry, transform, cameras, lights or markers changed'
assert before['materials'].keys() == after['materials'].keys()
for name in before['materials']:
    if name != material.name:
        assert before['materials'][name] == after['materials'][name], name
# Normalize the two intended color fields and compare every other target setting.
normalized = copy.deepcopy(after['materials'][material.name])
normalized['settings']['diffuse_color'] = before['materials'][material.name]['settings']['diffuse_color']
for index, row in enumerate(normalized['nodes']):
    if row[0] != 'BSDF_PRINCIPLED':
        continue
    for socket_index, socket in enumerate(row[2]):
        if socket[0] == 'Base Color':
            row[2][socket_index] = before['materials'][material.name]['nodes'][index][2][socket_index]
assert normalized == before['materials'][material.name], 'Other canvas settings changed'
assert check() == moon
(root / 'blender').mkdir(parents=True)
bpy.ops.wm.save_as_mainfile(filepath=str(root / 'blender/authoring.blend'), compress=True)
assert sha(source) == expected
report = {'status': 'separate_saved_canvas_palette_candidate_export_pending',
          'baseline_authoring_sha256': expected,
          'candidate_authoring_sha256': sha(root / 'blender/authoring.blend'),
          'material': material.name, 'old_linear_rgba': old, 'new_linear_rgba': new,
          'preserved_objects': len(before['objects']),
          'other_materials_preserved': len(before['materials']) - 1,
          'only_base_color_and_viewport_color_changed': True,
          'moon_preserved': moon,
          'scope': 'Warm gray base for the five inspected visible canvas floor users. All geometry, roughness, textures, black backstage, lights/cameras/COL/markers and runtime retained. No native appearance or fresh-bake acceptance yet.'}
(root / 'source-preservation.json').write_text(json.dumps(report, indent=2) + '\n')
sys.argv = ['export_garden.py', '--', '--output-root', str(root)]
runpy.run_path(str(repo / 'scripts/export_garden.py'), run_name='__main__')
report.update(status='separate_saved_canvas_palette_exported_not_adopted',
              candidate_glb_sha256=sha(root / 'export/garden-of-dreams.glb'))
(root / 'source-preservation.json').write_text(json.dumps(report, indent=2) + '\n')
print('SAVED_CANVAS_PALETTE_CANDIDATE_EXPORTED', report['candidate_glb_sha256'], flush=True)
