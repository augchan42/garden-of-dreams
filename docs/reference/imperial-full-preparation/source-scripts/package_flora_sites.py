"""Make the five flora-refined sites directly openable without rebuilding their art."""
import bpy,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for slug in ['xiaoxiang-guan','yihong-yuan','longcui-an','ziling-zhou','qinfang-ting']:
 path=R/f'blender/sites/SITE_{slug}.blend';bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.collections=[path.stem]
 col=dst.collections[0];s=bpy.context.scene;s.name=path.stem;s.collection.children.link(col);s.unit_settings.system='METRIC';s.render.engine='BLENDER_EEVEE'
 s.camera=next(o for o in col.objects if o.type=='CAMERA' and ('wide' in o.name or 'stage_wide' in o.name))
 s.render.resolution_x=1600;s.render.resolution_y=680;s.render.resolution_percentage=100
 tmp=path.with_name(path.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,path)
 assert any(o.get('flora_placement') for o in col.objects)
print('FLORA_SITE_LIBRARIES_PASS',5)
