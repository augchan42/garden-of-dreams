"""Replace temporary typeset board with brush inscription recessed into the plaster arch."""
import bpy,ast,os
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
C=scene.collection.children['SITE_rockery-gate']
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for o in list(C.objects):
 if o.get('gate_inscription') or o.name.startswith(('KIT_props_calligraphy_board','KIT_props_inscription_')):bpy.data.objects.remove(o,do_unlink=True)
arch=next(o for o in C.objects if o.get('kit_part')=='arch' and not o.name.startswith('COL_') and min(v.co.y for v in o.data.vertices)<-30)
bvh=BVHTree.FromPolygons([arch.matrix_basis@v.co for v in arch.data.vertices],[tuple(p.vertices) for p in arch.data.polygons])
vs=[];uvs=[];fs=[];nx,ny=42,14
for j in range(ny+1):
 for i in range(nx+1):
  u=i/nx;v=j/ny;x=(u-.5)*1.8;z=3.0+(v-.5)*.6
  hit,normal,idx,dist=bvh.ray_cast(Vector((x,-33,z)),Vector((0,1,0)),2)
  assert hit is not None,('Inscription outside plaster',x,z)
  vs.append(hit-Vector((0,.006,0)));uvs.append((u,v))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
m=bpy.data.materials.get('MAT_gate_inscription') or mat('MAT_gate_inscription',(.2,.15,.09),.85)
m.node_tree.nodes.clear();out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Roughness'].default_value=.85
for filename,isnormal in [('gate-inscription.png',False),('gate-inscription-normal.png',True)]:
 im=bpy.data.images.load(str(R/'textures/decals'/filename),check_existing=True);im.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
 if isnormal:
  im.colorspace_settings.name='Non-Color';normal=m.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=1
  m.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
 else:
  m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(tex.outputs['Alpha'],p.inputs['Alpha'])
prop=m.bl_rna.properties.get('surface_render_method')
if prop:m.surface_render_method=next(i.identifier for i in prop.enum_items if i.identifier=='DITHERED')
o=mesh('HERO_gate_inscription',vs,fs,m);o['gate_inscription']=True;o['inscription_text']='曲徑通幽';o['finish']='Brush lettering with recessed normal map on plaster'
uv=o.data.uv_layers.new(name='UVMap')
for p in o.data.polygons:
 for li in p.loop_indices:uv.data[li].uv=uvs[o.data.loops[li].vertex_index]
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_rockery-gate.blend';bpy.data.libraries.write(str(file),{C},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_rockery-gate']
s=bpy.context.scene;s.name='SITE_rockery-gate';s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC';s.render.resolution_x=1410;s.render.resolution_y=600;s.render.resolution_percentage=100
s.camera=next(o for o in s.objects if o.name.startswith('CAM_gate_reveal_wide'))
tmp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('GATE_INSCRIPTION_SAVED: 曲徑通幽, 1.8m wide, alpha and recessed normals, all vertices supported by arch')
