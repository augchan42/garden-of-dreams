"""Replace the paired-pavilion placeholder with a single closed imperial facade."""
import bpy, math, ast, os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
tree=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','gold':'bronze','black':'backstage','plaster':'whitewash','roofmat':'rooftile','crtamber':'crt_amber'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
font=next(f for f in bpy.data.fonts if 'Songti' in f.filepath)
C=next(c for c in scene.collection.children if c.name=='SITE_daguan-lou')
for o in list(C.objects):bpy.data.objects.remove(o,do_unlink=True)
box('DAGUAN_platform',(0,23.05,-.15),(14,3.5,.3),stone)
collision('daguan_floor',(0,23.05,-.15),(14,3.5,.3))
box('DAGUAN_front',(0,23,1.6),(13,.18,3.2),plaster)
collision('daguan_closed_front',(0,23,1.6),(13,.22,3.2))
box('DAGUAN_backstage',(0,24.3,1.7),(13,.18,3.4),black)
for x in [-6.5,6.5]:
 box('DAGUAN_return_wall',(x,23.6,1.6),(.18,1.4,3.2),black)
 collision('daguan_return_wall',(x,23.6,1.6),(.22,1.4,3.2))
for x in [-6.5,-3.9,-1.3,1.3,3.9,6.5]:
 cyl('DAGUAN_column',(x,22.45,1.6),.11,3.2,wood)
 cyl('DAGUAN_column_foot',(x,22.45,.15),.18,.3,stone)
 collision('daguan_column',(x,22.45,1.6),(.24,.24,3.2))
 for z,w in [(2.85,.5),(3.02,.72),(3.15,.95)]:box('DAGUAN_bracket',(x,22.45,z),(w,.6,.11),wood)
for x in [-5.2,-2.6,0,2.6,5.2]:
 raised=.45 if x==0 else 0
 for side in [-1,1]:
  px=x+side*.52
  box('DAGUAN_closed_door',(px,22.83,1.18+raised),(1.01,.14,2.36),wood)
  for z in [.55,1.5]:box('DAGUAN_recessed_panel',(px,22.746,z+raised),(.72,.025,.7),black)
  for k in range(6):
   for column in [-.33,0,.33]:cyl_o=cyl('DAGUAN_door_stud',(0,0,0),.023,.035,gold,8);cyl_o.location=(px+column,22.72,.25+k*.35+raised);cyl_o.rotation_euler.x=math.pi/2
  box('DAGUAN_door_pull',(x+side*.16,22.69,1.15+raised),(.07,.07,.18),gold)
 if abs(x)>5:
  box('DAGUAN_amber_transom',(x,22.72,2.65),(1.8,.04,.42),crtamber)
  for j in range(7):box('DAGUAN_transom_lattice',(x-.75+j*.25,22.68,2.65),(.025,.04,.45),wood)
# Ceremonial steps are deliberately outside the visitor's arrival position.
for y,z,depth in [(21.85,.15,.5),(22.2,.3,.5),(22.55,.45,.5)]:
 box('DAGUAN_central_step',(0,y,z/2),(2.3,depth,z),stone)
 collision('daguan_central_step',(0,y,z/2),(2.3,depth,z))
box('DAGUAN_upper_storey',(0,23,4.15),(9,.95,1.5),plaster)
box('DAGUAN_upper_back',(0,23.55,4.15),(9,.15,1.5),black)
for x in range(-4,5):box('DAGUAN_upper_timber',(x,22.49,4.15),(.07,.08,1.5),wood)
def roof_tier(name,levels):
 vs=[]
 for w,d,z in levels:vs.extend([(-w,23-d,z),(w,23-d,z),(w,23+d,z),(-w,23+d,z)])
 faces=[(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(len(levels)-1) for i in range(4)]
 faces.append(tuple(range((len(levels)-1)*4,len(levels)*4)))
 mesh(name,vs,faces,roofmat)
 for side in range(4):
  for j in range(len(levels)-1):beam('DAGUAN_hip',vs[j*4+side],vs[(j+1)*4+side],.055,stone)
  strips=38 if side in [0,2] else 12
  for t in range(1,strips):
   for j in range(len(levels)-1):
    a=Vector(vs[j*4+side]).lerp(Vector(vs[j*4+(side+1)%4]),t/strips)
    b=Vector(vs[(j+1)*4+side]).lerp(Vector(vs[(j+1)*4+(side+1)%4]),t/strips)
    beam('DAGUAN_tile_strip',a,b,.022,roofmat)
roof_tier('DAGUAN_lower_roof',[(7.65,2.5,3.45),(7.3,2.2,3.2),(5.6,1.35,4.35),(4.4,.35,4.9)])
roof_tier('DAGUAN_upper_roof',[(5.4,1.85,5.0),(5.05,1.55,4.8),(3.65,.8,5.65),(2.6,.06,6.3)])
beam('DAGUAN_upper_ridge',(-2.9,23,6.38),(2.9,23,6.38),.11,stone)
for x in [-2.9,2.9]:cyl('DAGUAN_ridge_finial',(x,23,6.55),.09,.35,gold)
sign('大觀樓',(0,22.0,3.05),3.8)
light('LGT_daguan-lou_key',(6,18,3),450,(.18,1,.18),'SPOT',(0,23,1.5))
for name,p in [('entry',(0,20.5,0)),('closed_doors',(0,21.3,0)),('return',(0,19,0))]:empty('TRG_daguan_lou_'+name,p,'daguan_lou')
camera('CAM_daguan-lou_wide',(7,11,3.2),(0,23,2.2),32)
camera('CAM_daguan-lou_doors',(0,19.8,1.7),(0,23,1.7),40)
assert len([o for o in C.objects if o.name.startswith('DAGUAN_closed_door')])==10
assert len([o for o in C.objects if o.name.startswith('TRG_')])==3
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_daguan-lou.blend';bpy.data.libraries.write(str(file),{C},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.camera=next(o for o in s.objects if o.name=='CAM_daguan-lou_wide')
temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('IMPERIAL_FACADE_PASS: two continuous roof tiers, five closed door bays, three markers')
