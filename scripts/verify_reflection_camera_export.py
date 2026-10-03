"""Compare the camera pass with a supplied predecessor GLB, including binary data."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--previous',type=Path,required=True)
options=parser.parse_args()

def read(path):
    blob=path.read_bytes()
    length=struct.unpack_from('<I',blob,12)[0]
    return json.loads(blob[20:20+length]),blob[20+length:],hashlib.sha256(blob).hexdigest()

old,old_binary,old_hash=read(options.previous)
new,new_binary,new_hash=read(ROOT/'export/garden-of-dreams.glb')
assert old_binary==new_binary,'Camera alignment changed binary geometry or image data'
old_structure={n['name']:n for n in old['nodes'] if n['name'].startswith(('COL_','TRG_','LGT_'))}
new_structure={n['name']:n for n in new['nodes'] if n['name'].startswith(('COL_','TRG_','LGT_'))}
assert old_structure==new_structure
assert old['extensions']['KHR_lights_punctual']==new['extensions']['KHR_lights_punctual']
for key in ['meshes','materials','images','textures','samplers','accessors','bufferViews']:
    assert old.get(key)==new.get(key),key
report={'previous_source_glb_sha256':old_hash,'source_glb_sha256':new_hash,
        'unchanged_collision_trigger_light_records':len(old_structure),
        'mesh_material_texture_accessor_records_identical':True,'binary_data_identical':True,'cameras':{}}
for node in new['nodes']:
    if node['name'].startswith('CAM_aojing-guan'):
        report['cameras'][node['name']]={**node,'projection':new['cameras'][node['camera']]}
assert len(report['cameras'])==3
(ROOT/'export/reflection-camera-alignment.json').write_text(json.dumps(report,indent=2)+'\n')
print('REFLECTION_CAMERA_EXPORT_PRESERVATION_PASS',len(old_structure),new_hash)
