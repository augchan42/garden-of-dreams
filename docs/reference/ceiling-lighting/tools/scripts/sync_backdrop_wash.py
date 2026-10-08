"""Validate the complete native Area-light bake before installing any files."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
from lightmap_catalog import glb_document
from wash_receiver_contract import validate_manifest_receivers

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--source',type=Path,default=ROOT/'export/lightmaps/backdrop-wash')
options=parser.parse_args()
source=options.source
manifest=json.loads((source/'manifest.json').read_text())
glb_hash=hashlib.sha256((ROOT/'export/garden-of-dreams.glb').read_bytes()).hexdigest()
stage_hash=hashlib.sha256((ROOT/'blender/sites/SITE_stage.blend').read_bytes()).hexdigest()
assert manifest['source_glb_sha256']==glb_hash and manifest['stage_blend_sha256']==stage_hash, 'Stale wash source'
assert manifest['lighting']['type']=='AREA' and manifest['building_control_max']<=1e-7
assert manifest['authoring_blend_sha256']==hashlib.sha256((ROOT/'blender/authoring.blend').read_bytes()).hexdigest(), 'Stale authoring rig'
assert len(manifest['lighting']['lights'])==12 and len(manifest['site_blend_sha256'])==12
for slug,digest in manifest['site_blend_sha256'].items():
    assert hashlib.sha256((ROOT/'blender/sites'/('SITE_'+slug+'.blend')).read_bytes()).hexdigest()==digest, ('Stale site wash',slug)
expected=validate_manifest_receivers(manifest, glb_document(ROOT/'export/garden-of-dreams.glb'))
records={}
for name in sorted(expected):
    record=json.loads((source/(name+'.json')).read_text())
    assert record==manifest['records'][name]
    assert record['source_glb_sha256']==glb_hash and record['stage_blend_sha256']==stage_hash
    assert record['backface_uv_mapping_verified'] is True
    assert record['authoring_blend_sha256']==manifest['authoring_blend_sha256']
    assert record['site_blend_sha256']==manifest['site_blend_sha256'] and record['lights_baked']==12
    assert record['uv_channel']==1 and record['point_lights_baked'] is False and record['pass_filter']==['DIRECT']
    assert math.isfinite(record['scale']) and record['scale']>0
    assert set(record['sides'])==({'front','back'} if record['double_sided'] else {'front'})
    assert max(s['linear_max'] for s in record['sides'].values())>1e-5 or record['unoccluded_control_max']>1e-5
    for side in record['sides'].values():
        assert math.isfinite(side['scale']) and side['scale']>0
        assert hashlib.sha256((source/side['texture']).read_bytes()).hexdigest()==side['png_sha256']
    key=name.replace('.','_');assert key not in records
    sides={name:{**side,'texture':'backdrop-wash/'+side['texture']} for name,side in record['sides'].items()}
    records[key]={**record,'sides':sides,'texture':sides['front']['texture'],'engine_node':key}
output=ROOT/'godot/lightmaps/backdrop-wash'
output.mkdir(parents=True,exist_ok=True)
for record in records.values():
    name=record['mesh']
    for side in record['sides'].values():
        filename=Path(side['texture']).name
        shutil.copy2(source/filename,output/filename)
    shutil.copy2(source/(name+'.json'),output/(name+'.json'))
shutil.copy2(source/'manifest.json',output/'manifest.json')
(output.parent/'backdrop-wash-index.json').write_text(json.dumps(records,indent=2)+'\n')
print('BACKDROP_WASH_CATALOG_PASS',len(records),glb_hash,stage_hash)
