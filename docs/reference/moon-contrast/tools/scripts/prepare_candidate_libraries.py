"""Package a separate complete candidate source without rewriting authoring.

Run before package_site_washes.py in the same scratch tree. Its linked master
is provisional until the separate packager verifies shared receiver identity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from lightmap_catalog import glb_document
from wash_receiver_contract import validate_source_receivers

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=args.root.resolve()
repo=Path(__file__).resolve().parents[1]
assert root!=repo and repo not in root.parents,'Use a separate candidate tree'
source=root/'blender/authoring.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert not (root/'blender/master.blend').exists(),'Do not overwrite a previous candidate master'
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
document=glb_document(root/'export/garden-of-dreams.glb')
stage=bpy.data.collections['SITE_stage']
reference=bpy.data.objects['LGT_stage_backdrop_wash']
expected=validate_source_receivers(reference.light_linking.receiver_collection.objects,document)
washes=[o for o in scene.objects if o.type=='LIGHT' and o.data.type=='AREA' and o.data.energy>0]
assert len(washes)==12
plan=json.loads((repo/'export/site-wash-rig.json').read_text())
assert {o['wash_site'] for o in washes}==set(plan['washes'])
for wash in washes:
    validate_source_receivers(wash.light_linking.receiver_collection.objects,document)
    plan['washes'][wash['wash_site']]['receivers']=sorted(expected)
plan.update(status='candidate_saved_rig',source_glb_sha256=hashlib.sha256((root/'export/garden-of-dreams.glb').read_bytes()).hexdigest())
(root/'export/site-wash-rig.json').write_text(json.dumps(plan,indent=2)+'\n')
collections=[c for c in scene.collection.children if c.name.startswith('SITE_')]
assert len(collections)==15
for collection in collections:
    bpy.data.libraries.write(str(root/'blender/sites'/(collection.name+'.blend')),{collection},fake_user=True,compress=True)
master=bpy.data.scenes.new('Garden of Dreams | master')
master.world=scene.world
master.unit_settings.system='METRIC'
master.render.engine=scene.render.engine
master.render.resolution_x=1410;master.render.resolution_y=600
for file in sorted((root/'blender/sites').glob('SITE_*.blend')):
    with bpy.data.libraries.load(str(file),link=True) as (available,loaded):loaded.collections=[file.stem]
    master.collection.children.link(loaded.collections[0])
    if file.stem=='SITE_qinfang-ting':master.camera=next(o for o in loaded.collections[0].objects if o.name=='CAM_stage_wide')
bpy.context.window.scene=master
master.view_layers.update()
bpy.ops.wm.save_as_mainfile(filepath=str(root/'blender/master.blend'),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
report={'status':'candidate_libraries_saved_receiver_packaging_pending','authoring_sha256':digest,'receiver_objects':expected,'site_libraries':len(collections),'scope':'Candidate source extraction; shared linked receiver identity and final native audit still required.'}
(root/'export/candidate-libraries.json').write_text(json.dumps(report,indent=2)+'\n')
print('CANDIDATE_LIBRARIES_PREPARED',len(collections),'authoring unchanged; packager required')
