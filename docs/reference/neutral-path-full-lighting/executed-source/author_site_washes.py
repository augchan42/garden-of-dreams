"""Author linked backdrop washes for the twelve exterior site contracts.

Terminal cells borrow window spill; the tunnel explicitly has no wash. Use
--apply to save the editable sources. Default mode reports the proposed rig.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--apply',action='store_true')
parser.add_argument('--report',type=Path,default=ROOT/'export/site-wash-rig.json')
options=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
bpy.context.view_layer.update()
stage=bpy.data.collections['SITE_stage']
receivers=bpy.data.collections['LINK_stage_backdrop_receivers']
assert len(receivers.objects)==5
source=ROOT/'export/garden-of-dreams.glb'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
static_objects={o.name:(o.type,list(map(list,o.matrix_world)),
                       (o.data.type,o.data.energy,list(o.data.color)) if o.type=='LIGHT' else None)
                for o in scene.objects if not(o.type=='LIGHT' and o.data.type=='AREA')}
exceptions={'terminal-cells':'No broad key; borrowed cyclorama/window spill, per its site sheet.',
            'rockery-gate':'No wash in the tunnel, per its site sheet.'}
records={}
for path in sorted((ROOT/'docs/sites').glob('*.md')):
    if path.name=='README.md':continue
    slug=path.stem
    if slug in exceptions:continue
    collection=bpy.data.collections.get('SITE_'+slug)
    assert collection,slug
    camera_name='CAM_stage_wide' if slug=='qinfang-ting' else 'CAM_'+slug+'_wide'
    cameras=[o for o in collection.objects if o.type=='CAMERA' and o.name==camera_name]
    assert len(cameras)==1,(slug,[o.name for o in cameras])
    camera=cameras[0]
    direction=camera.matrix_world.to_quaternion()@Vector((0,0,-1))
    direction.z=0
    assert direction.length>.1
    direction.normalize()
    # Intersect the establishing sightline with the painted 48 m enclosure.
    origin=camera.matrix_world.translation.copy();origin.z=0
    projection=origin.dot(direction)
    distance=-projection+math.sqrt(projection*projection+48*48-origin.length_squared)
    target=origin+direction*distance
    target.z=8
    position=target-direction*12
    position.z=11
    color=(.68,.78,.73) if slug=='qinfang-ting' else (.72,.78,.84)
    name='LGT_'+slug.replace('-','_')+'_backdrop_wash'
    records[slug]={'name':name,'camera':camera.name,'position':list(position),'target':list(target),
                   'energy':150.0,'color':list(color),'size':15.0,'size_y':10.0,
                   'receivers':sorted(o.name for o in receivers.objects)}
    if not options.apply:continue
    old=bpy.data.objects.get(name)
    if old:
        assert old.type=='LIGHT' and old.data.type=='AREA'
        old_data=old.data
        bpy.data.objects.remove(old,do_unlink=True)
        if old_data.users==0:bpy.data.lights.remove(old_data)
    data=bpy.data.lights.new(name,'AREA')
    data.shape='RECTANGLE';data.size=15;data.size_y=10
    data.energy=150;data.color=color
    light=bpy.data.objects.new(name,data)
    collection.objects.link(light)
    light.location=position
    light.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler()
    light.light_linking.receiver_collection=receivers
    light['wash_site']=slug
    light['lighting_contract']='Native Cycles backdrop-only Area wash; site sheet exceptions retained.'
assert len(records)==12,records.keys()
if options.apply:
    # The old shared wash stays editable as a disabled reference; replacing it
    # avoids adding its energy on top of the twelve site washes.
    bpy.data.objects['LGT_stage_backdrop_wash'].data.energy=0
    bpy.context.view_layer.update()
    current={o.name:(o.type,list(map(list,o.matrix_world)),
                    (o.data.type,o.data.energy,list(o.data.color)) if o.type=='LIGHT' else None)
             for o in scene.objects if not(o.type=='LIGHT' and o.data.type=='AREA')}
    assert current==static_objects,'Wash authoring changed a static object or punctual light'
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/authoring.blend'),compress=True)
    for slug in [*records,'stage']:
        collection=bpy.data.collections['SITE_'+slug]
        bpy.data.libraries.write(str(ROOT/'blender/sites'/('SITE_'+slug+'.blend')),{collection},fake_user=True,compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
report={'status':'saved' if options.apply else 'proposed','source_glb_sha256':digest,
        'exceptions':exceptions,'washes':records,'shared_reference_energy':bpy.data.objects['LGT_stage_backdrop_wash'].data.energy}
options.report.parent.mkdir(parents=True,exist_ok=True)
options.report.write_text(json.dumps(report,indent=2)+'\n')
print('SITE_WASH_RIG',report['status'],len(records),'exterior sites; static objects/punctual lights unchanged',flush=True)
