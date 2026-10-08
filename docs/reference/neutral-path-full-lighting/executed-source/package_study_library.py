"""Make the updated bulletin hall collection directly openable in Blender."""

import os
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1]
path = root / "blender/sites/SITE_qiushuang-zhai.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(path), link=False) as (source, target):
    assert path.stem in source.collections
    target.collections = [path.stem]
site = target.collections[0]
scene = bpy.context.scene
scene.name = path.stem
scene.collection.children.link(site)
scene.unit_settings.system = "METRIC"
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1410
scene.render.resolution_y = 600
scene.camera = next(o for o in site.objects if o.name == "CAM_qiushuang-zhai_wide")
temporary = path.with_name(path.stem + "-packaged.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True)
os.replace(temporary, path)
assert len([o for o in site.objects if o.name.startswith("LGT_study_warm_")]) == 2
assert {o.name for o in site.objects if o.name.startswith("HERO_study_")} == {
    "HERO_study_title", "HERO_study_scroll_bamboo", "HERO_study_scroll_plum"
}
print("STUDY_LIBRARY_PASS: directly openable site with camera, lights and painted art")
