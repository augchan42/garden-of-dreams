"""Keep standalone Blender sites in sync with their softer key lights."""

import os
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SITES = (
    "aojing-guan", "daguan-lou", "daoxiang-cun", "hengwu-yuan",
    "longcui-an", "xiaoxiang-guan", "yihong-yuan",
)

for slug in SITES:
    name = f"SITE_{slug}"
    collection = bpy.data.collections[name]
    path = ROOT / "blender/sites" / f"{name}.blend"
    bpy.data.libraries.write(str(path), {collection}, fake_user=True, compress=True)

for slug in SITES:
    name = f"SITE_{slug}"
    path = ROOT / "blender/sites" / f"{name}.blend"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(path), link=False) as (source, target):
        assert name in source.collections
        target.collections = [name]
    scene = bpy.context.scene
    scene.name = name
    scene.collection.children.link(target.collections[0])
    scene.unit_settings.system = "METRIC"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1410
    scene.render.resolution_y = 600
    scene.camera = next((o for o in scene.objects if o.type == "CAMERA"), None)
    if scene.camera is None:
        camera = bpy.data.objects.new("CAM_library", bpy.data.cameras.new("CAM_library"))
        scene.collection.objects.link(camera)
        camera.location = (10, -14, 9)
        camera.rotation_euler = (Vector((0, 0, 1)) - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.camera = camera
    key = bpy.data.objects[f"LGT_{slug}_key"]
    assert tuple(round(x, 2) for x in key.data.color) == (0.55, 0.74, 0.58)
    temporary = path.with_name(path.stem + "-packaged.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True)
    os.replace(temporary, path)

print("SOFTENED_SITE_LIBRARIES_PASS", len(SITES))
