"""Read and verify saved bamboo topology and kit/source/library parity.

Run Blender --background --python this_file -- --root PROJECT --output REPORT.
No scenes or exports are saved by this verifier.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
root = Path(args.root).resolve()
output = Path(args.output).resolve()
sys.path.insert(0, str(root / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bamboo_source_contract import inspect
from moon_paint_contract import fingerprint

variants = ["bamboo_small", "bamboo_medium", "bamboo_large"]
files = [root / "blender/kits/KIT_flora.blend", root / "blender/authoring.blend",
         root / "blender/sites/SITE_xiaoxiang-guan.blend",
         root / "blender/sites/SITE_qinfang-ting.blend", root / "blender/master.blend"]
assert output not in files and output.suffix == ".json"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
frozen = {p: sha(p) for p in files}
kit = {}
rows = []
for path in files:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    if path.name == "KIT_flora.blend":
        for variant in variants:
            counts = []
            for suffix in ["", "_LOD1"]:
                mesh = bpy.data.meshes["KIT_flora_" + variant + "_render" + suffix]
                row = inspect(mesh, variant)
                kit[variant, suffix] = fingerprint(mesh)
                counts.append(row["triangles"])
                rows.append({**row, "file":str(path.relative_to(root)), "mesh":mesh.name})
            assert counts[0] <= 2000 and .32 <= counts[1] / counts[0] <= .48
    else:
        objects = list(bpy.context.scene.objects) if path.name in ["authoring.blend", "master.blend"] else list(bpy.data.objects)
        plants = [o for o in objects if o.get("flora_variant") in variants]
        expected = 4 if path.stem == "SITE_xiaoxiang-guan" else 3 if path.stem == "SITE_qinfang-ting" else 7
        assert len(plants) == expected, (path, len(plants), expected)
        for obj in plants:
            variant = obj["flora_variant"]
            row = inspect(obj.data, variant)
            assert fingerprint(obj.data) == kit[variant, ""], (path, obj.name)
            rows.append({**row, "file":str(path.relative_to(root)), "object":obj.name})
assert len(rows) == 27
assert all(sha(p) == digest for p, digest in frozen.items())
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({"status":"saved_bamboo_contract_passed", "rows":rows,
    "source_files_sha256":{str(p.relative_to(root)):h for p,h in frozen.items()},
    "scope":"Saved opaque-culm connectivity, collar count, height, UVs, finite coordinates, LOD budget and source/kit/library parity. No visual, phone or final art acceptance."}, indent=2) + "\n")
print("SAVED_BAMBOO_CONTRACT_PASS 27 saved meshes")
