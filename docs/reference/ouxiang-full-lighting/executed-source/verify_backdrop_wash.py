"""Check the Blender wash link and a low-resolution Cycles light response."""

import bpy
import numpy as np
from mathutils import Vector
from pathlib import Path


scene = next(s for s in bpy.data.scenes if s.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
wash = bpy.data.objects["LGT_stage_backdrop_wash"]
receivers = wash.light_linking.receiver_collection
assert wash.data.type == "AREA" and receivers is not None
assert len(receivers.objects) == 5
assert all(o.name.startswith(("KIT_stage_cyclorama", "KIT_stage_painted_mountain_layer", "KIT_stage_painted_moon")) for o in receivers.objects)

camera_data = bpy.data.cameras.new("Backdrop wash check")
camera = bpy.data.objects.new("CAM_backdrop_wash_check", camera_data)
scene.collection.objects.link(camera)
camera.location = (0, 0, 9)
camera.rotation_euler = (Vector((0, 47, 7)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.lens = 32
scene.camera = camera
scene.render.engine = "CYCLES"
scene.cycles.samples = 8
scene.render.resolution_x = 320
scene.render.resolution_y = 180
scene.render.resolution_percentage = 100

def render_rgb(label):
    scene.render.filepath = str(Path("/private/tmp") / f"garden-backdrop-{label}.png")
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(scene.render.filepath, check_existing=False)
    pixels = np.empty(320 * 180 * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    bpy.data.images.remove(image)
    return pixels.reshape(180, 320, 4)[:, :, :3].copy()

wash.hide_render = True
dark = render_rgb("dark")
wash.hide_render = False
lit = render_rgb("lit")
change = float(np.abs(lit - dark).mean())
assert change > 0.003, f"Linked backdrop wash made no visible difference: {change}"
print(f"BLENDER_BACKDROP_WASH_PASS: five receivers, mean RGB change {change:.4f}")
