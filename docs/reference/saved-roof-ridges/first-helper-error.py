"""Inspect cap face winding in the saved authoring scene without saving it."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pavilion_roof_geometry import components

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=ROOT / 'blender/authoring.blend')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
source_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(args.source))
scene = bpy.context.scene
roofs = {}
for obj in scene.objects:
    if obj.type != 'MESH' or 'roof' not in obj.name.lower():
        continue
    caps = []
    for vertices, faces in components(obj.data):
        if len(vertices) == 15 and len(faces) == 8:
            values = [float(obj.data.polygons[index].normal.z) for index in faces]
            caps.append({'faces': len(values), 'positive_local_z': sum(v > 0 for v in values),
                         'negative_local_z': sum(v < 0 for v in values),
                         'minimum_local_normal_z': min(values), 'maximum_local_normal_z': max(values)})
    if caps:
        roofs[obj.name] = {'components': len(caps), 'faces': sum(c['faces'] for c in caps),
                           'positive_local_z': sum(c['positive_local_z'] for c in caps),
                           'negative_local_z': sum(c['negative_local_z'] for c in caps)}
assert roofs['QINFANG_kit_roof_hex']['components'] == 42
assert roofs['QINFANG_kit_roof_hex']['negative_local_z'] == 0
assert hashlib.sha256(args.source.read_bytes()).hexdigest() == source_hash
report = {'status': 'saved_cap_winding_inspected', 'authoring_sha256': source_hash,
          'scope': 'Scene objects with roof in their name and disconnected 15-vertex/8-face components matching the diagnosed tile-strip topology. Local-space face normal signs only; not a complete roof inventory, world-space visibility, material/culling behavior, UV sampling or final rendered lighting diagnosis. No source save.',
          'roofs': roofs}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2) + '\n')
print('SAVED_ROOF_RIDGES_INSPECTED', len(roofs))
for name, row in roofs.items():
    print(name, row['components'], 'caps', row['negative_local_z'], '/', row['faces'], 'negative local Z faces')
