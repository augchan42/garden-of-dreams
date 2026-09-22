"""Replace only the western water-pavilion and island collections in authoring.blend."""
import bpy, math, random, ast, json, os
from pathlib import Path
from mathutils import Vector
R=Path('/Users/auchan/projects/garden-of-dreams')
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
random.seed(7412)
tree=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','plaster':'whitewash','roofmat':'rooftile','stone':'plaster_rock','black':'backstage','gold':'bronze','amber':'lantern','green':'crt_green','crtamber':'crt_amber','water':'water','foliage':'foliage_card','cycomat':'cyclorama'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
font=next(f for f in bpy.data.fonts if 'Songti' in f.filepath)
sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children}
for slug in ['ouxiang-xie','ziling-zhou']:
 for obj in list(sites[slug].objects):bpy.data.objects.remove(obj,do_unlink=True)
# Remove the old continuous slab where the timber approach and bridge now stand.
for o in list(sites['stage'].objects):
 if o.name.startswith(('KIT_water_stone_walk','COL_stone_walk')) and abs(o.location.x+26.5)<.02 and abs(o.location.y)<.02:
  bpy.data.objects.remove(o,do_unlink=True)
C=sites['ouxiang-xie']
# Open rectangular pavilion with a clear east-west aisle, not a closed hall.
box('SITE_ouxiang_deck',(-23,0,-.13),(6,5,.26),wood)
collision('ouxiang_deck',(-23,0,-.13),(6,5,.26))
for x in [-25.55,-20.45]:
 for y in [-2.05,2.05]:
  cyl('KIT_pavilion_water_post',(x,y,1.55),.11,3.1,wood)
  cyl('KIT_pavilion_water_pier',(x,y,-.5),.17,1.3,stone)
  box('KIT_pavilion_water_bracket',(x,y,2.92),(.65,.55,.13),wood)
  collision('ouxiang_post',(x,y,1.5),(.24,.24,3))
# A hipped roof whose corners line up with the rectangular deck.
levels=[(3.45,2.95,3.32),(3.12,2.64,3.08),(2.0,1.64,3.68),(.95,.42,4.4)]
vs=[]
for w,d,z in levels:
 vs.extend([(-23-w,-d,z),(-23+w,-d,z),(-23+w,d,z),(-23-w,d,z)])
fs=[(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(3) for i in range(4)]
fs.append((12,13,14,15))
mesh('KIT_pavilion_water_hipped_roof',vs,fs,roofmat)
for side in range(4):
 for level in range(3):
  beam('KIT_pavilion_water_hip',vs[level*4+side],vs[(level+1)*4+side],.05,stone)
 for t in range(1,15):
  u=t/15;k=(side+1)%4
  for j in range(3):
   beam('KIT_pavilion_water_tiles',Vector(vs[j*4+side]).lerp(Vector(vs[j*4+k]),u),Vector(vs[(j+1)*4+side]).lerp(Vector(vs[(j+1)*4+k]),u),.018,roofmat)
beam('KIT_pavilion_water_ridge',(-24.15,0,4.48),(-21.85,0,4.48),.09,stone)
# Bracket beams and continuous north/south rails; east/west doors stay open.
for y in [-2.05,2.05]:beam('KIT_pavilion_water_beam',(-25.55,y,2.9),(-20.45,y,2.9),.09,wood)
for y in [-2.4,2.4]:
 rail((-25.8,y,0),(-20.2,y,0))
 collision('ouxiang_rail',(-23,y,.5),(5.6,.1,1))
 box('KIT_pavilion_meirenkao_seat',(-23,y*.85,.46),(4.5,.32,.09),wood)
for x in [-25.85,-20.15]:
 for y in [-1.7,1.7]:
  rail((x,y-.55,0),(x,y+.55,0))
  collision('ouxiang_side_rail',(x,y,.5),(.1,1.1,1))
for x in [-25,-21]:lantern((x,0,2.3))
# Table and seating kept north of the through aisle.
box('SITE_ouxiang_tea_table',(-23,1.12,.73),(1.7,.72,.12),wood)
for x in [-23.65,-22.35]:box('KIT_props_tea_table_leg',(x,1.12,.35),(.1,.5,.7),wood)
collision('ouxiang_table',(-23,1.12,.4),(1.7,.72,.8))
for x,y in [(-24.2,.9),(-21.8,.9),(-24.2,1.65),(-21.8,1.65),(-23.5,1.95),(-22.5,1.95)]:
 cyl('KIT_props_tea_stool',(x,y,.23),.22,.46,stone)
for i in range(6):
 cyl('KIT_props_tea_cup',(-23.65+i*.26,1.12,.84),.045,.09,gold,10)
cyl('KIT_props_teapot',(-23,1.35,.9),.11,.19,stone,12)
beam('KIT_props_teapot_spout',(-22.91,1.35,.92),(-22.8,1.35,.99),.035,stone)
# Short deck links the existing western corridor to the pavilion.
box('KIT_water_pavilion_approach',(-19.5,0,-.1),(1.05,1.8,.2),wood)
collision('ouxiang_approach',(-19.5,0,-.1),(1.05,1.8,.2))
for i in range(25):
 x=random.uniform(-27,-19);y=random.choice([-1,1])*random.uniform(2.7,4.5)
 cyl('KIT_water_ouxiang_lotus',(x,y,-1.065),random.uniform(.15,.35),.015,foliage,10)
for name,p in [('entry',(-20,0,0)),('table',(-23,.3,0)),('water_rail',(-23,-2,0)),('return',(-19.2,0,0))]:empty('TRG_ouxiang_xie_'+name,p,'ouxiang_xie')
camera('CAM_ouxiang-xie_wide',(-14,-12,5.4),(-23,0,1.8),32)
camera('CAM_ouxiang-xie_table',(-19.3,-.2,1.7),(-23,1.1,.9),32)
C=sites['ziling-zhou']
# Low irregular island; no house or roof.
n=24;outline=[]
for i in range(n):
 a=math.tau*i/n;outline.append((-34+3.5*math.cos(a)*(1+.04*math.sin(5*a)),2.5*math.sin(a),-.08))
vs=outline+[(x,y,-1.35) for x,y,z in outline]
mesh('SITE_ziling_island',vs,[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],stone)
# Walking landing at bridge level.
box('SITE_ziling_stone_landing',(-33.8,0,-.08),(5.6,1.8,.16),stone)
collision('ziling_landing',(-33.8,0,-.08),(5.6,1.8,.16))
# Timber bridge with stock rails and individually visible boards.
for i in range(23):
 x=-31+i*(5/22)
 box('KIT_water_footbridge_plank',(x,0,-.045),(.215,1.8,.09),wood)
collision('ziling_footbridge',(-28.5,0,-.1),(5.2,1.8,.2))
for y in [-.88,.88]:
 rail((-31.1,y,0),(-25.9,y,0))
 collision('ziling_bridge_rail',(-28.5,y,.5),(5.2,.08,1))
 for x in [-31,-29.3,-27.6,-26]:
  beam('KIT_water_footbridge_pile',(x,y,-1.2),(x,y,1),.055,wood)
for i in range(85):
 a=random.uniform(0,math.tau);r=random.uniform(.65,.97)
 x=-34+3.4*r*math.cos(a);y=2.35*r*math.sin(a)
 if abs(y)<1.05:continue
 h=random.uniform(.8,1.6);tip=(x+.12,y+.06,h-.08)
 beam('KIT_flora_ziling_reed',(x,y,-.08),tip,.016,foliage)
 beam('KIT_flora_ziling_seedhead',tip,(tip[0],tip[1],tip[2]+.13),.036,gold)
 for side in [-1,1]:mesh('KIT_flora_ziling_reed_leaf',[(x,y,h*.4),(x+side*.3,y-.035,h*.7),(x+side*.5,y,h*.73),(x+side*.25,y+.035,h*.5)],[(0,1,2,3)],foliage)
for i in range(14):
 a=i*math.tau/14
 if abs(math.sin(a))<.35:continue
 rock((-34+3.25*math.cos(a),2.32*math.sin(a),-.3),(.25,.22,.38))
for x,y in [(-37.5,1.7),(-36.7,-2.6),(-32.8,2.8),(-31.5,-2.3)]:cyl('KIT_water_ziling_lotus',(x,y,-1.06),.25,.015,foliage,10)
for name,p in [('entry',(-31.1,0,0)),('overlook',(-35.4,0,0)),('return',(-26.3,0,0))]:empty('TRG_ziling_zhou_'+name,p,'ziling_zhou')
camera('CAM_ziling-zhou_wide',(-41,-8,3.1),(-33,0,.5),32)
camera('CAM_ziling-zhou_reeds',(-35.6,-.5,1.6),(-26,0,1.2),40)
scene.camera=next(o for o in sites['ouxiang-xie'].objects if o.name=='CAM_ouxiang-xie_wide')
# Validate the scene contracts before packaging.
assert sum(o.name.startswith('KIT_props_tea_stool') for o in sites['ouxiang-xie'].objects)==6
assert sum(o.name.startswith('KIT_props_lantern_paper') for o in sites['ouxiang-xie'].objects)==2
assert not any('roof' in o.name.lower() or '_front' in o.name for o in sites['ziling-zhou'].objects)
assert len([o for o in sites['ouxiang-xie'].objects if o.name.startswith('TRG_')])==4
assert len([o for o in sites['ziling-zhou'].objects if o.name.startswith('TRG_')])==3
scene.render.resolution_x=1410;scene.render.resolution_y=600;scene.render.resolution_percentage=100
for slug in ['ouxiang-xie','ziling-zhou']:
 scene.camera=next(o for o in sites[slug].objects if o.name=='CAM_'+slug+'_wide')
 scene.render.filepath=str(R/'docs/reference'/(slug+'-raw.png'));bpy.ops.render.render(write_still=True)
scene.camera=next(o for o in sites['qinfang-ting'].objects if o.name=='CAM_stage_wide')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
changed=['ouxiang-xie','ziling-zhou','stage']
# The linked master reads these three files; all other site files remain unchanged.
for slug in changed:bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{sites[slug]},fake_user=True,compress=True)
for slug in changed:
 file=R/'blender/sites'/('SITE_'+slug+'.blend')
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
 s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC';s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1410;s.render.resolution_y=600
 s.camera=next((o for o in s.objects if o.type=='CAMERA'),None)
 temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('WESTERN_SITES_PASS: open pavilion, 6 seats, 2 lanterns, island without hall, named markers; authoring and 3 linked libraries saved')
