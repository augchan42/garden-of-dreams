"""Build Hengwu's enclosed stone/herb court without trees."""
import bpy, bmesh, math, random, ast, os, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
tree=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','stone':'plaster_rock','gold':'bronze','black':'backstage','amber':'lantern','plaster':'whitewash','foliage':'foliage_card','roofmat':'rooftile'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children}
C=sites['hengwu-yuan'];random.seed(7433)
for o in list(C.objects):
 if o.name.startswith(('HENGWU_','COL_hengwu_','KIT_rockery_','TRG_hengwu_yuan_','CAM_hengwu-yuan_','KIT_props_lantern_','LGT_lantern')):
  bpy.data.objects.remove(o,do_unlink=True)
box('HENGWU_court_paving',(-18,14,-.12),(9,8,.24),stone)
collision('hengwu_court',(-18,14,-.12),(9,8,.24))
collision('hengwu_closed_hall',(-18,18,1.3),(7,.18,2.6))
for x in [-20.45,-18,-15.55]:collision('hengwu_hall_post',(x,17.1,1.5),(.2,.2,3))
# Side walls have genuine openings, filled by crossed timber lattice.
for x in [-22.5,-13.5]:
 for y,span in [(11.6,3.2),(16.6,2.8)]:box('HENGWU_side_wall',(x,y,1.1),(.18,span,2.2),plaster)
 for z,h in [(.35,.7),(2.05,.3)]:box('HENGWU_window_spandrel',(x,14.2,z),(.18,2,.7 if z==.35 else h),plaster)
 for y in [13.3,15.1]:box('HENGWU_window_jamb',(x,y,1.3),(.2,.1,1.3),wood)
 for z in [.7,1.9]:box('HENGWU_window_frame',(x,14.2,z),(.2,1.9,.09),wood)
 for y in [13.5,13.9,14.3,14.7]:
  beam('HENGWU_leak_lattice',(x,y,.75),(x,min(y+.6,15.05),1.85),.018,wood)
  beam('HENGWU_leak_lattice',(x,y,1.85),(x,min(y+.6,15.05),.75),.018,wood)
 box('HENGWU_side_cap',(x,14,2.24),(.36,8.2,.15),roofmat)
 collision('hengwu_side_wall',(x,14,1.1),(.22,8,2.2))
for x in [-20.8,-15.2]:
 box('HENGWU_front_wall',(x,10,1.1),(3.4,.18,2.2),plaster)
 box('HENGWU_front_cap',(x,10,2.24),(3.6,.36,.15),roofmat)
 collision('hengwu_front_wall',(x,10,1.1),(3.4,.22,2.2))
for x in [-19.12,-16.88]:box('HENGWU_entry_jamb',(x,10,1.2),(.2,.32,2.4),wood)
box('HENGWU_entry_lintel',(-18,10,2.4),(2.5,.4,.18),wood)
# Thin slab seams keep the court bare and maintain a clear central aisle.
for x in [-21,-19.5,-18,-16.5,-15]:box('HENGWU_paving_joint',(x,14,.003),(.012,7.7,.006),black)
for y in [11.5,13,14.5,16]:box('HENGWU_paving_joint',(-18,y,.003),(8.7,.012,.006),black)
holes=[]
for rock_index,(cx,cy,height,width) in enumerate([(-15.4,12.5,2.8,1.05),(-21,11.8,1.8,.75),(-14.9,16,1.4,.65)]):
 n=16;levels=9;vs=[]
 for j in range(levels):
  z=height*j/(levels-1)
  factor=.7+.23*math.sin(j*1.3)+.06*math.cos(j*2.1)
  for k in range(n):
   a=k*math.tau/n;irregular=1+.09*math.sin(k*3+j)
   vs.append((cx+width*factor*math.cos(a)*irregular,cy+.55*factor*math.sin(a)*irregular,z))
 faces=[tuple(reversed(range(n))),tuple(range((levels-1)*n,levels*n))]+[(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(levels-1) for k in range(n)]
 rock_object=mesh('HENGWU_perforated_rock',vs,faces,stone)
 bm=bmesh.new();bm.from_mesh(rock_object.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(rock_object.data);bm.free()
 centers=[]
 for h,offset in [(.3,-.12),(.57,.16),(.8,-.1)]:
  radius=height*.09;center=Vector((cx+offset*width,cy,height*h))
  cutter=cyl('HENGWU_temporary_cutter',(0,0,0),radius,3,None,24)
  cutter.location=center;cutter.rotation_euler.x=math.pi/2;cutter.scale.x=1.15
  mod=rock_object.modifiers.new('Pierced plaster','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.context.view_layer.objects.active=rock_object
  bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.data.objects.remove(cutter,do_unlink=True);centers.append(center)
 bpy.context.view_layer.update()
 tree=BVHTree.FromObject(rock_object,bpy.context.evaluated_depsgraph_get())
 for center in centers:
  hit=tree.ray_cast(center-Vector((0,2,0)),Vector((0,1,0)),4)[0]
  assert hit is None,'Blocked rock perforation'
  holes.append(list(center))
 collision('hengwu_rock',(cx,cy,height/2),(width*1.9,1.15,height))
# Low planted pockets, deliberately below the stone silhouettes.
for x,y,w,d in [(-21.7,14.5,.8,3),(-14.3,14.2,.8,1.5),(-20.5,16.4,1.6,.65)]:
 box('HENGWU_herb_bed',(x,y,.06),(w,d,.12),black)
 for i in range(24):
  px=x+random.uniform(-w*.43,w*.43);py=y+random.uniform(-d*.43,d*.43);height=random.uniform(.12,.32)
  for a in [0,math.pi/2]:
   dx=.11*math.cos(a);dy=.11*math.sin(a)
   mesh('HENGWU_herb_leaf',[(px-dx,py-dy,.12),(px,py,height+.12),(px+dx,py+dy,.12)],[(0,1,2)],foliage)
box('HENGWU_study_table',(-20,14.7,.77),(1.8,1.15,.12),stone)
for x in [-20.65,-19.35]:box('HENGWU_table_leg',(x,14.7,.36),(.2,.7,.72),stone)
collision('hengwu_table',(-20,14.7,.43),(1.8,1.15,.86))
for x,y in [(-21.3,14.7),(-18.7,14.7),(-20,13.55),(-20,15.85)]:
 cyl('HENGWU_study_stool',(x,y,.23),.24,.46,stone)
 collision('hengwu_stool',(x,y,.23),(.48,.48,.46))
box('HENGWU_open_book',(-20,14.7,.87),(.65,.46,.07),plaster)
box('HENGWU_book_spine',(-20,14.7,.91),(.018,.46,.01),black)
for x in [-20.16,-19.84]:
 for i in range(5):box('HENGWU_book_ink',(x,14.54+i*.07,.911),(.22,.012,.008),black)
lantern((-18,17.25,2.2))
for name,p in [('entry',(-18,11,0)),('study_table',(-18,14.7,0)),('rocks',(-17,12.5,0)),('return',(-18,9,0))]:empty('TRG_hengwu_yuan_'+name,p,'hengwu_yuan')
camera('CAM_hengwu-yuan_wide',(-17.5,10.5,2.6),(-18,15.2,1.1),24)
camera('CAM_hengwu-yuan_table',(-18,13.4,1.8),(-20,14.7,.85),35)
camera('CAM_hengwu-yuan_rocks',(-17.4,10.8,1.6),(-15.4,12.5,1.35),35)
C=sites['stage']
for o in list(C.objects):
 if o.name.startswith(('HENGWU_approach','COL_hengwu_approach')):bpy.data.objects.remove(o,do_unlink=True)
# Branch just beyond the covered walk's end, avoiding its north balustrade.
for p,size in [((-19.5,1.5,-.12),(1.8,3,.24)),((-18.75,3,-.12),(3.3,1.8,.24))]:
 box('HENGWU_approach',p,size,stone);collision('hengwu_approach',p,size)
assert len(holes)==9
(R/'export/hengwu-perforation-check.json').write_text(json.dumps({'open_holes':holes,'method':'BVH rays through each boolean hole centre along the front-back axis'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for slug in ['hengwu-yuan','stage']:
 bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{sites[slug]},fake_user=True,compress=True)
for slug in ['hengwu-yuan','stage']:
 file=R/'blender/sites'/('SITE_'+slug+'.blend')
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
 s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
 s.camera=next((o for o in s.objects if o.type=='CAMERA'),None)
 temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('HENGWU_ART_PASS: enclosed courtyard, nine open rock perforations, herbs, study table, four markers')
