"""Make the placed-tech site libraries directly openable in Blender."""
import bpy,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
slugs=sorted({r['site'] for r in json.loads((R/'export/tech-placements.json').read_text())['placements']})
for slug in slugs:
 path=R/f'blender/sites/SITE_{slug}.blend';bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.collections=[path.stem]
 c=dst.collections[0];s=bpy.context.scene;s.name=path.stem;s.collection.children.link(c);s.unit_settings.system='METRIC'
 s.camera=next(o for o in c.objects if o.type=='CAMERA' and ('wide' in o.name or 'stage_wide' in o.name))
 s.render.resolution_x=1600;s.render.resolution_y=680;s.render.resolution_percentage=100
 assert any(o.get('tech_placement') for o in c.objects)
 temp=path.with_name(path.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,path)
print('TECH_SITE_LIBRARIES_PASS',len(slugs))
