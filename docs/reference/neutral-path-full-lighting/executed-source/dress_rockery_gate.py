"""Add the specified single potted banana and fitted second-bend water-stain decal."""
import bpy,math,ast,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
C=scene.collection.children['SITE_rockery-gate']
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for o in list(C.objects):
 if o.get('gate_dressing') or o.name.startswith('KIT_flora_'):bpy.data.objects.remove(o,do_unlink=True)
prior=set(C.objects)
stone=bpy.data.materials['MAT_plaster_rock'];wood=bpy.data.materials['MAT_lattice_wood'];foliage=bpy.data.materials['MAT_foliage_card']
# East of the walking path; the reveal camera exits on the opposite side.
px,py=.55,-17.35
# Tapered open planter, rolled rim and recessed soil.
vs=[];rings=[(.20,.02),(.30,.52),(.25,.52),(.19,.13)]
for r,z in rings:
 for i in range(16):
  a=math.tau*i/16;vs.append((px+r*math.cos(a),py+r*math.sin(a),z))
fs=[]
for j in range(3):
 for i in range(16):fs.append((j*16+i,j*16+(i+1)%16,(j+1)*16+(i+1)%16,(j+1)*16+i))
mesh('GATE_banana_planter',vs,fs,stone)
cyl('GATE_banana_soil',(px,py,.18),.195,.02,wood,16)
c=collision('GATE_banana_planter',(px,py,.27),(.60,.60,.54));c.hide_viewport=True
beam('GATE_banana_pseudostem',(px,py,.19),(px+.1,py,2.45),.10,foliage)
for leaf in range(7):
 a=leaf*math.tau/7+.3;length=.8+.12*(leaf%3)
 base=Vector((px+.1,py,2.45-.11*(leaf%3)));direction=Vector((math.cos(a),math.sin(a),0));side=Vector((-math.sin(a),math.cos(a),0))
 vs=[];centres=[]
 for j in range(13):
  t=j/12;centre=base+direction*(length*t)+Vector((0,0,.55*math.sin(math.pi*t)-.52*t*t));centres.append(centre)
  width=.24*math.sin(math.pi*t)**.75
  # Irregular leaf margins suggest natural splits without disconnected geometry.
  left=width*(.63 if j in (7,10) else 1);right=width*(.7 if j in (5,9) else 1)
  vs.extend([centre-side*left-Vector((0,0,width*.18)),centre+Vector((0,0,.025*math.sin(math.pi*t))),centre+side*right-Vector((0,0,width*.18))])
 fs=[]
 for j in range(12):
  for k in range(2):fs.append((j*3+k,(j+1)*3+k,(j+1)*3+k+1,j*3+k+1))
 mesh('GATE_banana_leaf',vs,fs,foliage)
 for j in range(12):beam('GATE_banana_midrib',centres[j],centres[j+1],.009,foliage)
# Project a gridded transparent stain onto the actual inside wall at the second bend.
bpy.context.view_layer.update()
vs=[];fs=[]
for o in C.objects:
 if o.get('kit_placement')=='gate_rockery' and o.get('kit_part')=='tunnel' and not o.name.startswith('COL_'):
  start=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(start+i for i in p.vertices) for p in o.data.polygons)
bvh=BVHTree.FromPolygons(vs,fs)
vs=[];uvs=[];fs=[];nx,ny=24,32
for j in range(ny+1):
 for i in range(nx+1):
  u=i/nx;v=j/ny;y=-22.6+1.2*u;z=.35+1.5*v
  center=1.8*math.sin(math.tau*(y+31)/12)
  hit,normal,idx,dist=bvh.ray_cast(Vector((center,y,z)),Vector((1,0,0)),3)
  assert hit is not None, (y,z)
  vs.append(hit-Vector((.012,0,0)));uvs.append((u,v))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i;fs.append((a,a+nx+1,a+nx+2,a+1))
m=bpy.data.materials.get('MAT_gate_drips') or mat('MAT_gate_drips',(1,1,1),.25)
p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
im=bpy.data.images.load(str(R/'textures/decals/gate-water-drips.png'),check_existing=True);im.pack()
tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha'])
prop=m.bl_rna.properties.get('surface_render_method')
if prop:m.surface_render_method=next(i.identifier for i in prop.enum_items if i.identifier=='DITHERED')
o=mesh('HERO_gate_water_drips',vs,fs,m);uv=o.data.uv_layers.new(name='UVMap')
for p in o.data.polygons:
 for li in p.loop_indices:uv.data[li].uv=uvs[o.data.loops[li].vertex_index]
for o in set(C.objects)-prior:o['gate_dressing']=True
assert sum(o.name.startswith('GATE_banana_leaf') for o in C.objects)==7
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_rockery-gate.blend';bpy.data.libraries.write(str(file),{C},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_rockery-gate']
s=bpy.context.scene;s.name='SITE_rockery-gate';s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.render.resolution_x=1410;s.render.resolution_y=600;s.render.resolution_percentage=100
s.camera=next(o for o in s.objects if o.name.startswith('CAM_gate_reveal_wide'))
tmp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('GATE_DRESSING_SAVED: one potted banana, seven leaves, second-bend projected drip decal')
