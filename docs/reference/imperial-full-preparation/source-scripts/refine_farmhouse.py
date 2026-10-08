"""Build Daoxiang's thatched farmhouse, rough fence and painted paddy flat."""
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
C=next(c for c in scene.collection.children if c.name=='SITE_daoxiang-cun')
for o in list(C.objects):bpy.data.objects.remove(o,do_unlink=True)
thatch=bpy.data.materials.get('MAT_thatch') or mat('MAT_thatch',(.18,.19,.075),1)
paddy=bpy.data.materials.get('MAT_paddy_paint') or mat('MAT_paddy_paint',(.045,.13,.035),1,.2)
box('DAOXIANG_court',(-32,20.1,-.12),(8,5.8,.24),stone)
collision('daoxiang_court',(-32,20.1,-.12),(8,5.8,.24))
box('DAOXIANG_front',(-32,22,1.35),(6,.2,2.7),plaster)
collision('daoxiang_closed_front',(-32,22,1.35),(6,.24,2.7))
box('DAOXIANG_backstage',(-32,24,1.4),(6,.2,2.8),black)
for x in [-35,-29]:
 box('DAOXIANG_side',(x,23,1.35),(.2,2.2,2.7),plaster)
 collision('daoxiang_side',(x,23,1.35),(.24,2.2,2.7))
box('DAOXIANG_closed_door',(-32,21.84,1.08),(1.45,.16,2.16),wood)
for x in [-32.6,-32.3,-32,-31.7,-31.4]:box('DAOXIANG_door_seam',(x,21.75,1.08),(.015,.025,2.1),black)
for z in [.35,1.65]:box('DAOXIANG_door_rail',(-32,21.69,z),(1.5,.09,.08),wood)
box('DAOXIANG_door_latch',(-31.52,21.65,1.03),(.07,.07,.18),gold)
box('DAOXIANG_warm_sliver',(-32,21.72,.035),(1.3,.04,.035),crtamber)
light('LGT_daoxiang_sliver',(-32,21.3,.16),20,(1,.38,.005))
for x in [-34,-30]:
 box('DAOXIANG_shutter',(x,21.85,1.6),(1.15,.12,.9),wood)
 for j in range(6):box('DAOXIANG_shutter_lath',(x-.5+j*.2,21.77,1.6),(.05,.04,.92),black)
# Thick thatch masses and uneven layered stalk bundles replace all tiled roof pieces.
vs=[(-35.6,21.25,2.7),(-28.4,21.25,2.7),(-35.35,23,4.0),(-28.65,23,4.0),(-35.6,24.75,2.7),(-28.4,24.75,2.7),(-35.6,21.25,2.45),(-28.4,21.25,2.45),(-35.6,24.75,2.45),(-28.4,24.75,2.45)]
mesh('DAOXIANG_thatch_mass',vs,[(0,1,3,2),(2,3,5,4),(6,7,1,0),(4,5,9,8),(0,2,4,8,6),(1,7,9,5,3)],thatch)
for side in [-1,1]:
 for row in range(3):
  start=row*.48;end=min(1.85,start+.82)
  for i in range(53):
   x=-35.55+i*.137
   jitter=.045*math.sin(i*2.3+row)
   a=(x,23+side*start,4.06-start*.76)
   b=(x+jitter,23+side*(end+.05*math.sin(i)),4.04-end*.76+jitter)
   beam('DAOXIANG_thatch_bundle',a,b,.047,thatch)
beam('DAOXIANG_bound_ridge',(-35.5,23,4.03),(-28.5,23,4.03),.13,thatch)
for x in [-35+i*.4 for i in range(16)]:beam('DAOXIANG_ridge_binding',(x,22.8,3.99),(x,23.2,3.99),.018,wood)
# Fence under one metre, with a clear central opening on the arrival aisle.
for a,b in [((-35.8,18),(-33,18)),((-31,18),(-28.2,18)),((-35.8,18),(-35.8,22)),((-28.2,18),(-28.2,22))]:
 av=Vector((*a,0));bv=Vector((*b,0));length=(bv-av).length
 for j in range(int(length/.75)+1):
  p=av.lerp(bv,j/max(1,int(length/.75)))
  beam('DAOXIANG_fence_post',p,p+Vector((.04*math.sin(j),0,.88)),.06,wood)
 for h in [.35,.72]:beam('DAOXIANG_rough_rail',av+Vector((0,0,h)),bv+Vector((0,0,h+.04)),.045,wood)
 center=(av+bv)/2;size=(abs(bv.x-av.x)+.14,abs(bv.y-av.y)+.14,.86)
 collision('daoxiang_fence',(center.x,center.y,.43),size)
# Two small agricultural tools propped against the wall.
for x in [-34.3,-33.75]:beam('DAOXIANG_tool_handle',(x,21,.12),(x+.15,21.7,1.75),.023,wood)
beam('DAOXIANG_rake_head',(-34.6,21,.18),(-34.0,21,.18),.026,wood)
for x in [-34.55+i*.12 for i in range(5)]:beam('DAOXIANG_rake_tooth',(x,21,.18),(x,20.8,.08),.018,wood)
box('DAOXIANG_hoe_blade',(-33.75,20.96,.12),(.3,.16,.12),gold)
# Visible studio flat: perspective field bands and rice strokes lie in one plane.
# Generated gouache painting replaces the geometric field-row placeholder.
paddy=bpy.data.materials.get('MAT_paddy_painted_texture') or mat('MAT_paddy_painted_texture',(1,1,1),1)
bsdf=next(n for n in paddy.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
tex=next((n for n in paddy.node_tree.nodes if n.type=='TEX_IMAGE'),None)
if tex is None:tex=paddy.node_tree.nodes.new('ShaderNodeTexImage')
tex.image=bpy.data.images.load(str(R/'textures/backdrops/daoxiang-paddy-v1.png'),check_existing=True);tex.image.pack()
paddy.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
paddy.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Emission Color'])
bsdf.inputs['Emission Strength'].default_value=.35
flat=mesh('DAOXIANG_paddy_painting',[(-40,23.8,.15),(-34,23.8,.15),(-34,23.8,3.15),(-40,23.8,3.15)],[(0,1,2,3)],paddy)
uv=flat.data.uv_layers.new(name='UVMap')
for loop,coord in zip(flat.data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uv.data[loop].uv=coord
box('DAOXIANG_paddy_black_back',(-37,23.87,1.65),(6,.04,3),black)
for x in [-40,-34]:box('DAOXIANG_paddy_frame',(x,23.79,1.65),(.055,.06,3.1),wood)
for z in [.15,3.15]:box('DAOXIANG_paddy_frame',(-37,23.79,z),(6.1,.06,.055),wood)
sign('稻香村',(-32,21.72,2.43),1.8)
light('LGT_daoxiang-cun_key',(-28,16,6),350,(.18,1,.18),'SPOT',(-32,22,2))
for name,p in [('entry',(-32,19.3,0)),('closed_door',(-32,20.8,0)),('tools',(-33,20.2,0)),('return',(-32,17,0))]:empty('TRG_daoxiang_cun_'+name,p,'daoxiang_cun')
camera('CAM_daoxiang-cun_wide',(-34,13,3.4),(-34,22,1.7),32)
camera('CAM_daoxiang-cun_door',(-32,19.7,1.7),(-32,22,1.2),35)
camera('CAM_daoxiang-cun_tools',(-32.5,19.8,1.5),(-34,21.2,.8),40)
camera('CAM_daoxiang-cun_paddy',(-38,19,2.5),(-37.3,23.8,1.6),32)
sites={c.name.removeprefix('SITE_'):c for c in scene.collection.children}
C=sites['stage']
for o in list(C.objects):
 if o.name.startswith(('DAOXIANG_approach','COL_daoxiang_approach')):bpy.data.objects.remove(o,do_unlink=True)
# Leave Hengwu through its front opening, then go around its western enclosure.
for p,size in [((-25,8,-.12),(15.8,1.8,.24)),((-32,13.65,-.12),(1.8,13.1,.24))]:
 box('DAOXIANG_approach',p,size,stone);collision('daoxiang_approach',p,size)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
for slug in ['daoxiang-cun','stage']:
 bpy.data.libraries.write(str(R/'blender/sites'/('SITE_'+slug+'.blend')),{sites[slug]},fake_user=True,compress=True)
for slug in ['daoxiang-cun','stage']:
 file=R/'blender/sites'/('SITE_'+slug+'.blend')
 bpy.ops.wm.read_factory_settings(use_empty=True)
 with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=[file.stem]
 s=bpy.context.scene;s.name=file.stem;s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
 s.camera=next((o for o in s.objects if o.type=='CAMERA'),None)
 temp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(temp),compress=True);os.replace(temp,file)
print('DAOXIANG_ART_PASS: layered thatch, rough fence, closed door, two tools, painted paddy flat')
