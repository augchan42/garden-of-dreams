"""Fit eight painted kit arcs to the garden's existing circular soundstage."""
import bpy,json,math
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
stage=bpy.data.collections['SITE_stage'];canvas=bpy.data.objects['KIT_stage_cyclorama']
before={o.name:list(v for row in o.matrix_basis for v in row) for o in scene.objects if o.name.startswith(('COL_','TRG_','LGT_')) and not o.get('enclosure_collision')}
with bpy.data.libraries.load(str(R/'blender/kits/KIT_stage.blend'),link=False) as (src,dst):dst.collections=['KIT_stage_cyclorama_moonlit']
module=next(o for o in dst.collections[0].objects if o.type=='MESH' and not o.name.startswith('COL_'))
assert module.data.uv_layers
radius=48.;height=22.;bottom=-2.;count=8;span=math.tau/count
verts=[];faces=[];uvs=[];materials=[];groups=[]
for panel in range(count):
 rotation=Matrix.Rotation(panel*span,4,'Z');offset=len(verts);indices=[]
 for vertex in module.data.vertices:
  a=math.asin(max(-1,min(1,vertex.co.x/14.)))
  back=vertex.co.y-14*(math.cos(a)-1)>.04
  phi=a/1.44*span;r=radius+(.08 if back else 0)
  p=rotation@Vector((r*math.sin(phi),r*math.cos(phi),bottom+vertex.co.z/7.5*height))
  indices.append(len(verts));verts.append(p)
 groups.append(indices)
 for poly in module.data.polygons:
  faces.append([offset+i for i in poly.vertices]);materials.append(poly.material_index)
  # Keep the existing single moon; the other panels use mountain/sky artwork.
  uvs.append([(module.data.uv_layers[0].data[i].uv.x*.70,module.data.uv_layers[0].data[i].uv.y) if poly.material_index==0 else tuple(module.data.uv_layers[0].data[i].uv) for i in poly.loop_indices])
mesh=bpy.data.meshes.new('Eight painted cyclorama arcs');mesh.from_pydata(verts,[],faces);mesh.update()
for material in module.data.materials:mesh.materials.append(bpy.data.materials[material.name.split('.')[0]])
uv=mesh.uv_layers.new(name='UVMap')
for poly,coords,material in zip(mesh.polygons,uvs,materials):
 poly.material_index=material
 for i,value in zip(poly.loop_indices,coords):uv.data[i].uv=value
canvas.data=mesh;canvas.matrix_basis=Matrix.Identity(4);canvas['enclosure_panels']=count;canvas['enclosure_radius']=radius;canvas['stage_variant']='cyclorama_moonlit'
canvas.vertex_groups.clear()
for panel,indices in enumerate(groups):canvas.vertex_groups.new(name='Panel_'+str(panel+1)).add(indices,1.,'REPLACE')
for o in list(scene.objects):
 if o.get('enclosure_collision'):bpy.data.objects.remove(o,do_unlink=True)
for panel in range(count):
 for segment in range(8):
  phi=panel*span+((segment+.5)/8-.5)*span
  bpy.ops.mesh.primitive_cube_add(size=1,location=(-radius*math.sin(phi),radius*math.cos(phi),bottom+height/2))
  o=bpy.context.object;o.name=f'COL_stage_enclosure_{panel}_{segment}';o.scale=(2*radius*math.sin(span/16)+.05,.30,height);o.rotation_euler=(0,0,phi);o.hide_render=True;o.hide_viewport=True;o['enclosure_collision']=True
  for col in list(o.users_collection):col.objects.unlink(o)
  stage.objects.link(o)
for name,matrix in before.items():assert list(v for row in bpy.data.objects[name].matrix_basis for v in row)==matrix,name
wash=bpy.data.objects['LGT_stage_backdrop_wash'];assert len(wash.light_linking.receiver_collection.objects)==5 and canvas in list(wash.light_linking.receiver_collection.objects)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
bpy.data.libraries.write(str(R/'blender/sites/SITE_stage.blend'),{stage},fake_user=True,compress=True)
(R/'export/stage-enclosure.json').write_text(json.dumps({'variant':'cyclorama_moonlit','panels':count,'radius':radius,'height':height,'bottom':bottom,'colliders':64,'front_u_range':[0,.70],'single_original_moon_preserved':True,'wash_receivers':5,'existing_collision_light_trigger_transforms_preserved':True},indent=2)+'\n')
print('STAGE_ENCLOSURE_SOURCE_PASS',count,'arcs, 64 proxies, original moon and five linked receivers')
