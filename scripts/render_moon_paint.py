"""Render the saved physical moon and its actual packed source material, without saving."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from moon_paint_contract import OBJECT, check

parser = argparse.ArgumentParser()
parser.add_argument('--output-directory', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
source = Path(bpy.data.filepath)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
report = check()
moon = bpy.data.objects[OBJECT]
scene = bpy.data.scenes.new('Moon paint source inspection')
scene.collection.objects.link(moon)
scene.world = bpy.data.worlds.new('Moon inspection black')
scene.world.use_nodes = True
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value = 0
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = False
scene.render.resolution_x = scene.render.resolution_y = 256
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
camera = bpy.data.objects.new('Moon inspection camera', bpy.data.cameras.new('Moon inspection camera'))
scene.collection.objects.link(camera)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 6.2
camera.location = moon.matrix_world.translation + Vector((0, -8, 0))
camera.rotation_euler = (moon.matrix_world.translation - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera
bpy.context.window.scene = scene
args.output_directory.mkdir(parents=True, exist_ok=True)
png = args.output_directory / 'cycles-source-emission.png'
scene.render.filepath = str(png)
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
report.update(status='rendered', source_blend_sha256=source_hash,
              image_sha256=hashlib.sha256(png.read_bytes()).hexdigest(),
              scope='Isolated actual saved moon mesh/material, no key or ambient illumination, Cycles 128 samples, Standard sRGB view. Not full garden lighting or final scene art acceptance.')
(args.output_directory / 'cycles-source-report.json').write_text(json.dumps(report, indent=2) + '\n')
print('MOON_SOURCE_RENDER_PASS', report['image_sha256'])
