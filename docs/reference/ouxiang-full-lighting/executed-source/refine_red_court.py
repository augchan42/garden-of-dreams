"""Replace Yihong's generic hall with a closed lacquer court and banana plants."""
import bpy, math, ast, os
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
tree=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','gold':'bronze','black':'backstage','plaster':'whitewash','roofmat':'rooftile','crtamber':'crt_amber','foliage':'foliage_card'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
font=next(f for f in bpy.data.fonts if 'Songti' in f.filepath)
C=next(c for c in scene.collection.children if c.name=='SITE_yihong-yuan')
for o in list(C.objects):bpy.data.objects.remove(o,do_unlink=True)
lacquer=bpy.data.materials.get('MAT_yihong_lacquer') or mat('MAT_yihong_lacquer',(.25,.065,.025),.28)
# Local front faces -Y; rotate the complete site westward after construction.
box('YIHONG_paving',(0,-1.6,-.12),(7.6,5.4,.24),stone)
collision('yihong_floor',(0,-1.6,-.12),(7.6,5.4,.24))
box('YIHONG_closed_front',(0,0,1.3),(7,.2,2.6),lacquer)
collision('yihong_closed_front',(0,0,1.3),(7,.24,2.6))
box('YIHONG_backstage',(0,1,1.3),(7,.2,2.6),black)
for x in [-3.5,3.5]:
 box('YIHONG_side_return',(x,.5,1.3),(.2,1.2,2.6),lacquer)
 collision('yihong_side_return',(x,.5,1.3),(.24,1.2,2.6))
 box('YIHONG_court_side',(x,-1.5,.55),(.22,3,1.1),lacquer)
 box('YIHONG_court_cap',(x,-1.5,1.14),(.36,3.1,.13),roofmat)
 collision('yihong_court_side',(x,-1.5,.55),(.26,3,1.1))
box('YIHONG_wall_cap',(0,0,2.68),(7.5,.7,.16),roofmat)
box('YIHONG_stone_threshold',(0,-.32,.075),(2.15,.55,.15),stone)
collision('yihong_threshold',(0,-.32,.075),(2.15,.55,.15))
for x in [-.48,.48]:
 box('YIHONG_closed_door',(x,-.16,1.1),(.93,.14,2.0),lacquer)
 for z in [.65,1.6]:box('YIHONG_door_panel',(x,-.24,z),(.69,.045,.66),wood)
 for z in [.18,1.1,2.05]:box('YIHONG_door_rail',(x,-.28,z),(.95,.08,.065),gold)
 box('YIHONG_door_pull',(x*.35,-.34,1.08),(.065,.07,.19),gold)
for x in [-1.08,1.08]:box('YIHONG_door_jamb',(x,-.22,1.12),(.16,.34,2.24),wood)
box('YIHONG_door_head',(0,-.22,2.2),(2.32,.4,.18),wood)
# A low rectangular gate roof distinguishes this court from the pavilion halls.
vs=[(-1.6,-.85,2.47),(1.6,-.85,2.47),(-1.4,-.15,3.06),(1.4,-.15,3.06),(-1.6,.5,2.47),(1.6,.5,2.47)]
mesh('YIHONG_gate_roof',vs,[(0,1,3,2),(2,3,5,4)],roofmat)
beam('YIHONG_ridge',(-1.55,-.15,3.08),(1.55,-.15,3.08),.075,stone)
for x in [-1.5+i*.15 for i in range(21)]:
 beam('YIHONG_roof_tile',(x,-.85,2.48),(x*.9,-.15,3.07),.022,roofmat)
 beam('YIHONG_roof_tile',(x*.9,-.15,3.07),(x,.5,2.48),.022,roofmat)
# Exactly one lit window, with amber spill over the adjacent lacquer.
box('YIHONG_amber_window',(2.3,-.125,1.55),(1.0,.05,1.1),crtamber)
for x in [1.77,2.03,2.3,2.57,2.83]:box('YIHONG_window_lattice',(x,-.18,1.55),(.04,.07,1.18),wood)
for z in [.98,1.35,1.72,2.12]:box('YIHONG_window_lattice',(2.3,-.18,z),(1.1,.07,.04),wood)
light('LGT_yihong_window',(2.3,-.65,1.7),65,(1,.38,.005))
# Broad curved leaves with a raised midrib and pointed drooping tips.
for plant,(px,py,height) in enumerate([(-2.45,-1.35,2.15),(2.7,-2.35,1.65)]):
 cyl('YIHONG_banana_planter',(px,py,.2),.46,.4,stone)
 collision('yihong_planter',(px,py,.3),(.95,.95,.6))
 beam('YIHONG_banana_trunk',(px,py,.4),(px+.08,py,height),.09,foliage)
 for leaf in range(7):
  a=leaf*math.tau/7+plant*.5;length=1.15+.25*(leaf%3);base=Vector((px+.08,py,height-.12*(leaf%3)))
  direction=Vector((math.cos(a),math.sin(a),0));side=Vector((-math.sin(a),math.cos(a),0));vertices=[];centres=[]
  for j in range(9):
   t=j/8;centre=base+direction*(length*t)+Vector((0,0,.65*math.sin(math.pi*t)-.48*t*t));centres.append(centre)
   width=.34*math.sin(math.pi*t)**.7
   vertices.extend([centre-side*width-Vector((0,0,width*.15)),centre+Vector((0,0,.035*math.sin(math.pi*t))),centre+side*width-Vector((0,0,width*.15))])
  faces=[]
  for j in range(8):
   for k in range(2):faces.append((j*3+k,(j+1)*3+k,(j+1)*3+k+1,j*3+k+1))
  mesh('YIHONG_banana_leaf',vertices,faces,foliage)
  for j in range(8):beam('YIHONG_banana_midrib',centres[j],centres[j+1],.012,wood)
sign('怡紅院',(0,-.37,2.52),1.8)
light('LGT_yihong-yuan_key',(3,-4,5),450,(.18,1,.18),'SPOT',(0,-.5,1))
for name,p in [('entry',(0,-2.4,0)),('closed_doors',(0,-1.1,0)),('banana_leaves',(-1.2,-2,0)),('return',(0,-4,0))]:empty('TRG_yihong_yuan_'+name,p,'yihong_yuan')
camera('CAM_yihong-yuan_wide',(4,-7,3.1),(0,-.7,1.25),32)
camera('CAM_yihong-yuan_doors',(0,-2.8,1.65),(0,0,1.4),35)
camera('CAM_yihong-yuan_leaves',(-.5,-3.5,2.3),(-2.45,-1.35,1.7),35)
bpy.context.view_layer.update()
transform=Matrix.Translation((25,-1,0)) @ Matrix.Rotation(-math.pi/2,4,'Z')
for o in C.objects:o.matrix_world=transform @ o.matrix_world
assert len([o for o in C.objects if o.name.startswith('YIHONG_banana_leaf')])==14
assert len([o for o in C.objects if o.name.startswith('YIHONG_amber_window')])==1
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_yihong-yuan.blend';bpy.data.libraries.write(str(file),{C},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.camera=next(o for o in s.objects if o.name=='CAM_yihong-yuan_wide')
temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('YIHONG_ART_PASS: paired closed lacquer doors, one window, fourteen banana leaves, four markers')
