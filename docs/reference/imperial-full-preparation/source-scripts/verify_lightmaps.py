"""Check bake freshness and image contents; visual quality needs engine inspection."""
from pathlib import Path
import hashlib,json,struct,sys
import numpy as np
from PIL import Image
from lightmap_catalog import eligible_meshes, glb_document
root=Path(__file__).resolve().parents[1]
source=root/'export/garden-of-dreams.glb';digest=hashlib.sha256(source.read_bytes()).hexdigest()
demo='--demo' in sys.argv
records=list((root/'export/lightmaps').glob('*.json'))
if demo:
 records=[p for p in records if json.loads(p.read_text()).get('site') in ['terminal-cells','rockery-gate','qinfang-ting'] and json.loads(p.read_text()).get('source_glb_sha256')==digest]
elif '--current' in sys.argv:
 records=[p for p in records if json.loads(p.read_text()).get('source_glb_sha256')==digest]
assert records,'No bakes'
pixel_report=json.loads((root/'export/lightmap-pixels.json').read_text()) if (root/'export/lightmap-pixels.json').exists() else {}
for path in records:
 record=json.loads(path.read_text())
 assert record['source_glb_sha256']==digest,('stale bake',path)
 image=Image.open(path.parent/record['texture']);assert image.size==(record['size'],record['size'])
 data=np.asarray(image.convert('RGB'))
 if data.max()==0 or (data.max(axis=2)>0).mean()<=.01:
  native=pixel_report.get(record['texture'],{})
  texture_bytes=(path.parent/record['texture']).read_bytes()
  assert native.get('sha256')==hashlib.sha256(texture_bytes).hexdigest(),('Run inspect_lightmap_pixels.py for native precision',path)
  assert native['finite'] and native['max_value']>0 and native['nonzero_fraction']>.01,('empty bake at native precision',path)
 assert record['scale']>0 and record['uv_channel']==1
 print('LIGHTMAP_DATA_PASS',record['mesh'],image.size,'scale',record['scale'])

doc=glb_document(source)
expected=eligible_meshes(doc)
demo_prefixes=('SITE_terminal-cells_','SITE_rockery-gate_','SITE_qinfang-ting_','HERO_gate_','HERO_qinfang_','HERO_table_')
if demo:expected={name for name in expected if name.startswith(demo_prefixes)}
present={json.loads(p.read_text())['mesh'] for p in records}
coverage={'expected_meshes':len(expected),'baked_meshes':len(expected & present),'missing':sorted(expected-present),'unexpected':sorted(present-expected),'source_glb_sha256':digest}
(root/('export/demo-lightmaps-coverage.json' if demo else 'export/lightmaps-coverage.json')).write_text(json.dumps(coverage,indent=2)+'\n')
print('BAKE_COVERAGE',coverage['baked_meshes'],'/',coverage['expected_meshes'])
if '--require-all' in sys.argv:assert not coverage['missing'] and not coverage['unexpected'],coverage
