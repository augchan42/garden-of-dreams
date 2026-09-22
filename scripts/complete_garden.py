import bpy, math, random, json, ast
from pathlib import Path
from mathutils import Vector
R=Path('/Users/auchan/projects/garden-of-dreams');random.seed(1974)
scene=bpy.context.scene;sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children};C=None
# Reuse build helpers across stateless MCP calls.
tree=ast.parse((R/'scripts/build_garden.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for var,name in {'wood':'lattice_wood','plaster':'whitewash','roofmat':'rooftile','stone':'plaster_rock','black':'backstage','gold':'bronze','amber':'lantern','green':'crt_green','crtamber':'crt_amber','water':'water','foliage':'foliage_card','cycomat':'cyclorama'}.items():globals()[var]=bpy.data.materials['MAT_'+name]
font=next(f for f in bpy.data.fonts if 'Songti' in f.filepath)
C=sites['qinfang-ting']
for x in [-5.15,5.15]:
 box('KIT_water_bridge_crosswalk',(x,0,-.12),(3.5,1.8,.24),stone);collision('bridge_crosswalk',(x,0,-.12),(3.5,1.8,.24))
# Land platforms are visible stage floor, with stone walks above them.
C=sites['stage'];ground=mat('MAT_stage_canvas',(.055,.095,.037))
for y,size in [(-23,35),(25,39)]:box('KIT_stage_painted_canvas',(0,y,-.38),(86,size,.5),ground)
# plank lines in entry region
for x in range(-9,10):box('KIT_stage_floorboard_seam',(x,-39.3,.004),(.014,1.8,.008),black)
def hall(slug,title,p,w=7,depth=2,monitors=False):
 collection(slug);x,y,z=p
 box('SITE_'+slug+'_platform',(x,y,z-.15),(w+1,depth+2,.3),stone);collision(slug+'_floor',(x,y,z-.15),(w+1,depth+2,.3))
 box('SITE_'+slug+'_backstage',(x,y+depth/2,z+1.5),(w,.15,3),black)
 box('SITE_'+slug+'_front',(x,y,z+1.3),(w,.12,2.6),plaster)
 for dx in [-w/2,w/2]:box('KIT_wall_side',(x+dx,y+.5,z+1.4),(.16,depth,2.8),plaster)
 for dx in [-w*.35,0,w*.35]:
  box('KIT_wall_inset',(x+dx,y-.12,z+1.5),(1.65,.12,1.65),black)
  if monitors:
   for row in range(2):
    for col in range(2):crt((x+dx+(col-.5)*.74,y-.35,z+1.05+row*.62),True)
  else:box('KIT_wall_amber_window',(x+dx,y-.2,z+1.5),(1.4,.03,1.4),crtamber)
  for k in range(7):
   box('KIT_wall_lattice_vertical',(x+dx-.75+k*.25,y-.65,z+1.5),(.025,.035,1.6),wood)
   box('KIT_wall_lattice_horizontal',(x+dx,y-.67,z+.75+k*.25),(1.6,.035,.025),wood)
  cyl('KIT_pavilion_hall_post',(x+dx,y-.9,z+1.5),.09,3,wood)
 # two square roof sections form a broad silhouette
 for dx in [-w*.24,w*.24]:roof((x+dx,y+.15,z+2.95),w*.46,4)
 sign(title,(x,y-1.0,z+2.65),min(w*.6,4))
 for dx in [-w*.43,w*.43]:lantern((x+dx,y-.7,z+2.2),False)
 empty('TRG_'+slug.replace('-','_')+'_entry',(x,y-1.2,z),slug.replace('-','_'))
 camera('CAM_'+slug+'_wide',(x+8,y-13,z+5),(x,y,z+1.5),30)
 light('LGT_'+slug+'_key',(x+4,y-6,z+7),450,(.18,1,.18),'SPOT',(x,y,z))

# Site sheets are written before these additional models are built.
extra=[('qiushuang-zhai','秋爽齋',(22,16,0),9,True,'Long study hall; amber CRT bank recessed behind stock lattice.'),('tubi-tang','凸碧堂',(7,33,4),7,False,'Hilltop hall and stepped terrace overlooking the painted moon.'),('daguan-lou','大觀樓',(0,23,0),13,False,'Large imperial facade with black unfinished back; no interior.'),('ouxiang-xie','藕香榭',(-23,0,0),6,False,'Water pavilion reached along the western bridge walk.'),('hengwu-yuan','蘅蕪苑',(-18,18,0),7,False,'Bare rock courtyard with low herbs and no trees.'),('yihong-yuan','怡紅院',(25,-1,0),7,False,'Closed lacquer doors and amber window; future room.'),('xiaoxiang-guan','瀟湘館',(-9,-13,0),6,False,'Bamboo court around a shallow facade with a lit window.'),('longcui-an','櫳翠庵',(-25,-13,0),6,False,'Closed nunnery gate, plum trees and one lantern.'),('aojing-guan','凹晶館',(26,-12,-.65),7,False,'Water-level facade reflected in the stage pond.'),('daoxiang-cun','稻香村',(-32,22,0),6,False,'Farmhouse with thatch strips, fence and painted paddy flats.'),('ziling-zhou','紫菱洲',(-34,0,0),4,False,'Reed islet with a timber footbridge.')]
for slug,title,p,w,mon,direction in extra:
 if not (R/'docs/sites'/f'{slug}.md').exists(): (R/'docs/sites'/f'{slug}.md').write_text(f'# {title} — {slug}\n\n{direction}\n\nKey: hard green. Practicals: amber lanterns and window panels.\nAssets: stock wall, lattice, roof, lantern, stage platform; shallow facade with black back.\nTrigger: `TRG_{slug.replace("-","_")}_entry`, room_id `{slug.replace("-","_")}`.\nCamera: `CAM_{slug}_wide`, 2.35:1, 30 mm establishing view.\n\nReference direction: the master spec’s Shaw Brothers night exterior, flat-front construction, and tech-noir palette. External stills have not been collected.\n\nStatus: modelled first art pass; material atlas, painted signage and final light bake pending.\n')
 hall(slug,title,p,w,2,mon)
 if slug=='tubi-tang':
  for i in range(5):rock((p[0]+random.uniform(-4,4),p[1]+random.uniform(-2,2),-.3),(2.5,2,4.2))
  for i in range(16):
   box('HERO_tubi_terrace_stair',(7,21+i*.55,i*.25-.12),(2.2,.58,.25),stone);collision('tubi_step',(7,21+i*.55,i*.25-.12),(2.2,.58,.25))
 if slug=='hengwu-yuan':
  for i in range(7):rock((-22+i*1.1,14+random.random()*2,0),(.5,.6,random.uniform(.5,1.5)))
 if slug=='xiaoxiang-guan':
  for i in range(5):bamboo((-13+i*2,-15,0),6)
 if slug in ['longcui-an','ouxiang-xie']:
  for dx in [-4,4]:
   x,y,z=p;beam('KIT_flora_tree_trunk',(x+dx,y,0),(x+dx+.4,y,3.5),.13,wood)
   for j in range(5):
    a=j*math.tau/5;end=(x+dx+math.cos(a)*1.5,y+math.sin(a)*1.5,3+random.random())
    beam('KIT_flora_tree_branch',(x+dx+.3,y,2),end,.035,wood)
    for k in range(4):
     q=(end[0]+random.uniform(-.6,.6),end[1]+random.uniform(-.6,.6),end[2]+random.uniform(-.3,.3))
     mesh('KIT_flora_tree_leaf',[(q[0]-.3,q[1],q[2]),(q[0],q[1]-.2,q[2]+.2),(q[0]+.3,q[1],q[2]),(q[0],q[1]+.2,q[2]-.2)],[(0,1,2,3)],foliage)
 if slug=='ziling-zhou':
  for i in range(40):
   x=p[0]+random.uniform(-3,3);y=random.uniform(-3,3);beam('KIT_flora_reed',(x,y,-.5),(x+.2,y,random.uniform(.5,1.4)),.02,foliage)
 if slug=='daoxiang-cun':
  for j in range(35):beam('KIT_flora_thatch',(-36+j*.23,21,3.3),(-36+j*.23,19.8,2.8),.05,gold)
  rail((-36,18,0),(-28,18,0))
# Connecting stone paths, authored to the master map.
C=sites['stage']
for a,b in [((-19,0),(-34,0)),((-18,0),(-18,18)),((-18,18),(-32,22)),((0,17),(22,17)),((19,0),(25,0)),((25,0),(25,-12)),((0,-13),(-25,-13)),((0,19),(0,23))]:
 av=Vector((*a,0));bv=Vector((*b,0));d=bv-av;o=box('KIT_water_stone_walk',(0,0,-.12),(1.8,d.length,.24),stone);o.location=(av+bv)/2;o.rotation_euler.z=-math.atan2(d.x,d.y)
 c=collision('stone_walk',(0,0,-.12),(1.8,d.length,.24));c.location=o.location;c.rotation_euler=o.rotation_euler
# Save all scene dependencies without writing the unrelated open project.
scene['build_status']='First modelled art pass; see docs/build-status.md for spec gaps'
bpy.data.libraries.write(str(R/'blender/master.blend'),{scene},fake_user=True,compress=True)
print('Garden assembled',len(scene.objects),'objects',len(sites),'collections')
