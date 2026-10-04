"""Preserve bakes across verified camera-only exports; retain original provenance."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--previous',type=Path,required=True)
options=parser.parse_args()
subprocess.run([sys.executable,str(ROOT/'scripts/verify_reflection_camera_export.py'),
                '--previous',str(options.previous)],check=True)
proof_path=ROOT/'export/reflection-camera-alignment.json'
proof=json.loads(proof_path.read_text())
old=proof['previous_source_glb_sha256'];new=proof['source_glb_sha256']
assert old!=new
assert hashlib.sha256((ROOT/'export/garden-of-dreams.glb').read_bytes()).hexdigest()==new
assert proof['binary_data_identical'] and proof['non_camera_nodes_and_scene_membership_identical']
assert proof['mesh_material_texture_accessor_records_identical']
count=0
for path in (ROOT/'export/lightmaps').glob('*.json'):
    record=json.loads(path.read_text())
    if record.get('source_glb_sha256')!=old:continue
    image=path.parent/record['texture']
    assert image.is_file()
    record['baked_from_source_glb_sha256']=record.get('baked_from_source_glb_sha256',old)
    record['source_glb_sha256']=new
    record['camera_only_revalidation']={
        'previous_source_glb_sha256':old,'compatible_source_glb_sha256':new,
        'proof':'reflection-camera-alignment.json',
        'proof_sha256':hashlib.sha256(proof_path.read_bytes()).hexdigest(),
        'texture_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),
    }
    record['status']='Cycles bake retained after verified camera-only export; original bake source recorded'
    path.write_text(json.dumps(record,indent=2)+'\n')
    count+=1
assert count>0
print('CAMERA_ONLY_LIGHTMAP_REVALIDATION_PASS',count,'unchanged textures; original bake source retained')
