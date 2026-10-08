"""Keep the stage collection directly inspectable as a standalone Blender scene."""

import os
from pathlib import Path

import bpy
from mathutils import Vector


root = Path(__file__).resolve().parents[1]
path = root / "blender/sites/SITE_stage.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(path), link=False) as (source, target):
    assert path.stem in source.collections
    target.collections = [path.stem]
stage = target.collections[0]
scene = bpy.context.scene
scene.name = path.stem
scene.collection.children.link(stage)
scene.unit_settings.system = "METRIC"
camera = bpy.data.objects.new("CAM_stage_library_preview", bpy.data.cameras.new("Stage library preview"))
scene.collection.objects.link(camera)
camera.location = (0, -30, 9)
camera.rotation_euler = (Vector((0, 45, 8)) - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera
wash = next(o for o in stage.objects if o.name == "LGT_stage_backdrop_wash")
assert wash.type == "LIGHT" and wash.data.type == "AREA"
assert wash.light_linking.receiver_collection is not None
assert len(wash.light_linking.receiver_collection.objects) == 5
temporary = path.with_name(path.stem + "-packaged.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True)
os.replace(temporary, path)
print("STAGE_LIBRARY_PASS: broad backdrop Area light and five linked receivers")
