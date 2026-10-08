"""Native imported-geometry shadow pixels and explicit-intent preservation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gltf_shadow_contract import apply_shadow_intent

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--output-root', type=Path, required=True)
parser.add_argument('--inspect-only', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
source = args.source.resolve()
output = args.output_root.resolve()
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
scene = bpy.context.scene
before = {o.name: o.visible_shadow for o in scene.objects if o.type == 'MESH'}
contract = apply_shadow_intent(source, scene)
after = {o.name: o.visible_shadow for o in scene.objects if o.type == 'MESH'}
assert all(after[n] == contract['explicit_meshes'].get(n, value) for n, value in before.items())
report = {'source_glb_sha256': contract['source_glb_sha256'], 'contract': contract,
          'helper_sha256': hashlib.sha256((Path(__file__).parent / 'gltf_shadow_contract.py').read_bytes()).hexdigest(),
          'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'scope': 'Actual native imported GLB mesh ray visibility. Unflagged mesh preservation and, unless inspect-only, isolated scaled canopy shadow pixels. Not full-garden GI/fresh lighting or final paint.'}
if not args.inspect_only:
    canopy = scene.objects['SITE_stage_MAT_stage_canopy_paint']
    assert contract['explicit_meshes'] == {canopy.name: False}
    for obj in list(scene.objects):
        if obj != canopy:
            bpy.data.objects.remove(obj, do_unlink=True)
    canopy.scale *= .1
    dark = bpy.data.materials.new('Diagnostic black caster')
    dark.use_nodes = True
    bsdf = dark.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
    canopy.data.materials.clear()
    canopy.data.materials.append(dark)
    for polygon in canopy.data.polygons:
        polygon.material_index = 0
    bpy.ops.mesh.primitive_plane_add(size=8)
    floor = bpy.context.object
    matte = bpy.data.materials.new('Diagnostic white floor')
    matte.use_nodes = True
    bsdf = matte.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (1, 1, 1, 1)
    bsdf.inputs['Roughness'].default_value = 1
    floor.data.materials.append(matte)
    light = bpy.data.lights.new('Diagnostic lamp', 'SPOT')
    light.energy = 1500
    light.spot_size = 1.5707963267948966
    lamp = bpy.data.objects.new(light.name, light)
    scene.collection.objects.link(lamp)
    lamp.location = (0, 0, 7)
    data = bpy.data.cameras.new('Diagnostic camera')
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    camera.location = (0, -8, 1.5)
    camera.rotation_euler = (-camera.location).to_track_quat('-Z', 'Y').to_euler()
    data.type = 'ORTHO'
    data.ortho_scale = 5
    scene.camera = camera
    world = bpy.data.worlds.new('Diagnostic black world')
    world.use_nodes = True
    world.node_tree.nodes.get('Background').inputs['Strength'].default_value = 0
    scene.world = world
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 320
    scene.render.resolution_y = 240
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Standard'
    samples = {}
    for name, value in [('imported-before-contract', before[canopy.name]),
                        ('after-contract', after[canopy.name]),
                        ('forced-shadow-on', True), ('forced-shadow-off', False)]:
        canopy.visible_shadow = value
        path = output / (name + '.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        # Render Result pixels are unavailable in some background workflows;
        # reload the actual saved PNG and convert its sRGB values to linear.
        image = bpy.data.images.load(str(path), check_existing=False)
        pixels = np.empty(320 * 240 * 4, dtype=np.float32)
        image.pixels.foreach_get(pixels)
        pixels = pixels.reshape(240, 320, 4)
        rgb = pixels[117:124, 157:164, :3]
        luminance = float(np.mean(rgb @ np.array([.2126, .7152, .0722])))
        samples[name] = {'visible_shadow': value, 'floor_linear_luminance': luminance,
                         'image_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        bpy.data.images.remove(image)
    assert samples['after-contract']['floor_linear_luminance'] > samples['forced-shadow-on']['floor_linear_luminance'] + .2
    assert abs(samples['after-contract']['floor_linear_luminance'] - samples['forced-shadow-off']['floor_linear_luminance']) < .001
    assert samples['imported-before-contract']['visible_shadow'] is True
    report['samples'] = samples
report['status'] = 'passed'
(output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print('NATIVE_GLTF_SHADOW_TRANSFER_PASS', json.dumps(report), flush=True)
