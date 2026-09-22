"""Run inside Blender through MCP. Builds an independent scene; never clears other projects."""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
R=Path('/Users/auchan/projects/garden-of-dreams')
random.seed(74)
scene=bpy.data.scenes.new('Garden of Dreams — 大觀園')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1410; scene.render.resolution_y=600; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
world=bpy.data.worlds.new('GOD_black_stage'); world.use_nodes=True
next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.025,.045,.022,1)
next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.3
scene.world=world
C=None
sites={}
def collection(slug):
 global C
 C=bpy.data.collections.new('SITE_'+slug); scene.collection.children.link(C); sites[slug]=C
 return C
def mesh(name,vs,fs,mat):
 m=bpy.data.meshes.new(name); m.from_pydata(vs,[],fs); m.update()
 o=bpy.data.objects.new(name,m); C.objects.link(o)
 if mat:m.materials.append(mat)
 return o
def mat(name,col,rough=.7,em=0):
 m=bpy.data.materials.new(name); m.use_nodes=True; m.diffuse_color=(*col,1)
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
 p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=em
 return m
wood=mat('MAT_lattice_wood',(.045,.07,.025)); plaster=mat('MAT_whitewash',(.3,.39,.23))
roofmat=mat('MAT_rooftile',(.025,.06,.035),.43); stone=mat('MAT_plaster_rock',(.15,.24,.12),.35)
black=mat('MAT_backstage',(.001,.002,.001)); gold=mat('MAT_bronze',(.45,.23,.025),.4)
amber=mat('MAT_lantern',(1,.375,.005),.5,3); green=mat('MAT_crt_green',(.027,.51,.027),.35,4)
crtamber=mat('MAT_crt_amber',(1,.375,.005),.4,3)
water=mat('MAT_water',(.014,.07,.028),.15); foliage=mat('MAT_foliage_card',(.035,.19,.045))
cycomat=mat('MAT_cyclorama',(.019,.055,.025),1,.6)
def box(name,p,s,m):
 x,y,z=p;a,b,c=[q/2 for q in s]
 return mesh(name,[(x+u*a,y+v*b,z+w*c) for u,v,w in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
def cyl(name,p,r,h,m,n=12):
 vs=[(p[0]+r*math.cos(i*math.tau/n),p[1]+r*math.sin(i*math.tau/n),p[2]+z*h/2) for z in [-1,1] for i in range(n)]
 return mesh(name,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
def beam(name,a,b,r,m):
 d=Vector(b)-Vector(a);o=cyl(name,(0,0,0),r,d.length,m,8)
 o.location=(Vector(a)+Vector(b))/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def empty(name,p,room=None):
 o=bpy.data.objects.new(name,None);C.objects.link(o);o.location=p;o.empty_display_type='CUBE';o.empty_display_size=.3
 if room:o['room_id']=room;o['trigger_size']=[1.2,1.2,2.1]
 return o
def collision(name,p,s):
 o=box('COL_'+name,p,s,None);o.hide_render=True;o.display_type='WIRE';o['godot_collision']='box';return o
def light(name,p,energy,col,kind='POINT',target=None):
 d=bpy.data.lights.new(name,kind);d.energy=energy;d.color=col
 if kind=='POINT':d.shadow_soft_size=.1
 if kind=='SUN':d.angle=math.radians(.5)
 o=bpy.data.objects.new(name,d);C.objects.link(o);o.location=p
 if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 return o
def camera(name,p,target,lens=24):
 d=bpy.data.cameras.new(name);d.lens=lens;d.clip_end=250
 o=bpy.data.objects.new(name,d);C.objects.link(o);o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Songti.ttc')
def sign(text,p,w=2):
 box('KIT_props_calligraphy_board',p,(w,.14,.62),wood)
 d=bpy.data.curves.new('painted_characters','FONT');d.body=text;d.font=font;d.size=.43;d.align_x='CENTER';d.extrude=.002
 o=bpy.data.objects.new('KIT_props_inscription_'+text,d);C.objects.link(o);o.location=(p[0],p[1]-.08,p[2]-.16);o.rotation_euler=(math.pi/2,0,0);d.materials.append(gold)
 o['finish']='Calligraphy layout; replace typeset glyphs with painted decal in final art pass'
def lantern(p,lit=True):
 x,y,z=p;cyl('KIT_props_lantern_paper',p,.18,.45,amber,8)
 for dz in [-.26,.26]:cyl('KIT_props_lantern_cap',(x,y,z+dz),.22,.065,wood,8)
 beam('KIT_props_lantern_chain',(x,y,z+.28),(x,y,z+.65),.013,wood)
 for i in range(8):
  t=i*math.tau/8;beam('KIT_props_lantern_rib',(x+.182*math.cos(t),y+.182*math.sin(t),z-.22),(x+.182*math.cos(t),y+.182*math.sin(t),z+.22),.011,wood)
 if lit:light('LGT_lantern',(x,y,z),65,(1,.38,.005))
def roof(p,r,n=6):
 x,y,z=p;vs=[]
 rings=[(r,z+.2),(r*.9,z),(r*.61,z+.45),(r*.25,z+1.25),(.06,z+1.5)]
 for rr,zz in rings:
  for i in range(n):
   a=math.tau*i/n+math.pi/6;vs.append((x+rr*math.cos(a),y+rr*math.sin(a),zz))
 fs=[]
 for j in range(4):
  for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 mesh('KIT_pavilion_roof',vs,fs,roofmat)
 for i in range(n):
  for j in range(4):beam('KIT_pavilion_hip',vs[j*n+i],vs[(j+1)*n+i],.047,stone)
  # repeated narrow tile ridges along each pitched roof facet
  k=(i+1)%n
  for t in range(1,10):
   f=t/10
   for j in range(3):
    a=Vector(vs[j*n+i]).lerp(Vector(vs[j*n+k]),f);b=Vector(vs[(j+1)*n+i]).lerp(Vector(vs[(j+1)*n+k]),f)
    beam('KIT_pavilion_tile_strip',a,b,.022,roofmat)
 cyl('KIT_pavilion_finial',(x,y,z+1.65),.12,.3,gold)
def pavilion(p,r=3,n=6,lanterns=True):
 x,y,z=p;cyl('KIT_pavilion_plinth',(x,y,z-.13),r+.25,.26,stone,n)
 for i in range(n):
  a=i*math.tau/n+math.pi/6;px=x+(r-.3)*math.cos(a);py=y+(r-.3)*math.sin(a)
  cyl('KIT_pavilion_post',(px,py,z+1.55),.1,3.1,wood)
  cyl('KIT_pavilion_post_foot',(px,py,z+.15),.17,.3,stone)
  box('KIT_pavilion_bracket',(px,py,z+2.85),(.55,.45,.13),wood)
  if lanterns:lantern((x+(r-.65)*math.cos(a),y+(r-.65)*math.sin(a),z+2.45),i<4)
 roof((x,y,z+3.05),r+.55,n)
def rail(a,b):
 for z in [.4,.9]:beam('KIT_corridor_rail',(a[0],a[1],a[2]+z),(b[0],b[1],b[2]+z),.045,wood)
 for i in range(7):
  p=Vector(a).lerp(Vector(b),i/6);beam('KIT_corridor_baluster',(p.x,p.y,p.z+.15),(p.x,p.y,p.z+.9),.032,wood)
def corridor(p,axis=0):
 x,y,z=p;start=set(C.objects)
 box('KIT_corridor_floor',(x,y,z-.1),(1.8,3,.2),stone)
 collision('corridor',(x,y,z-.13),(1.8,3,.25))
 for dx in [-.86,.86]:
  for dy in [-1.5,1.5]:cyl('KIT_corridor_post',(x+dx,y+dy,z+1.45),.07,2.9,wood,8)
  rail((x+dx,y-1.5,z),(x+dx,y+1.5,z))
 # gabled curved eaves
 vs=[(x+dx,y+dy,z+zz) for dy in [-1.65,1.65] for dx,zz in [(-1.2,2.95),(-.9,2.8),(0,3.45),(.9,2.8),(1.2,2.95)]]
 mesh('KIT_corridor_roof',vs,[(i,i+1,i+6,i+5) for i in range(4)],roofmat)
 for dx in [-.9,0,.9]:beam('KIT_corridor_ridge',(x+dx,y-1.65,z+(3.46 if dx==0 else 2.83)),(x+dx,y+1.65,z+(3.46 if dx==0 else 2.83)),.055,stone)
 if axis:
  from mathutils import Matrix
  rot=Matrix.Rotation(axis,4,'Z');t=Matrix.Translation((x,y,z));xf=t@rot@t.inverted()
  for o in set(C.objects)-start:o.matrix_world=xf@o.matrix_world

def rock(p,s=(1,1,2)):
 # moulded irregular rings, deliberately faceted plaster
 vs=[];n=9
 for j in range(5):
  for i in range(n):
   a=i*math.tau/n;rr=random.uniform(.7,1.15)*(math.sin(math.pi*(j+.5)/5)*.65+.3)
   vs.append((p[0]+s[0]*rr*math.cos(a),p[1]+s[1]*rr*math.sin(a),p[2]+s[2]*j/4))
 return mesh('KIT_rockery_plaster',vs,[tuple(reversed(range(n)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(4) for i in range(n)]+[tuple(range(4*n,5*n))],stone)
def bamboo(p,count=8):
 x,y,z=p
 for j in range(count):
  px=x+random.uniform(-.65,.65);py=y+random.uniform(-.65,.65);h=random.uniform(2.5,4.5)
  beam('KIT_flora_bamboo',(px,py,z),(px+.15,py,z+h),.032,foliage)
  for k in range(3):
   zz=z+h*.5+k*.5
   for d in [-1,1]:mesh('KIT_flora_leaf_card',[(px,py,zz),(px+d*.65,py-.12,zz+.25),(px+d*1.1,py,zz+.15),(px+d*.5,py+.12,zz+.1)],[(0,1,2,3)],foliage)
def crt(p,am=False):
 x,y,z=p;box('KIT_tech_CRT_housing',(x,y,z),(.64,.5,.5),black)
 box('KIT_tech_CRT_screen',(x,y-.256,z+.02),(.51,.014,.34),crtamber if am else green)
 for i in range(11):box('KIT_tech_scanline',(x,y-.265,z-.13+i*.029),(.5,.008,.006),black)
 box('KIT_tech_cursor',(x-.15,y-.272,z-.04),(.045,.008,.013),amber)
 box('KIT_tech_CRT_stand',(x,y,z-.3),(.3,.27,.1),wood)
def build_stage():
 collection('stage')
 box('KIT_stage_floor',(0,0,-1.65),(90,100,.3),black)
 # physical cyclorama closing every view
 n=96;vs=[(48*math.cos(i*math.tau/n),48*math.sin(i*math.tau/n),z) for z in [-2,20] for i in range(n)]
 mesh('KIT_stage_cyclorama',vs,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],cycomat)
 for layer in range(3):
  m=mat('MAT_painted_mountains_'+str(layer),(.018+layer*.008,.048+layer*.019,.019+layer*.007),1,.6)
  vs=[]
  for i in range(n+1):
   a=i*math.tau/n;rad=47.7-layer*.1;h=3+layer*2+2*math.sin(a*7+layer)+math.sin(a*13)
   vs.extend([(rad*math.cos(a),rad*math.sin(a),-1.5),(rad*math.cos(a),rad*math.sin(a),h)])
  mesh('KIT_stage_painted_mountain_layer',vs,[(2*i,2*i+2,2*i+3,2*i+1) for i in range(n)],m)
 moon=mat('MAT_painted_moon',(.42,.55,.2),1,.8)
 o=cyl('KIT_stage_painted_moon', (0,0,0),2.7,.015,moon,64);o.location=(-15,44,12);o.rotation_euler=(math.pi/2,0,0)
 light('LGT_stage_green_key',(15,-20,25),2.3,(.18,1,.22),'SUN',(0,0,0))
 light('LGT_stage_amber_rim',(-22,12,20),1.0,(1,.4,.02),'SUN',(0,0,0))
 scene['engine_target']='Godot 4';scene['fog_height']=.6;scene['fog_color']='#2EBD2E'
def build_qinfang():
 collection('qinfang-ting')
 # 14 m bridge, arch underside, deck at origin
 vs=[]
 for i in range(29):
  y=-7+i*.5;under=-.22-1.0*(abs(y)/7)**2
  vs.extend([(-3.4,y,0),(3.4,y,0),(-3.4,y,under),(3.4,y,under)])
 mesh('HERO_qinfang_bridge',vs,[(4*i,4*i+4,4*i+5,4*i+1) for i in range(28)]+[(4*i+2,4*i+3,4*i+7,4*i+6) for i in range(28)]+[(4*i,4*i+2,4*i+6,4*i+4) for i in range(28)]+[(4*i+1,4*i+5,4*i+7,4*i+3) for i in range(28)],stone)
 collision('qinfang_deck',(0,0,-.12),(6.8,14,.24));pavilion((0,0,0))
 for x in [-3.25,3.25]:
  for y in [-5,5]:rail((x,y-1.8,0),(x,y+1.8,0))
 cyl('HERO_table_hexagram',(0,0,.83),.88,.14,stone,32);cyl('HERO_table_pedestal',(0,0,.4),.25,.8,stone)
 for i in range(6):
  y=-.35+i*.14
  o=box('HERO_table_line_'+str(i+1)+'_solid',(0,y,.91),(.65,.055,.018),gold);o['variant']='solid'
  for x in [-.22,.22]:
   o=box('HERO_table_line_'+str(i+1)+'_broken',(x,y,.91),(.22,.055,.018),gold);o.hide_render=True;o.hide_viewport=True;o['variant']='broken'
 for x,y in [(1.4,0),(-1.4,0),(0,1.5),(0,-1.5)]:cyl('KIT_props_stool',(x,y,.3),.28,.6,stone)
 sign('沁芳',(0,-2.48,2.68))
 for dx,dy,angle in [(0,1,0),(0,-1,0),(1,0,math.pi/2),(-1,0,math.pi/2)]:
  for i in range(4):corridor((dx*(8.5+3*i),dy*(8.5+3*i),0),angle)
 box('KIT_water_stream',(0,0,-1.1),(80,10,.04),water)
 for y in [-5.2,5.2]:box('KIT_water_embankment',(0,y,-.75),(80,.5,.7),stone)
 for i in range(34):
  x=random.uniform(-14,14);y=random.uniform(.7,4.5)
  if abs(x)>4:cyl('KIT_water_lotus',(x,y,-1.05),random.uniform(.15,.4),.014,foliage,10)
 for x in [-7,7]:bamboo((x,-7,-.4),12)
 for name,p,room in [('qinfang_center',(0,-1.8,0),'qinfang_ting'),('qinfang_table',(0,-1,.9),'qinfang_ting'),('qinfang_rail',(3,4,0),'qinfang_ting'),('exit_east',(19,0,0),'yihong_yuan'),('exit_west',(-19,0,0),'ouxiang_xie'),('exit_north',(0,19,0),'daguan_lou'),('exit_south',(0,-7,0),'rockery_gate')]:empty('TRG_'+name,p,room)
 scene.camera=camera('CAM_stage_wide',(17,-26,9),(0,2,2.2),36)
 camera('CAM_shawscope',(5,-5,1.6),(0,0,1),40)
 camera('CAM_garden_overview',(45,-58,42),(0,0,0),38)
def build_gate():
 collection('rockery-gate')
 for j in range(9):
  y=-31+j*1.5;x=math.sin(j*math.pi/4)*.8
  box('KIT_rockery_tunnel_floor',(x,y,-.12),(2.3,1.8,.24),stone);collision('tunnel_floor',(x,y,-.15),(2.3,1.8,.3))
  for side in [-1,1]:
   rock((x+side*1.8,y,0),(.7,1.1,3.2));collision('tunnel_wall',(x+side*1.8,y,1.4),(1,1.6,2.8))
  rock((x,y,2.65),(1.9,.9,.8))
 for y in [-28,-22]:lantern((.7,y,2.0))
 sign('曲徑通幽',(0,-32,2.75),2.4)
 bamboo((2.5,-18,0),4)
 for n,p,r in [('gate_mouth',(0,-32,0),'rockery_gate'),('gate_bend_2',(-.6,-23,0),'rockery_gate'),('gate_exit',(0,-18,0),'qinfang_ting')]:empty('TRG_'+n,p,r)
 camera('CAM_gate_reveal',(0,-18.5,1.65),(0,0,2),24)
def build_cells():
 collection('terminal-cells')
 for i in range(6):
  x=(i-2.5)*2.6;y=-37
  box('KIT_stage_cell_floor',(x,y,-.12),(2.4,2.4,.24),wood);collision('cell_floor',(x,y,-.14),(2.4,2.4,.28))
  for dx in [-1.2,1.2]:box('KIT_tech_cell_side',(x+dx,y,1.3),(.12,2.4,2.6),black);collision('cell_wall',(x+dx,y,1.3),(.12,2.4,2.6))
  box('KIT_tech_cell_ceiling',(x,y,2.65),(2.4,2.4,.1),black)
  # barred north window, open south doorway
  for zz,h in [(.55,1.1),(2.35,.5)]:box('KIT_wall_window_wall',(x,y+1.2,zz),(2.4,.12,h),black)
  for dx in [-.9,.9]:box('KIT_wall_window_side',(x+dx,y+1.2,1.65),(.6,.12,1.1),black)
  for dx in [-.4,-.2,0,.2,.4]:beam('KIT_wall_window_bar',(x+dx,y+1.2,1.1),(x+dx,y+1.2,2.1),.025,wood)
  for dx in [-.88,.88]:box('KIT_tech_door_jamb',(x+dx,y-1.2,1.3),(.64,.13,2.6),black)
  box('KIT_tech_door_head',(x,y-1.2,2.35),(1.2,.13,.5),black)
  box('KIT_tech_terminal_desk',(x,y+.4,.74),(1.3,.65,.09),wood)
  for dx in [-.52,.52]:box('KIT_tech_desk_leg',(x+dx,y+.4,.35),(.07,.5,.7),wood)
  crt((x,y+.5,1.1));light('LGT_CRT_cell_'+str(i),(x,y+.05,1.15),12,(.18,1,.18))
  box('KIT_props_chair_seat',(x,y-.4,.43),(.45,.43,.06),wood)
  box('KIT_props_chair_back',(x,y-.59,.75),(.45,.05,.5),wood)
  for dx in [-.18,.18]:
   for dy in [-.16,.16]:beam('KIT_props_chair_leg',(x+dx,y-.4+dy,0),(x-dx,y-.4+dy,.44),.022,wood)
  for n,p,r in [('cell_seat',(x,y-.4,0),'terminal_room'),('cell_window',(x,y+.7,0),'terminal_room'),('cell_door',(x,y-1.2,0),'rockery_gate')]:empty('TRG_'+n+('' if i==2 else '_'+str(i)),p,r)
 box('KIT_stage_entry_corridor',(0,-39.3,-.12),(17,1.8,.24),wood);collision('entry_corridor',(0,-39.3,-.14),(17,1.8,.28))
 # route around east end of cells to gate
 for p,s in [((8.4,-35.8,-.12),(1.8,8,.24)),((4.2,-32.5,-.12),(10,1.8,.24))]:box('KIT_stage_entry_walk',p,s,stone);collision('entry_walk',p,s)
 camera('CAM_cells_wide',(9,-40,1.7),(-4,-36.5,1.1),24)
 camera('CAM_cell_entry',(-1.3,-38.8,1.65),(-1.3,-36.5,1.1),24)

build_stage();build_qinfang();build_gate();build_cells()
print('Priority 1 built:',len(scene.objects),'objects')
