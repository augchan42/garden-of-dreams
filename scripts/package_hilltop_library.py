"""Make the edited hilltop site collection directly openable in Blender."""

import os
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1]
path = root / "blender/sites/SITE_tubi-tang.blend"
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
scene.camera = next(o for o in site.objects if o.name == "CAM_tubi-tang_wide")
assert any(o.name == "HERO_tubi_title" for o in site.objects)
assert any(o.name == "TUBI_terrace" and o.data.materials[0].name == "MAT_tubi_terrace_plaster" for o in site.objects)
temporary = path.with_name(path.stem + "-packaged.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True)
os.replace(temporary, path)
print("HILLTOP_LIBRARY_PASS: camera, painted title and warm plaster saved")
