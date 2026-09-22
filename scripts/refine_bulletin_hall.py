"""Complete the study-hall furniture and safe public approach."""
import bpy, math, ast, os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
helpers=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
wood=bpy.data.materials['MAT_lattice_wood'];stone=bpy.data.materials['MAT_plaster_rock'];gold=bpy.data.materials['MAT_bronze'];black=bpy.data.materials['MAT_backstage'];plaster=bpy.data.materials['MAT_whitewash']
sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children};C=sites['qiushuang-zhai']
# Scope reruns to furniture and geometry authored by this pass.
for o in list(C.objects):
 if o.name.startswith(('STUDY_','COL_study_','TRG_qiushuang_zhai_','CAM_qiushuang-zhai_','KIT_pavilion_hall_post')):
  bpy.data.objects.remove(o,do_unlink=True)
box('STUDY_front_walk',(22,13.85,-.12),(10,2.3,.24),stone)
collision('study_front_walk',(22,13.85,-.12),(10,2.3,.24))
collision('study_front_wall',(22,16,1.3),(9,.16,2.6))
for x in [17.7,20.425,23.575,26.3]:
 cyl('STUDY_post',(x,15.05,1.5),.075,3,wood)
 collision('study_post',(x,15.05,1.5),(.17,.17,3))
for bank,x in [('left',18.85),('centre',22),('right',25.15)]:
 box('STUDY_desk_'+bank,(x,15.24,.68),(1.9,.85,.12),wood)
 for dx in [-.78,.78]:
  for dy in [-.28,.28]:box('STUDY_desk_leg',(x+dx,15.24+dy,.31),(.09,.09,.62),wood)
 collision('study_desk_'+bank,(x,15.24,.36),(1.9,.85,.72))
 box('STUDY_keyboard_'+bank,(x,14.98,.77),(.55,.2,.055),black)
 for row in range(3):
  for col in range(10):box('STUDY_key',(x-.23+col*.05,14.92+row*.05,.805),(.03,.032,.012),gold)
 empty('TRG_qiushuang_zhai_'+bank,(x,13.9,0),'qiushuang_zhai')
 camera('CAM_qiushuang-zhai_'+bank,(x,12.7,1.65),(x,15.6,1.35),38)
# Two hanging scrolls in the gaps between screen banks.
for x in [20.9,23.1]:
 box('STUDY_scroll_paper',(x,15.8,1.75),(.4,.035,1.3),plaster)
 for z in [1.08,2.42]:beam('STUDY_scroll_roller',(x-.25,15.74,z),(x+.25,15.74,z),.03,wood)
 for i in range(6):box('STUDY_scroll_ink',(x,15.77,2.23-i*.18),(.12,.01,.07),black)
for x in [17.85,26.15]:
 box('STUDY_closed_door',(x,15.89,1.15),(.62,.12,2.3),wood)
 box('STUDY_door_latch',(x,15.81,1),(.22,.06,.045),gold)
empty('TRG_qiushuang_zhai_entry',(22,13.7,0),'qiushuang_zhai')
empty('TRG_qiushuang_zhai_return',(19,12.8,0),'qiushuang_zhai')
camera('CAM_qiushuang-zhai_wide',(22,6.8,3.2),(22,15.5,1.45),32)
C=sites['stage']
for o in list(C.objects):
 if o.name.startswith(('STUDY_approach','COL_study_approach')):bpy.data.objects.remove(o,do_unlink=True)
box('STUDY_approach',(19,6.45,-.12),(1.8,13.1,.24),stone)
collision('study_approach',(19,6.45,-.12),(1.8,13.1,.24))
assert sum(o.name.startswith('KIT_tech_CRT_screen') for o in sites['qiushuang-zhai'].objects)==12
assert sum(o.name.startswith('TRG_qiushuang_zhai_') for o in sites['qiushuang-zhai'].objects)==5
scene.camera=bpy.data.objects['CAM_qiushuang-zhai_wide']
scene.render.resolution_x=1410;scene.render.resolution_y=600;scene.render.resolution_percentage=100
scene.render.filepath=str(R/'docs/reference/qiushuang-zhai-raw.png');bpy.ops.render.render(write_still=True)
scene.camera=next(o for o in sites['qinfang-ting'].objects if o.name=='CAM_stage_wide')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
changed=['qiushuang-zhai','stage']
for slug in changed:bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{sites[slug]},fake_user=True,compress=True)
for slug in changed:
 file=R/'blender/sites'/('SITE_'+slug+'.blend')
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
 s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC';s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1410;s.render.resolution_y=600
 s.camera=next((o for o in s.objects if o.type=='CAMERA'),None)
 temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('STUDY_ART_PASS: 12 screens, 3 desks, 2 scrolls, 5 markers and connected approach saved')
