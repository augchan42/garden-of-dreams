"""Install exactly the current complete-garden bake targets; retain old source experiments."""
import hashlib
import json
import math
from pathlib import Path
import shutil
from lightmap_catalog import eligible_meshes, glb_document

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'export/garden-of-dreams.glb'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
expected = eligible_meshes(glb_document(source))
output = ROOT / 'godot/lightmaps'
records = {}
# Validate the entire catalog before changing any engine files.
for name in sorted(expected):
    path = ROOT / 'export/lightmaps' / (name + '.json')
    record = json.loads(path.read_text())
    assert record['mesh'] == name and record['source_glb_sha256'] == digest, ('Stale bake', path)
    assert record['point_lights_baked'] is False and record['uv_channel'] == 1, path
    assert math.isfinite(record['scale']) and record['scale'] > 0, path
    assert (path.parent / record['texture']).is_file(), path
    key = name.replace('.', '_')
    assert key not in records, ('Engine name collision', key)
    records[key] = {**record, 'engine_node': key}
output.mkdir(exist_ok=True)
for record in records.values():
    original = ROOT / 'export/lightmaps'
    shutil.copy2(original / record['texture'], output / record['texture'])
    shutil.copy2(original / (record['mesh'] + '.json'), output / (record['mesh'] + '.json'))
(output / 'full-index.json').write_text(json.dumps(records, indent=2) + '\n')
print('FULL_LIGHTMAP_CATALOG_PASS', len(records), digest)
