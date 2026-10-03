"""Copy current opaque site bakes for all three priority-2 hall previews."""

import hashlib
import json
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "export/garden-of-dreams.glb"
DIGEST = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
SITES = ("qiushuang-zhai", "tubi-tang", "daguan-lou")
OUTPUT = ROOT / "godot/lightmaps"


def glb_document(path: Path) -> dict:
    blob = path.read_bytes()
    size = struct.unpack_from("<I", blob, 12)[0]
    return json.loads(blob[20:20 + size])


records = {}
expected = set()
for slug in SITES:
    document = glb_document(ROOT / f"export/sites/SITE_{slug}.glb")
    for node in document["nodes"]:
        if "mesh" not in node or node.get("name", "").startswith("COL_"):
            continue
        mesh = document["meshes"][node["mesh"]]
        materials = [document["materials"][item["material"]] for item in mesh["primitives"]]
        if any(material.get("alphaMode", "OPAQUE") != "OPAQUE" for material in materials):
            continue  # Keep painted sign alpha on its source material.
        if any(material["name"] in ("MAT_water", "MAT_aojing_water", "MAT_fog_plane") for material in materials):
            continue
        expected.add(node["name"])

for path in (ROOT / "export/lightmaps").glob("*.json"):
    record = json.loads(path.read_text())
    if record.get("site") not in SITES or record["mesh"] not in expected:
        continue
    assert record["source_glb_sha256"] == DIGEST, ("Stale lightmap", path)
    assert record["point_lights_baked"] is False
    image = path.parent / record["texture"]
    assert image.is_file(), image
    shutil.copy2(path, OUTPUT / path.name)
    shutil.copy2(image, OUTPUT / image.name)
    key = record["mesh"].replace(".", "_")
    assert key not in records, key
    records[key] = {**record, "engine_node": key}

present = {record["mesh"] for record in records.values()}
assert present == expected, {"missing": sorted(expected - present), "unexpected": sorted(present - expected)}
(OUTPUT / "priority2-index.json").write_text(json.dumps(records, indent=2) + "\n")
print("PRIORITY2_LIGHTMAPS_PASS", len(records), DIGEST)
