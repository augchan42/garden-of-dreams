"""Add small perimeter seats to the hilltop overlook without narrowing the route."""

import ast
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
scene = next(scene for scene in bpy.data.scenes if scene.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
C = bpy.data.collections["SITE_tubi-tang"]
wood = bpy.data.materials["MAT_lattice_wood"]

tree = ast.parse((ROOT / "scripts/build_garden.py").read_text())
exec(compile(ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)], type_ignores=[]), "helpers", "exec"))

for obj in list(C.objects):
    if obj.name.startswith(("TUBI_view_bench_", "COL_tubi_view_bench_")):
        bpy.data.objects.remove(obj, do_unlink=True)

for side, x, inner in (("left", 3.04, 1), ("right", 10.96, -1)):
    y = 33.25
    # Seat top is 0.46 m above the terrace. The slatted back faces the aisle.
    box(f"TUBI_view_bench_{side}_seat", (x, y, 4.40), (0.52, 2.15, 0.12), wood)
    box(f"TUBI_view_bench_{side}_back", (x - inner * 0.19, y, 4.72), (0.10, 2.15, 0.59), wood)
    for end, leg_y in enumerate((32.3, 34.2)):
        box(f"TUBI_view_bench_{side}_leg_{end}", (x, leg_y, 4.19), (0.14, 0.14, 0.38), wood)
    collision(f"tubi_view_bench_{side}", (x, y, 4.40), (0.54, 2.25, 0.82))

assert sum(obj.name.startswith("TUBI_view_bench_") for obj in C.objects) == 8
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender/authoring.blend"), compress=True)
bpy.data.libraries.write(str(ROOT / "blender/sites/SITE_tubi-tang.blend"), {C}, fake_user=True, compress=True)
print("HILLTOP_VIEW_BENCHES_PASS: two perimeter benches, clear central aisle")
