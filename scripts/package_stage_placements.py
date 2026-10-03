"""Make the placed-stage site libraries directly openable in Blender."""
import bpy,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1]
catalog=json.loads((R/'export/stage-placements.json').read_text());slugs=catalog['changed_site_libraries']
for slug in slugs:
 path=R/f'blender/sites/SITE_{slug}.blend';bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.collections=[path.stem]
 c=dst.collections[0];s=bpy.context.scene;s.name=path.stem;s.collection.children.link(c);s.unit_settings.system='METRIC'
 cameras=[o for o in c.objects if o.type=='CAMERA' and ('wide' in o.name or 'stage_wide' in o.name)]
 if cameras:s.camera=cameras[0]
 else:
  from mathutils import Vector
  camera=bpy.data.objects.new('CAM_stage_placement_preview',bpy.data.cameras.new('Stage placement preview'));s.collection.objects.link(camera);camera.location=(0,-30,9);camera.rotation_euler=(Vector((0,45,8))-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera
 if slug=='stage':
  wash=next(o for o in c.objects if o.name=='LGT_stage_backdrop_wash')
  assert wash.type=='LIGHT' and wash.data.type=='AREA' and len(wash.light_linking.receiver_collection.objects)==5
 s.render.resolution_x=1600;s.render.resolution_y=680;s.render.resolution_percentage=100
 if slug in {r['site'] for r in catalog['placements']}:assert any(o.get('stage_placement') for o in c.objects)
 temp=path.with_name(path.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,path)
print('STAGE_SITE_LIBRARIES_PASS',len(slugs))
