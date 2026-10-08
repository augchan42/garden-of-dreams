"""Record exported flora node identities for the Godot LOD manager."""
import json,struct,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1]
blob=(R/'export/garden-of-dreams.glb').read_bytes();size=struct.unpack_from('<I',blob,12)[0];doc=json.loads(blob[20:20+size]);records={}
for n in doc['nodes']:
 if not n.get('extras',{}).get('flora_placement'):continue
 assert n['name'].startswith('HERO_flora_')
 records[n['name'].replace('.','_')]={'variant':n['extras']['flora_variant'],'lod_distance':n['extras']['lod_distance']}
placements=json.loads((R/'export/flora-placements.json').read_text());assert len(records)==placements['count']
(R/'godot/assets/flora-placements.json').write_text(json.dumps(records,indent=2)+'\n')
shutil.copyfile(R/'export/garden-of-dreams.glb',R/'godot/assets/garden-of-dreams.glb')
print('FLORA_RUNTIME_CATALOG_PASS',len(records))
