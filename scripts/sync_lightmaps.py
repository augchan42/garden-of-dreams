"""Copy only fresh Cycles bakes into the Godot test adapter's index."""
from pathlib import Path
import hashlib,json,shutil,sys
root=Path(__file__).resolve().parents[1]
digest=hashlib.sha256((root/'export/garden-of-dreams.glb').read_bytes()).hexdigest()
destination=root/'godot/lightmaps';destination.mkdir(exist_ok=True)
records={}
demo='--demo' in sys.argv
for path in (root/'export/lightmaps').glob('*.json'):
 record=json.loads(path.read_text())
 if demo and (record.get('site') not in ['terminal-cells','rockery-gate','qinfang-ting'] or record.get('source_glb_sha256')!=digest):continue
 assert record['source_glb_sha256']==digest,('stale bake',path)
 texture=path.parent/record['texture'];assert texture.exists()
 shutil.copy2(texture,destination/texture.name)
 shutil.copy2(path,destination/path.name)
 engine_name=record['mesh'].replace('.','_')
 assert engine_name not in records,('engine name collision',engine_name)
 record['engine_node']=engine_name
 records[engine_name]=record
(destination/('demo-index.json' if demo else 'index.json')).write_text(json.dumps(records,indent=2)+'\n')
if demo:
 (root/'godot/assets/garden-source.json').write_text(json.dumps({'source_glb_sha256':digest},indent=2)+'\n')
print('Synced',len(records),'fresh lightmaps')
