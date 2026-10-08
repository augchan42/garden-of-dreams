"""Save the imperial facade collection as a directly openable Blender scene."""

import os
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "blender/sites/SITE_daguan-lou.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(path), link=False) as (source, target):
    target.collections = [path.stem]
site = target.collections[0]
scene = bpy.context.scene
scene.name = path.stem
scene.collection.children.link(site)
scene.unit_settings.system = "METRIC"
scene.camera = next(obj for obj in site.objects if obj.name == "CAM_daguan-lou_wide")
assert any(obj.name == "HERO_daguan_title" for obj in site.objects)
assert sum(obj.name.startswith("DAGUAN_closed_door") for obj in site.objects) == 10
temporary = path.with_name(path.stem + "-packaged.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(temporary), compress=True)
os.replace(temporary, path)
print("IMPERIAL_LIBRARY_PASS: painted title and lacquer facade preserved")
