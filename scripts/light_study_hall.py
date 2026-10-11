"""Light the study frontage with one diagonal key and two amber practicals."""

import bpy
from math import radians
from pathlib import Path
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
scene = next(s for s in bpy.data.scenes if s.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
site = bpy.data.collections["SITE_qiushuang-zhai"]

key = next(o for o in site.objects if o.name == "LGT_qiushuang-zhai_key")
assert key.type == "LIGHT" and key.data.type == "SPOT"
practicals = {}
for side in ("left", "right"):
    stem = f"LGT_study_warm_{side}"
    matches = [o for o in site.objects
               if o.name == stem or o.name.startswith(stem + ".")]
    assert len(matches) <= 1, f"Duplicate {side} study practicals"
    if matches:
        assert matches[0].type == "LIGHT" and matches[0].data.type == "POINT"
        practicals[side] = matches[0]

# Moving the source back covers all three banks without a bright circle on
# the centre wall. The zero source radius retains the specified hard shadows.
key.data.color = (0.9, 0.82, 0.68)
key.data.energy = 1200
key.data.spot_size = radians(60)
key.data.spot_blend = 0.15
key.data.shadow_soft_size = 0
key.data.use_shadow = True
key.location = (26.5, 6, 3.6)
key.rotation_euler = (Vector((22, 15.94, 1.6)) - key.location).to_track_quat("-Z", "Y").to_euler()

for side, x in (("left", 18.13), ("right", 25.87)):
    obj = practicals.get(side)
    if obj is None:
        lamp = bpy.data.lights.new(f"LGT_study_warm_{side}", "POINT")
        obj = bpy.data.objects.new(lamp.name, lamp)
        site.objects.link(obj)
    lamp = obj.data
    lamp.color = (1.0, 0.42, 0.12)
    lamp.energy = 65
    lamp.shadow_soft_size = 0.1
    obj.location = (x, 15.3, 2.2)

assert len([o for o in site.objects if o.name.startswith("LGT_study_warm_")]) == 2
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender/authoring.blend"), compress=True)
bpy.data.libraries.write(
    str(ROOT / "blender/sites/SITE_qiushuang-zhai.blend"),
    {site},
    fake_user=True,
    compress=True,
)
print("STUDY_LIGHT_PASS: diagonal warm-neutral key and two lantern lights saved")
