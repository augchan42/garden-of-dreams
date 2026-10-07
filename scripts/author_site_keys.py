"""Add Qinfang, Ouxiang and Ziling hard keys; save only with --apply.

The shared green fill becomes neutral. Geometry, cameras, receiver linking,
practicals and all other site keys are preserved exactly.
"""
import argparse
import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true')
parser.add_argument('--report', type=Path, default=ROOT/'export/site-key-rig.json')
options = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
scene = next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene = scene
bpy.context.view_layer.update()
slugs = ('qinfang-ting', 'ouxiang-xie', 'ziling-zhou')
names = {'LGT_' + slug + '_key' for slug in slugs}
fill_name = 'LGT_stage_green_key'
def snapshot():
    return {o.name: {'type':o.type, 'matrix':list(map(list,o.matrix_world)),
                    'light':(o.data.type,o.data.energy,list(o.data.color)) if o.type=='LIGHT' else None}
            for o in scene.objects if o.name not in names | {fill_name}}
before = snapshot()
direction = Vector((math.cos(math.radians(35))/math.sqrt(2),
                    -math.cos(math.radians(35))/math.sqrt(2),math.sin(math.radians(35))))
config = {
    'qinfang-ting': {'type':'SUN','position':list(direction*25),'target':[0,0,0],
                     'energy':.6,'color':[.68,.78,.73]},
    'ouxiang-xie': {'type':'SPOT','position':[-30,7,8],'target':[-23,.3,1],
                    'energy':450,'color':[.68,.78,.73]},
    'ziling-zhou': {'type':'SPOT','position':[-28,4,8],'target':[-35.4,0,1],
                    'energy':400,'color':[.65,.80,.72]},
}
for slug,record in config.items():
    name = 'LGT_'+slug+'_key'
    record['name'] = name
    record['hard_shadow'] = True
    record['sun_angle_degrees' if record['type']=='SUN' else 'shadow_radius_m'] = .5 if record['type']=='SUN' else .01
    if not options.apply: continue
    old = bpy.data.objects.get(name)
    if old:
        assert old.type=='LIGHT' and old.data.type==record['type']
        data=old.data
        bpy.data.objects.remove(old,do_unlink=True)
        if data.users==0:bpy.data.lights.remove(data)
    data = bpy.data.lights.new(name,record['type'])
    data.energy=record['energy'];data.color=record['color'];data.use_shadow=True
    if data.type=='SUN':data.angle=math.radians(.5)
    else:
        data.shadow_soft_size=.01
        data.spot_size=math.radians(65);data.spot_blend=0
    light=bpy.data.objects.new(name,data)
    bpy.data.collections['SITE_'+slug].objects.link(light)
    light.location=record['position']
    light.rotation_euler=(Vector(record['target'])-light.location).to_track_quat('-Z','Y').to_euler()
    light['lighting_contract']='Owned hard site key; muted green per user palette revision.'
fill={'name':fill_name,'energy':1.4,'color':[.70,.74,.78],
      'role':'Neutral shared fill; legacy object name retained.'}
if options.apply:
    light=bpy.data.objects[fill_name]
    light.data.energy=fill['energy'];light.data.color=fill['color']
    light['lighting_contract']=fill['role']
    bpy.context.view_layer.update()
    assert snapshot()==before,'Changed geometry, cameras, wash linking or unrelated lights'
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/authoring.blend'),compress=True)
    for slug in (*slugs,'stage'):
        collection=bpy.data.collections['SITE_'+slug]
        bpy.data.libraries.write(str(ROOT/'blender/sites'/('SITE_'+slug+'.blend')),{collection},fake_user=True,compress=True)
report={'status':'saved' if options.apply else 'proposed','keys':config,'shared_fill':fill,
        'unchanged_objects_checked':len(before),'canonical_glb_before_sha256':hashlib.sha256((ROOT/'export/garden-of-dreams.glb').read_bytes()).hexdigest(),
        'ordinary_bakes_require_refresh':True}
options.report.parent.mkdir(parents=True,exist_ok=True)
options.report.write_text(json.dumps(report,indent=2)+'\n')
print('SITE_KEY_AUTHORING',report['status'],len(config),'keys; preserved',len(before),'other objects',flush=True)
