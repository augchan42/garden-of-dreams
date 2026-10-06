"""Report the saved per-site lighting rig against spec section 9, without edits."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
report={'authoring_blend_sha256':hashlib.sha256((ROOT/'blender/authoring.blend').read_bytes()).hexdigest(),
        'scope':'Saved Blender scene lighting inventory; not engine visual or performance acceptance.',
        'sites':{},'shared_stage_washes':[],'missing_per_site_washes':[],
        'sites_without_owned_keys':[],'other_scene_lights':[]}
owned_light_names=set()
for collection in sorted(bpy.data.collections,key=lambda c:c.name):
    if not collection.name.startswith('SITE_'):continue
    lights=[obj for obj in collection.all_objects if obj.type=='LIGHT' and obj.name in scene.objects]
    records=[{'name':o.name,'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color),
              'linked_receivers':sorted(r.name for r in o.light_linking.receiver_collection.objects)
               if o.light_linking.receiver_collection else []} for o in lights]
    if collection.name=='SITE_stage':
        report['shared_stage_washes']=[r for r in records if r['type']=='AREA']
        owned_light_names.update(r['name'] for r in report['shared_stage_washes'])
        continue
    slug=collection.name.removeprefix('SITE_')
    if not (ROOT/'docs/sites'/f'{slug}.md').exists():continue
    keys=[r for r in records if r['type'] in ['SUN','SPOT']]
    washes=[r for r in records if r['type']=='AREA']
    report['sites'][slug]={'keys':keys,'washes':washes,'practicals':[r for r in records if r['type']=='POINT']}
    owned_light_names.update(r['name'] for r in records)
    if not keys:report['sites_without_owned_keys'].append(slug)
    if not washes:report['missing_per_site_washes'].append(slug)
assert len(report['sites'])==14, report['sites'].keys()
for obj in scene.objects:
    if obj.type=='LIGHT' and obj.name not in owned_light_names:
        report['other_scene_lights'].append({'name':obj.name,'type':obj.data.type,
            'energy':obj.data.energy,'color':list(obj.data.color),
            'location':list(obj.location),'collections':[c.name for c in obj.users_collection]})
(ROOT/'export/lighting-rig-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('LIGHTING_RIG_AUDIT',len(report['sites']),'sites',len(report['shared_stage_washes']),'shared washes',len(report['missing_per_site_washes']),'missing per-site washes',flush=True)
