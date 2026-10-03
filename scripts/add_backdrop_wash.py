"""Author a broad cyclorama-only wash in the editable Blender stage."""

from pathlib import Path

import bpy
from mathutils import Vector


root = Path(__file__).resolve().parents[1]
scene = next(s for s in bpy.data.scenes if s.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
stage = bpy.data.collections["SITE_stage"]
backdrop = [
    obj for obj in stage.objects
    if obj.name.startswith((
        "KIT_stage_cyclorama",
        "KIT_stage_painted_mountain_layer",
        "KIT_stage_painted_moon",
    ))
]
assert len(backdrop) == 5, "Expected cyclorama, three mountain layers and moon"

for old in list(bpy.data.objects):
    if old.name.startswith("LGT_stage_backdrop_wash"):
        bpy.data.objects.remove(old, do_unlink=True)
for old_data in list(bpy.data.lights):
    if old_data.name.startswith("LGT_stage_backdrop_wash") and old_data.users == 0:
        bpy.data.lights.remove(old_data)
old_collection = bpy.data.collections.get("LINK_stage_backdrop_receivers")
if old_collection:
    bpy.data.collections.remove(old_collection)

receivers = bpy.data.collections.new("LINK_stage_backdrop_receivers")
for obj in backdrop:
    receivers.objects.link(obj)

data = bpy.data.lights.new("LGT_stage_backdrop_wash", "AREA")
data.shape = "RECTANGLE"
data.size = 70.0
data.size_y = 25.0
data.energy = 1800.0
data.color = (0.72, 0.78, 0.84)
light = bpy.data.objects.new(data.name, data)
stage.objects.link(light)
light.location = (0.0, 12.0, 16.0)
light.rotation_euler = (Vector((0.0, 47.0, 7.0)) - light.location).to_track_quat("-Z", "Y").to_euler()
light.light_linking.receiver_collection = receivers
assert set(receivers.objects) == set(backdrop)

bpy.ops.wm.save_as_mainfile(filepath=str(root / "blender/authoring.blend"), compress=True)
bpy.data.libraries.write(str(root / "blender/sites/SITE_stage.blend"), {stage}, fake_user=True, compress=True)
print("BACKDROP_WASH_PASS: authored area light linked to five backdrop meshes")
