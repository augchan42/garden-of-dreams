"""Export saved bamboo-court camera subjects without modifying Blender files.

Run Blender --background authoring.blend --python this_file --
--root PROJECT --test-output FILE --runtime-output FILE.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--test-output", required=True)
parser.add_argument("--runtime-output", required=True)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
root = Path(args.root)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
authoring = root / "blender/authoring.blend"
assert Path(bpy.data.filepath).resolve() == authoring.resolve()
frozen = sha(authoring)
scene = next(s for s in bpy.data.scenes if s.name.startswith("Garden of Dreams"))
bpy.context.window.scene = scene
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
subjects = {}
for obj in scene.objects:
    if obj.type != "MESH" or not obj.name.startswith(("XIAOXIANG_", "HERO_flora_xiaoxiang_")):
        continue
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    subjects[obj.name] = {"points": [[p.x, p.z, -p.y] for p in points],
                          "materials": [material.name for material in obj.data.materials]}
    evaluated.to_mesh_clear()
source = sha(root / "export/garden-of-dreams.glb")
test = {"authoring_sha256": frozen, "source_glb_sha256": source, "subjects": subjects}
runtime = {"source_glb_sha256": source, "subjects": {}}
for action, names in {"doors": ["XIAOXIANG_gate_leaf", "XIAOXIANG_gate_leaf.001", "XIAOXIANG_threshold"],
                      "stems": ["HERO_flora_xiaoxiang_guan_1", "XIAOXIANG_amber_window"]}.items():
    points = {tuple(point) for name in names for point in subjects[name]["points"]}
    runtime["subjects"][action] = [list(point) for point in sorted(points)]
assert len(runtime["subjects"]["doors"]) == 24 and len(runtime["subjects"]["stems"]) == 968
assert sha(authoring) == frozen
Path(args.test_output).write_text(json.dumps(test, indent=2) + "\n")
Path(args.runtime_output).write_text(json.dumps(runtime, separators=(",", ":")) + "\n")
print("XIAOXIANG_CAMERA_SUBJECTS_EXPORTED", len(subjects), source)
