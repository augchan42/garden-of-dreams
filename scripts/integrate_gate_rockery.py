"""Fit four reusable tunnel segments to the entrance's two-bend reveal route."""
import bpy, math, ast, os
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
C=scene.collection.children['SITE_rockery-gate']
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
stone=bpy.data.materials['MAT_plaster_rock'];wood=bpy.data.materials['MAT_lattice_wood'];amber=bpy.data.materials['MAT_lantern']
for o in list(C.objects):
 if o.name.startswith(('KIT_rockery_','COL_tunnel_','KIT_props_lantern_','LGT_lantern','GATE_paving','COL_GATE_paving')) or o.get('kit_placement')=='gate_rockery':
  bpy.data.objects.remove(o,do_unlink=True)
canonical={m.name:m for m in bpy.data.materials}
parts=['tunnel','arch','cliff']
with bpy.data.libraries.load(str(R/'blender/kits/KIT_rockery.blend'),link=False) as (src,dst):dst.collections=['KIT_rockery_'+p for p in parts]
modules=dict(zip(parts,dst.collections))
def center(y):return 1.8*math.sin(math.tau*(y+31)/12) if -31<y<-19 else 0
def place(part,p,length_scale=1,warp=False):
 xf=Matrix.Translation(p)@Matrix.Diagonal((1,length_scale,1,1))
 for source in modules[part].objects:
  if source.type!='MESH':continue
  o=source.copy();o.data=source.data.copy()
  for i,m in enumerate(o.data.materials):
   if m and m.name.split('.')[0] in canonical:o.data.materials[i]=canonical[m.name.split('.')[0]]
  for layer in list(o.data.uv_layers)[1:]:o.data.uv_layers.remove(layer)
  transform=xf@source.matrix_basis
  for v in o.data.vertices:
   v.co=transform@v.co
   if warp:v.co.x+=center(v.co.y)
  o.matrix_world=Matrix.Identity(4);C.objects.link(o)
  col=source.name.startswith('COL_');o.name=('COL_' if col else '')+'GATE_kit_'+part
  o['kit_placement']='gate_rockery';o['kit_part']=part;o.hide_viewport=col;o.hide_render=col
for y in [-29.5,-26.5,-23.5,-20.5]:place('tunnel',(0,y,0),.75,True)
for y in [-31.7,-18.3]:place('arch',(0,y,0))
for x in [-5.1,5.1]:place('cliff',(x,-18.8,0))
# One continuous slab follows the same centreline, including both arch landings.
vs=[];fs=[];steps=64
for i in range(steps+1):
 y=-32.6+15.2*i/steps;x=center(y)
 vs.extend([(x-1.2,y,0),(x+1.2,y,0),(x-1.2,y,-.2),(x+1.2,y,-.2)])
for i in range(steps):
 a=i*4;b=a+4;fs.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,a+4,a+6,a+2),(a+1,a+3,b+3,b+1)])
fs.extend([(0,2,3,1),(steps*4,steps*4+1,steps*4+3,steps*4+2)])
floor=mesh('GATE_paving',vs,fs,stone)
collider=floor.copy();collider.data=floor.data.copy();collider.data.materials.clear();C.objects.link(collider)
collider.name='COL_GATE_paving';collider.hide_render=True;collider.hide_viewport=True
for y in [-28,-22]:lantern((center(y)+.55,y,2.05))
for o in C.objects:
 if o.name.startswith('TRG_gate_bend_2'):o.location=(-1.8,-22,0)
 elif o.name.startswith('KIT_props_calligraphy_board'):
  mid=sum((o.matrix_world@Vector(c) for c in o.bound_box),Vector())/8
  o.location+=Vector((0,-32.48,3.12))-mid
 elif o.name.startswith('KIT_props_inscription_'):o.location=(0,-32.57,2.96)
bpy.context.view_layer.update()
assert sum(o.get('kit_placement')=='gate_rockery' for o in C.objects)==16
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_rockery-gate.blend';bpy.data.libraries.write(str(file),{C},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_rockery-gate']
s=bpy.context.scene;s.name='SITE_rockery-gate';s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.camera=next(o for o in s.objects if o.name.startswith('CAM_gate_reveal'))
tmp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('GATE_ROCKERY_INTEGRATED: four tunnel segments, two arches, two cliffs, continuous paving and two bend lanterns')
