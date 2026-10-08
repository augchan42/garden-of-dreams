"""Give the bulletin hall a warm local key and light its existing lanterns."""

import bpy
from pathlib import Path
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
scene = next(s for s in bpy.data.scenes if s.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
site = bpy.data.collections["SITE_qiushuang-zhai"]

key = next(o for o in site.objects if o.name == "LGT_qiushuang-zhai_key")
assert key.type == "LIGHT" and key.data.type == "SPOT"
key.data.color = (0.9, 0.72, 0.45)
key.location = (22, 12, 2.6)
key.rotation_euler = (Vector((22, 15.4, 1.4)) - key.location).to_track_quat("-Z", "Y").to_euler()

for name in ("LGT_study_warm_left", "LGT_study_warm_right"):
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

for side, x in (("left", 18.13), ("right", 25.87)):
    lamp = bpy.data.lights.new(f"LGT_study_warm_{side}", "POINT")
    lamp.color = (1.0, 0.42, 0.12)
    lamp.energy = 65
    lamp.shadow_soft_size = 0.1
    obj = bpy.data.objects.new(lamp.name, lamp)
    site.objects.link(obj)
    obj.location = (x, 15.3, 2.2)

assert len([o for o in site.objects if o.name.startswith("LGT_study_warm_")]) == 2
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender/authoring.blend"), compress=True)
bpy.data.libraries.write(
    str(ROOT / "blender/sites/SITE_qiushuang-zhai.blend"),
    {site},
    fake_user=True,
    compress=True,
)
print("STUDY_LIGHT_PASS: warm key and two lantern lights saved")
