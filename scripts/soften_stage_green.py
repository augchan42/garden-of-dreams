"""Reduce the broad green wash while retaining green CRT and foliage accents."""

import bpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_COLOR = (0.55, 0.74, 0.58)

for obj in bpy.data.objects:
    if obj.type != "LIGHT":
        continue
    if obj.name == "LGT_stage_green_key" or (
        obj.name.startswith("LGT_") and obj.name.endswith("_key")
        and obj.name != "LGT_qiushuang-zhai_key"
        and obj.name != "LGT_tubi-tang_key"
    ):
        obj.data.color = KEY_COLOR

base_colors = {
    "MAT_cyclorama": (0.035, 0.045, 0.045),
    "MAT_painted_moon": (0.62, 0.58, 0.38),
    "MAT_painted_mountains_0": (0.038, 0.05, 0.043),
    "MAT_painted_mountains_1": (0.05, 0.069, 0.055),
    "MAT_painted_mountains_2": (0.064, 0.088, 0.07),
}
for name, rgb in base_colors.items():
    material = bpy.data.materials[name]
    material.diffuse_color = (*rgb, 1)
    if material.use_nodes:
        node = material.node_tree.nodes.get("Principled BSDF")
        if node:
            node.inputs["Base Color"].default_value = (*rgb, 1)

bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender/authoring.blend"), compress=True)
print("SOFTEN_STAGE_GREEN_PASS")
