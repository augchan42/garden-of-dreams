"""Build Longcui’s closed nunnery gate, plum trees and incense bowl."""
import bpy, math, ast, os
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
tree=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','gold':'bronze','black':'backstage','plaster':'whitewash','roofmat':'rooftile','crtamber':'crt_amber','foliage':'foliage_card','amber':'lantern'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
font=next(f for f in bpy.data.fonts if 'Songti' in f.filepath)
C=next(c for c in scene.collection.children if c.name=='SITE_longcui-an')
for o in list(C.objects):bpy.data.objects.remove(o,do_unlink=True)
box('LONGCUI_paving',(0,-1.7,-.12),(7.4,5.4,.24),stone)
collision('longcui_floor',(0,-1.7,-.12),(7.4,5.4,.24))
box('LONGCUI_closed_front',(0,0,1.25),(6,.22,2.5),plaster)
collision('longcui_closed_front',(0,0,1.25),(6,.26,2.5))
box('LONGCUI_backstage',(0,1.4,1.25),(6,.2,2.5),black)
for x in [-3,3]:
 box('LONGCUI_return',(x,.7,1.25),(.2,1.6,2.5),plaster)
 collision('longcui_return',(x,.7,1.25),(.24,1.6,2.5))
box('LONGCUI_wall_cap',(0,0,2.56),(6.4,.6,.15),roofmat)
for x in [-.52,.52]:
 box('LONGCUI_closed_gate',(x,-.19,1.075),(1.01,.16,2.1),wood)
 for j in range(5):box('LONGCUI_gate_plank',(x-.4+j*.2,-.28,1.075),(.013,.025,2.0),black)
 for z in [.3,1.15,1.9]:box('LONGCUI_gate_rail',(x,-.3,z),(1,.08,.065),wood)
 box('LONGCUI_gate_pull',(x*.32,-.37,1.1),(.06,.07,.19),gold)
for x in [-1.12,1.12]:box('LONGCUI_gate_jamb',(x,-.18,1.15),(.16,.35,2.3),stone)
box('LONGCUI_gate_lintel',(0,-.18,2.27),(2.4,.4,.18),stone)
box('LONGCUI_threshold',(0,-.28,.06),(2.35,.6,.12),stone)
collision('longcui_threshold',(0,-.28,.06),(2.35,.6,.12))
vs=[(-1.55,-.75,2.58),(1.55,-.75,2.58),(-1.4,.25,3.12),(1.4,.25,3.12),(-1.55,1.05,2.58),(1.55,1.05,2.58)]
mesh('LONGCUI_gate_roof',vs,[(0,1,3,2),(2,3,5,4)],roofmat)
beam('LONGCUI_ridge',(-1.6,.25,3.14),(1.6,.25,3.14),.07,stone)
for i in range(21):
 x=-1.5+i*.15
 beam('LONGCUI_tile',(x,-.75,2.6),(x*.9,.25,3.13),.022,roofmat)
 beam('LONGCUI_tile',(x*.9,.25,3.13),(x,1.05,2.6),.022,roofmat)
# Two bent plum trunks with sparse branching and small five-petal blossom clusters.
for tree,(px,py,flip) in enumerate([(-2.45,-1.8,1),(2.5,-2.5,-1)]):
 trunk=[Vector((px,py,0)),Vector((px+.2*flip,py+.05,.9)),Vector((px-.1*flip,py,1.7)),Vector((px+.22*flip,py+.1,2.7))]
 for j in range(3):beam('LONGCUI_plum_trunk',trunk[j],trunk[j+1],.12-j*.026,wood)
 collision('longcui_plum_trunk',(px,py,.7),(.48,.48,1.4))
 for branch in range(5):
  a=branch*math.tau/5+tree*.6;base=trunk[2] if branch<3 else trunk[3]
  mid=base+Vector((math.cos(a)*.65,math.sin(a)*.5,.6))
  tip=mid+Vector((math.cos(a+.3)*.65,math.sin(a+.3)*.5,.45))
  beam('LONGCUI_plum_branch',base,mid,.037,wood);beam('LONGCUI_plum_branch',mid,tip,.021,wood)
  for twig in [-1,1]:
   end=tip+Vector((math.cos(a+twig*.7)*.38,math.sin(a+twig*.7)*.35,.25))
   beam('LONGCUI_plum_twig',mid,end,.011,wood)
   for fraction in [.65,.95]:
    centre=mid.lerp(end,fraction)
    # Faceted five-petal rosette in a vertical plane; no foliage canopy.
    for petal in range(5):
     angle=petal*math.tau/5
     direction=Vector((math.cos(angle),0,math.sin(angle)))
     side=Vector((-math.sin(angle),0,math.cos(angle)))
     tip_p=centre+direction*.065
     mesh('LONGCUI_plum_blossom',[centre,centre+direction*.035+side*.025,tip_p,centre+direction*.035-side*.025],[(0,1,2,3)],plaster)
# Open incense bowl with a visible rim, three feet and upright incense sticks.
centre=Vector((1.6,-1.25,.72));verts=[]
for radius,z in [(.18,-.2),(.34,0),(.34,.06),(.28,.06),(.14,-.14)]:
 for k in range(16):
  a=k*math.tau/16;verts.append(centre+Vector((radius*math.cos(a),radius*math.sin(a),z)))
faces=[(j*16+k,j*16+(k+1)%16,(j+1)*16+(k+1)%16,(j+1)*16+k) for j in range(4) for k in range(16)]
mesh('LONGCUI_incense_bowl',verts,faces,gold)
for a in [0,math.tau/3,math.tau*2/3]:
 foot=centre+Vector((.18*math.cos(a),.18*math.sin(a),-.2));beam('LONGCUI_burner_foot',foot,foot+Vector((.06*math.cos(a),.06*math.sin(a),-.52)),.04,gold)
for x in [-.09,0,.09]:beam('LONGCUI_incense_stick',centre+Vector((x,0,-.13)),centre+Vector((x,0,.45)),.009,wood)
collision('longcui_burner',(1.6,-1.25,.44),(.7,.7,.88))
beam('LONGCUI_lantern_arm',(1.45,0,2.8),(1.45,-.8,2.8),.035,wood)
lantern((1.45,-.7,2.15))
sign('櫳翠庵',(0,-.37,2.6),1.7)
light('LGT_longcui-an_key',(-4,-3,5),300,(.18,1,.18),'SPOT',(0,-1,1.5))
for name,p in [('entry',(0,-2.4,0)),('closed_gate',(0,-1.1,0)),('incense',(.8,-2,0)),('return',(0,-4.4,0))]:empty('TRG_longcui_an_'+name,p,'longcui_an')
camera('CAM_longcui-an_wide',(-3,-7,2.6),(0,-.8,1.45),32)
camera('CAM_longcui-an_gate',(0,-2.8,1.65),(0,0,1.4),35)
camera('CAM_longcui-an_incense',(.3,-2.8,1.5),(1.6,-1.25,.85),40)
bpy.context.view_layer.update()
transform=Matrix.Translation((-25,-13,0)) @ Matrix.Rotation(math.pi,4,'Z')
for o in C.objects:o.matrix_world=transform @ o.matrix_world
assert len([o for o in C.objects if o.type=='LIGHT' and o.data.type=='POINT'])==1
sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children}
C=sites['stage']
for o in list(C.objects):
 if o.name.startswith(('LONGCUI_approach','COL_longcui_approach')):bpy.data.objects.remove(o,do_unlink=True)
# Branch east of the water pavilion, clear of its continuous south railing.
for p,size in [((-19.2,-2.5,-.12),(1.8,5,.24)),((-22.1,-5,-.12),(7.6,1.8,.24)),((-25,-7.9,-.12),(1.8,7.6,.24))]:
 box('LONGCUI_approach',p,size,stone);collision('longcui_approach',p,size)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for slug in ['longcui-an','stage']:
 bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{sites[slug]},fake_user=True,compress=True)
for slug in ['longcui-an','stage']:
 file=R/'blender/sites'/('SITE_'+slug+'.blend')
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
 s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
 s.camera=next((o for o in s.objects if o.type=='CAMERA'),None)
 temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('LONGCUI_ART_PASS: closed gate, two plum trees, one lantern, incense bowl, four markers')
