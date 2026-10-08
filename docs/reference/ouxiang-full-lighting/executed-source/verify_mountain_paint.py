"""Check native painted-flat texture, emission, UV and luminance contracts."""
import hashlib
import json
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'textures/backdrops/mountain-paint'
materials = ['MAT_painted_mountains_' + str(i) for i in range(3)]
for name in materials:
    material = bpy.data.materials[name]
    bsdf = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    assert bsdf.inputs['Base Color'].is_linked, ('Missing painted mountain texture', name)
    assert bsdf.inputs['Emission Color'].is_linked, ('Original green emission retained', name)
    base = bsdf.inputs['Base Color'].links[0].from_node
    emission = bsdf.inputs['Emission Color'].links[0].from_node
    assert base == emission and base.type == 'TEX_IMAGE'
    assert tuple(base.image.size) == (4096, 4096) and base.image.packed_file
    assert base.image.colorspace_settings.name == 'sRGB'
    assert abs(bsdf.inputs['Emission Strength'].default_value - .6) < 1e-6
manifest = json.loads((folder / 'atlas.json').read_text())
digest = hashlib.sha256((folder / 'mountain-paint.png').read_bytes()).hexdigest()
assert digest == manifest['png_sha256']
before = json.loads((ROOT / 'export/mountain-source-before.json').read_text())
report = {'texture_sha256': digest, 'materials': {}, 'objects': [],
          'scope': 'Saved native paint/UV/emission source contracts; runtime and final art acceptance remain separate.'}
for i, name in enumerate(materials):
    bsdf = next(n for n in bpy.data.materials[name].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    image = bsdf.inputs['Base Color'].links[0].from_node.image
    assert hashlib.sha256(image.packed_file.data).hexdigest() == digest, 'Saved paint differs from original PNG'
    rgb = np.asarray(manifest['mean_linear_rgb'][str(i)])
    assert rgb[2] > rgb[1] > rgb[0] and rgb[1] - (rgb[0] + rgb[2]) / 2 <= .001
    old_rgb = np.asarray(before['materials'][name]['emission'][:3])
    weights = np.asarray([.2126, .7152, .0722])
    ratio = float((rgb @ weights) / (old_rgb @ weights))
    assert .9 < ratio < 1.1, ('Paint should retain existing emitted luminance', name, ratio)
    report['materials'][name] = {'mean_linear_rgb': rgb.tolist(), 'emitted_luminance_ratio': ratio}
for saved in before['objects']:
    obj = bpy.data.objects[saved['name']]
    assert list(map(list, obj.matrix_world)) == saved['matrix']
    assert len(obj.data.vertices) == saved['vertices'] and len(obj.data.polygons) == saved['polygons']
    assert len(obj.data.uv_layers) == 1
    name = obj.data.materials[0].name
    x, y, w, h = manifest['uv_regions'][name]
    uv = np.asarray([list(v.uv) for v in obj.data.uv_layers[0].data])
    assert np.isfinite(uv).all() and uv[:, 0].min() >= -1e-5 and uv[:, 0].max() <= 1.00001
    assert uv[:, 1].min() >= y - 1e-5 and uv[:, 1].max() <= y + h + 1e-5
    assert np.ptp(uv[:, 0]) > .99 and np.ptp(uv[:, 1]) > h * .99
    report['objects'].append({'name': obj.name, 'uv_layer': obj.data.uv_layers[0].name,
                              'geometry_and_transform_preserved': True})
(ROOT / 'export/mountain-paint-source-checks.json').write_text(json.dumps(report, indent=2) + '\n')
print('MOUNTAIN_PAINT_SOURCE_PASS: three textured/emissive flats; original luminance and physical geometry retained')
