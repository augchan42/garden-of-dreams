"""Complete Tubi's public terrace and continuous four-metre climb."""
import bpy, math, ast, os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
tree=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','gold':'bronze','black':'backstage','amber':'lantern'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children}
C=sites['tubi-tang']
for o in list(C.objects):
 if o.name.startswith(('TUBI_','COL_tubi_','HERO_tubi_terrace_stair','TRG_tubi_tang_','CAM_tubi-tang_','LGT_tubi-tang_key','LGT_lantern','KIT_props_lantern_')):
  bpy.data.objects.remove(o,do_unlink=True)
# Front terrace widens the narrow facade platform, with an open stair landing.
box('TUBI_terrace',(7,31,3.85),(9,2.4,.3),stone)
collision('tubi_terrace',(7,31,3.85),(9,2.4,.3))
collision('tubi_closed_hall',(7,33,5.3),(7,.18,2.6))
for x in [4.55,7,9.45]:collision('tubi_hall_post',(x,32.1,5.5),(.2,.2,3))
def parapet(a,b):
 d=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2
 o=box('TUBI_parapet',(0,0,.45),(.16,d.length,.9),stone)
 o.location=mid;o.rotation_euler.z=-math.atan2(d.x,d.y)
 c=collision('tubi_parapet',(0,0,.45),(.18,d.length,.9))
 c.location=mid;c.rotation_euler.z=o.rotation_euler.z
 beam('TUBI_parapet_cap',Vector(a)+Vector((0,0,.92)),Vector(b)+Vector((0,0,.92)),.11,stone)
for a,b in [((2.5,29.8,4),(8.7,29.8,4)),((11.3,29.8,4),(11.5,29.8,4)),((2.5,29.8,4),(2.5,34.9,4)),((11.5,29.8,4),(11.5,34.9,4))]:parapet(a,b)
# Twenty visible treads; a single simplified ramp avoids capsule snagging on risers.
for i in range(20):
 top=(i+1)*.2
 box('TUBI_stair_tread',(10,20.25+i*.5,top-.1),(2.2,.5,.2),stone)
# Flatten before the deck edge so the capsule clears its vertical front face.
vs=[(x,y,z) for x in [8.9,11.1] for y,z in [(20,0),(29.5,4),(30.2,4),(30.2,-.2),(20,-.2)]]
c=mesh('COL_tubi_stair_ramp',vs,[(0,5,6,1),(1,6,7,2),(2,7,8,3),(3,8,9,4),(4,9,5,0),(4,3,2,1,0),(5,6,7,8,9)],None)
c.hide_render=True;c['godot_collision']='trimesh'
for x in [8.85,11.15]:
 beam('TUBI_stair_handrail',(x,20,.9),(x,30,4.9),.055,wood)
 for i in range(11):
  y=20+i;z=i*.4
  beam('TUBI_stair_baluster',(x,y,z),(x,y,z+.9),.035,wood)
 # A thin sloping prism keeps the visitor on the stair.
 v=[(xx,y,z+dz) for xx in [x-.05,x+.05] for y,z in [(20,0),(30,4)] for dz in [0,1]]
 guard=mesh('COL_tubi_stair_guard',v,[(0,2,3,1),(4,5,7,6),(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3)],None)
 guard.hide_render=True
# Table sits beside the arrival aisle; leave the path to the overlook clear.
cyl('TUBI_topic_table',(4.4,31.05,4.82),.7,.15,stone,24)
cyl('TUBI_topic_pedestal',(4.4,31.05,4.38),.22,.76,stone,12)
collision('tubi_topic_table',(4.4,31.05,4.45),(1.4,1.4,.9))
box('TUBI_topic_frame',(4.4,31.05,4.925),(.8,.48,.055),gold)
box('TUBI_topic_panel',(4.4,31.05,4.96),(.7,.38,.035),black)
for i in range(5):box('TUBI_topic_line',(4.4,30.9+i*.07,4.985),(.5,.016,.009),amber)
lantern((5.5,31.6,6.2))
light('LGT_tubi-tang_key',(12,26,11),450,(1,.38,.02),'SPOT',(7,31,4))
for name,p in [('stair_foot',(10,19.6,0)),('entry',(7,31,4)),('news_table',(5.5,31,4)),('overlook',(7,30.35,4)),('return',(10,30.4,4))]:empty('TRG_tubi_tang_'+name,p,'tubi_tang')
camera('CAM_tubi-tang_wide',(16,20,10),(7,32,4.9),32)
camera('CAM_tubi-tang_overlook',(7,30.5,5.7),(0,0,1.2),32)
camera('CAM_tubi-tang_table',(6.4,30.1,5.6),(4.4,31.05,4.9),40)
C=sites['stage']
for o in list(C.objects):
 if o.name.startswith(('TUBI_approach','COL_tubi_approach')):bpy.data.objects.remove(o,do_unlink=True)
for p,size in [((16.5,16.25,-.12),(1.8,5.5,.24)),((13.25,19,-.12),(8.3,1.8,.24)),((19.25,13.5,-.12),(7.3,1.8,.24)),((10,19.5,-.12),(2.2,1.8,.24))]:
 box('TUBI_approach',p,size,stone);collision('tubi_approach',p,size)
assert sum(o.name.startswith('TRG_tubi_tang_') for o in sites['tubi-tang'].objects)==5
assert sum(o.name.startswith('KIT_props_lantern_paper') for o in sites['tubi-tang'].objects)==1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
changed=['tubi-tang','stage']
for slug in changed:bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{sites[slug]},fake_user=True,compress=True)
for slug in changed:
 file=R/'blender/sites'/('SITE_'+slug+'.blend')
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
 s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
 s.camera=next((o for o in s.objects if o.type=='CAMERA'),None)
 temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('HILLTOP_ART_SAVED: terrace, 20 treads, ramp collider, parapets, table, one lantern, five markers')
