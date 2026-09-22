"""Build Aojing’s lowered hall, pond, dry ledge and guarded ramp."""
import bpy, math, ast, os
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
tree=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','gold':'bronze','black':'backstage','plaster':'whitewash','roofmat':'rooftile','crtamber':'crt_amber','foliage':'foliage_card','water':'water'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
font=next(f for f in bpy.data.fonts if 'Songti' in f.filepath)
C=next(c for c in scene.collection.children if c.name=='SITE_aojing-guan')
for o in list(C.objects):bpy.data.objects.remove(o,do_unlink=True)
# World-space construction: hall floor -0.65 m, pond surface -1.1 m.
box('AOJING_dry_ledge',(26,-13.1,-.8),(7.8,1.8,.3),stone)
collision('aojing_dry_ledge',(26,-13.1,-.8),(7.8,1.8,.3))
box('AOJING_hall_floor',(26,-11.7,-.8),(7.8,1.4,.3),stone)
collision('aojing_hall_floor',(26,-11.7,-.8),(7.8,1.4,.3))
box('AOJING_closed_front',(26,-12.2,.65),(7,.2,2.6),plaster)
collision('aojing_closed_front',(26,-12.2,.65),(7,.24,2.6))
box('AOJING_backstage',(26,-10.7,.65),(7,.2,2.6),black)
for x in [22.5,29.5]:
 box('AOJING_return',(x,-11.45,.65),(.2,1.7,2.6),plaster)
 collision('aojing_return',(x,-11.45,.65),(.24,1.7,2.6))
# One broad window is the focal point for the later reflection pass.
box('AOJING_amber_window',(26,-12.325,.9),(2.35,.05,1.35),crtamber)
for x in [24.8,25.2,25.6,26,26.4,26.8,27.2]:box('AOJING_window_lattice',(x,-12.39,.9),(.035,.07,1.45),wood)
for z in [.18,.66,1.14,1.62]:box('AOJING_window_lattice',(26,-12.39,z),(2.45,.07,.035),wood)
for x in [23.4,28.6]:
 box('AOJING_shutter',(x,-12.33,.55),(1.1,.1,2.3),wood)
 for j in range(5):box('AOJING_shutter_seam',(x-.44+j*.22,-12.39,.55),(.012,.02,2.2),black)
# Low, broad roof: a continuous silhouette rather than paired pavilions.
vs=[(21.9,-13.05,2.0),(30.1,-13.05,2.0),(22.5,-11.6,3.05),(29.5,-11.6,3.05),(21.9,-10.1,2.0),(30.1,-10.1,2.0)]
mesh('AOJING_roof',vs,[(0,1,3,2),(2,3,5,4)],roofmat)
beam('AOJING_ridge',(22.3,-11.6,3.08),(29.7,-11.6,3.08),.075,stone)
for i in range(41):
 x=22+i*.2;ridge_x=26+(x-26)*.86
 beam('AOJING_tile',(x,-13.05,2.02),(ridge_x,-11.6,3.07),.022,roofmat)
 beam('AOJING_tile',(ridge_x,-11.6,3.07),(x,-10.1,2.02),.022,roofmat)
# Keep the water as a separate named material batch for planar-reflection integration.
pondmat=bpy.data.materials.get('MAT_aojing_water')
if not pondmat:
 pondmat=water.copy();pondmat.name='MAT_aojing_water'
mesh('AOJING_pond',[(20.5,-21,-1.1),(32,-21,-1.1),(32,-14,-1.1),(20.5,-14,-1.1)],[(0,1,2,3)],pondmat)
for p,size in [((20.35,-17.5,-.8),(.3,7.3,.6)),((32.15,-17.5,-.8),(.3,7.3,.6)),((26.25,-21.15,-.8),(12.2,.3,.6))]:box('AOJING_embankment',p,size,stone)
# Low stone parapet protects the ledge; west end remains open to the ramp.
box('AOJING_ledge_parapet',(26,-14.0,-.38),(7.8,.18,.54),stone)
collision('aojing_ledge_parapet',(26,-14,-.38),(7.8,.22,.54))
box('AOJING_ledge_end',(29.9,-13.1,-.38),(.18,1.8,.54),stone)
collision('aojing_ledge_end',(29.9,-13.1,-.38),(.22,1.8,.54))
sign('凹晶館',(26,-12.55,1.93),2)
light('LGT_aojing_window',(26,-12.8,.9),65,(1,.38,.005))
light('LGT_aojing-guan_key',(30,-16,5),300,(.18,1,.18),'SPOT',(26,-12,1))
for name,p in [('entry',(23,-13.1,-.65)),('reflection',(26,-13.1,-.65)),('return',(21.9,-13.1,-.65))]:empty('TRG_aojing_guan_'+name,p,'aojing_guan')
camera('CAM_aojing-guan_wide',(24,-20,1.6),(26,-12,-.4),32)
camera('CAM_aojing-guan_reflection',(26,-19,.1),(26,-12,-.7),32)
sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children}
C=sites['stage']
# Cut away the raised canvas where the lowered hall and pond sit.
for o in list(C.objects):
 if (o.name.startswith('KIT_stage_painted_canvas') and sum(v.co.y for v in o.data.vertices)/len(o.data.vertices)<0) or o.name.startswith(('AOJING_ground','AOJING_approach','COL_aojing_approach')):
  bpy.data.objects.remove(o,do_unlink=True)
 elif o.name.startswith(('KIT_water_stone_walk','COL_stone_walk')) and abs(o.location.x-25)<.01 and abs(o.location.y+6)<.01:
  bpy.data.objects.remove(o,do_unlink=True)
ground=bpy.data.materials['MAT_stage_canvas']
for p,size in [((-12.5,-23,-.38),(61,35,.5)),((37.5,-23,-.38),(11,35,.5)),((25,-30.75,-.38),(14,19.5,.5)),((25,-7.75,-.38),(14,4.5,.5))]:box('AOJING_ground',p,size,ground)
for p,size in [((20.6,-1,-.12),(4.6,1.8,.24)),((19,-7.05,-.12),(1.8,13.9,.24))]:
 box('AOJING_approach',p,size,stone);collision('aojing_approach',p,size)
# Sloped ramp drops 0.65 m; separate simple collider follows the same slope.
verts=[(19.9,-14,-.24),(22.3,-14,-.89),(22.3,-12.2,-.89),(19.9,-12.2,-.24),(19.9,-14,0),(22.3,-14,-.65),(22.3,-12.2,-.65),(19.9,-12.2,0)]
faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
mesh('AOJING_approach_ramp',verts,faces,stone)
o=mesh('COL_aojing_approach_ramp',verts,faces,None);o.hide_render=True;o.display_type='WIRE';o['godot_collision']='box'
for y in [-14,-12.2]:
 beam('AOJING_approach_guard',(19.9,y,.55),(22.3,y,-.1),.055,wood)
 # Sloped upper guard volumes keep the capsule on the ramp.
 guardverts=[(x,y+dy,z+dz) for x,z in [(19.9,0),(22.3,-.65)] for dy,dz in [(-.07,0),(.07,0),(.07,.6),(-.07,.6)]]
 gfaces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 o=mesh('COL_aojing_approach_guard',guardverts,gfaces,None);o.hide_render=True;o.display_type='WIRE';o['godot_collision']='box'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for slug in ['aojing-guan','stage']:
 bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{sites[slug]},fake_user=True,compress=True)
for slug in ['aojing-guan','stage']:
 file=R/'blender/sites'/('SITE_'+slug+'.blend')
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
 s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
 s.camera=next((o for o in s.objects if o.type=='CAMERA'),None)
 temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('AOJING_ART_PASS: lowered hall, one window, dry ledge, pond and guarded ramp; engine reflection pending')
