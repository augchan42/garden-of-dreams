"""Keep directly openable site libraries and linked-master wash receivers valid."""
import bpy
import argparse
import json
import os
import sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from lightmap_catalog import glb_document
from wash_receiver_contract import validate_source_receivers, expected_receivers

ROOT=Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/'export/site-wash-rig.json').read_text())
document=glb_document(ROOT/'export/garden-of-dreams.glb')
expected=expected_receivers(document)
assert all(set(record['receivers'])==set(expected) for record in plan['washes'].values())
parser=argparse.ArgumentParser()
parser.add_argument('--sites',nargs='+',default=['stage',*plan['washes']])
options=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert len(set(options.sites))==len(options.sites)
assert set(options.sites)<=set(['stage',*plan['washes'],*plan['exceptions']])
assert options.sites[0]=='stage','Package the shared receiver IDs first'
stage_path=ROOT/'blender/sites/SITE_stage.blend'
for slug in options.sites:
    path=ROOT/'blender/sites'/('SITE_'+slug+'.blend')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(path),link=False) as (available,loaded):
        loaded.collections=[path.stem]
    collection=loaded.collections[0]
    scene=bpy.context.scene
    scene.name=path.stem
    scene.collection.children.link(collection)
    scene.unit_settings.system='METRIC'
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=1410;scene.render.resolution_y=600
    scene.camera=next((o for o in collection.objects if o.type=='CAMERA' and ('wide' in o.name)),None)
    if scene.camera is None:
        camera=bpy.data.objects.new('CAM_library',bpy.data.cameras.new('CAM_library'))
        scene.collection.objects.link(camera)
        camera.location=(0,-20,10)
        camera.rotation_euler=(Vector((0,30,7))-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.camera=camera
    if slug in plan['washes']:
        # All site-file lights reference the same external stage object IDs.
        # A master can then link each site without dangling private receiver
        # copies that never appear in its rendered scene.
        names=plan['washes'][slug]['receivers']
        with bpy.data.libraries.load(str(stage_path),link=True) as (available,loaded):
            assert set(names)<=set(available.objects)
            loaded.objects=names
        receivers=bpy.data.collections.new('LINK_'+slug.replace('-','_')+'_backdrop_receivers')
        for obj in loaded.objects:
            assert obj.library and Path(bpy.path.abspath(obj.library.filepath)).resolve()==stage_path
            receivers.objects.link(obj)
        light=next(o for o in collection.objects if o.name==plan['washes'][slug]['name'])
        light.light_linking.receiver_collection=receivers
        for obj in receivers.objects:obj.library.filepath='//'+os.path.relpath(stage_path,path.parent)
    temporary=path.with_name(path.stem+'-packaged.blend')
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
    os.replace(temporary,path)
    print('SITE_WASH_LIBRARY_PASS',slug,flush=True)
# Load the existing linked assembly and check actual object identity. No master
# rewrite is needed: its existing library links resolve to the updated sources.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/master.blend'))
scene=next(s for s in bpy.data.scenes if s.name=='Garden of Dreams | master')
bpy.context.window.scene=scene
stage_col=next(c for c in scene.collection.children if c.name=='SITE_stage')
actual={o for o in stage_col.objects if o.name in expected}
validate_source_receivers(actual,document)
washes=[o for o in scene.objects if o.type=='LIGHT' and o.data.type=='AREA' and o.data.energy>0]
assert len(washes)==12
for light in washes:
    assert set(light.light_linking.receiver_collection.objects)==actual, ('Master wash links to invisible copies',light.name)
print('LINKED_MASTER_WASH_PASS',len(washes),'lights share',len(actual),'exact visible stage receivers',flush=True)
