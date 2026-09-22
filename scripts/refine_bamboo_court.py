"""Build Xiaoxiang’s closed bamboo courtyard and single amber window."""
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
C=next(c for c in scene.collection.children if c.name=='SITE_xiaoxiang-guan')
for o in list(C.objects):bpy.data.objects.remove(o,do_unlink=True)
# Local facade faces -Y; rotate toward the central garden spine.
box('XIAOXIANG_paving',(0,-1.8,-.12),(6.8,5.4,.24),stone)
collision('xiaoxiang_floor',(0,-1.8,-.12),(6.8,5.4,.24))
box('XIAOXIANG_closed_front',(0,0,1.3),(6,.2,2.6),plaster)
collision('xiaoxiang_closed_front',(0,0,1.3),(6,.24,2.6))
box('XIAOXIANG_black_back',(0,1,1.3),(6,.2,2.6),black)
for x in [-3,3]:
 box('XIAOXIANG_return',(x,.5,1.3),(.2,1.2,2.6),plaster)
 collision('xiaoxiang_return',(x,.5,1.3),(.24,1.2,2.6))
box('XIAOXIANG_wall_cap',(0,0,2.68),(6.5,.6,.16),roofmat)
for x in [-1.22,-.48]:
 box('XIAOXIANG_gate_leaf',(x,-.17,1.05),(.71,.16,2.1),wood)
 for z in [.25,1.05,1.9]:box('XIAOXIANG_gate_rail',(x,-.28,z),(.7,.08,.07),black)
 box('XIAOXIANG_gate_pull',(-.85+(x+.85)*.35,-.3,1.05),(.05,.07,.17),gold)
for x in [-1.66,-.04]:box('XIAOXIANG_gate_jamb',(x,-.23,1.1),(.13,.3,2.2),wood)
box('XIAOXIANG_gate_head',(-.85,-.23,2.2),(1.9,.4,.17),wood)
box('XIAOXIANG_threshold',(-.85,-.28,.055),(1.75,.6,.11),stone)
collision('xiaoxiang_threshold',(-.85,-.28,.055),(1.75,.6,.11))
# One continuous shallow pitched roof, open black backing beneath the eaves.
vs=[(-3.4,-.55,2.65),(3.4,-.55,2.65),(-3.2,.45,3.25),(3.2,.45,3.25),(-3.4,1.35,2.65),(3.4,1.35,2.65)]
mesh('XIAOXIANG_roof',vs,[(0,1,3,2),(2,3,5,4)],roofmat)
beam('XIAOXIANG_ridge',(-3.35,.45,3.28),(3.35,.45,3.28),.065,stone)
for i in range(35):
 x=-3.3+i*6.6/34
 beam('XIAOXIANG_tiles',(x,-.55,2.66),(x*.95,.45,3.26),.022,roofmat)
 beam('XIAOXIANG_tiles',(x*.95,.45,3.26),(x,1.35,2.66),.022,roofmat)
box('XIAOXIANG_amber_window',(1.65,-.125,1.6),(1.25,.05,1.15),crtamber)
for x in [1,1.32,1.65,1.98,2.3]:box('XIAOXIANG_window_lattice',(x,-.18,1.6),(.035,.08,1.25),wood)
for z in [1,1.4,1.8,2.2]:box('XIAOXIANG_window_lattice',(1.65,-.18,z),(1.35,.08,.035),wood)
light('LGT_xiaoxiang_window',(1.65,-.7,1.7),65,(1,.38,.005))
# Three explicit stalk sizes, separated into clumps around a 1.8 m clear aisle.
for clump,(cx,cy) in enumerate([(-2.15,-1.3),(2.4,-1.1),(-2.3,-3.3),(2.5,-3.3)]):
 box('XIAOXIANG_bamboo_bed',(cx,cy,.04),(1.1,.95,.08),black)
 collision('xiaoxiang_bamboo_bed',(cx,cy,.3),(1.1,.95,.6))
 for stalk in range(3):
  height=[2.5,3.5,4.5][stalk];px=cx+(stalk-1)*.28;py=cy+(.16 if stalk==1 else -.16)
  top=Vector((px+.13,py+.07,height));bottom=Vector((px,py,.08))
  beam('XIAOXIANG_bamboo_stem',bottom,top,.035,foliage)
  for j in range(1,int(height/.35)):
   centre=bottom.lerp(top,j*.35/height)
   cyl('XIAOXIANG_bamboo_node',centre,.045,.045,wood,8)
  for level in [0.52,.72,.9]:
   anchor=bottom.lerp(top,level)
   a=stalk*1.8+clump*.8+level*3
   direction=Vector((math.cos(a),math.sin(a),.35))
   end=anchor+direction*.6
   beam('XIAOXIANG_bamboo_branch',anchor,end,.012,wood)
   for k in range(5):
    p=anchor.lerp(end,.25+k*.15)
    angle=a+(-1 if k%2 else 1)*.65
    d=Vector((math.cos(angle),math.sin(angle),.2));side=Vector((-math.sin(angle),math.cos(angle),0))
    length=.34+.06*(k%3)
    mesh('XIAOXIANG_bamboo_leaf',[p,p+d*length*.45+side*.055,p+d*length,p+d*length*.45-side*.055],[(0,1,2,3)],foliage)
for y in [-3.8,-3,-2.2,-1.4]:box('XIAOXIANG_path_slab',(0,y,.01),(1.8,.72,.02),stone)
sign('瀟湘館',(-.85,-.32,2.5),1.75)
light('LGT_xiaoxiang-guan_key',(-4,-3,5),450,(.18,1,.18),'SPOT',(0,-1,1.4))
for name,p in [('entry',(0,-2.4,0)),('closed_gate',(-.85,-1.1,0)),('bamboo',(0,-3.4,0)),('return',(0,-4.4,0))]:empty('TRG_xiaoxiang_guan_'+name,p,'xiaoxiang_guan')
camera('CAM_xiaoxiang-guan_wide',(0,-7,2.3),(.5,-.2,1.6),32)
camera('CAM_xiaoxiang-guan_gate',(-.85,-2.6,1.6),(-.85,0,1.4),35)
camera('CAM_xiaoxiang-guan_bamboo',(0,-4.2,2.4),(1.7,-1,2),35)
bpy.context.view_layer.update()
transform=Matrix.Translation((-9,-13,0)) @ Matrix.Rotation(math.pi/2,4,'Z')
for o in C.objects:o.matrix_world=transform @ o.matrix_world
assert len([o for o in C.objects if o.name.startswith('XIAOXIANG_amber_window')])==1
assert len([o for o in C.objects if o.name.startswith('XIAOXIANG_bamboo_stem')])==12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_xiaoxiang-guan.blend';bpy.data.libraries.write(str(file),{C},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.camera=next(o for o in s.objects if o.name=='CAM_xiaoxiang-guan_wide')
temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('XIAOXIANG_ART_PASS: closed gate, one window, twelve stalks in three sizes, four markers')
