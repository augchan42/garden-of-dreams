"""Open the covered walk's western rail where the bamboo approach joins it."""
import bpy,bmesh
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=s;bpy.context.view_layer.update()
col=bpy.data.collections['SITE_qinfang-ting'];removed=0
for o in list(col.objects):
 if o.type!='MESH' or not o.name.startswith(('QINFANG_corridor_south_1','QINFANG_corridor_south_2','COL_QINFANG_corridor_south_1','COL_QINFANG_corridor_south_2')):continue
 if o.name.startswith('COL_'):
  points=[o.matrix_basis@Vector(p) for p in o.bound_box];lo=Vector(tuple(min(v[a] for v in points) for a in range(3)));hi=Vector(tuple(max(v[a] for v in points) for a in range(3)));center=(lo+hi)/2
  if abs(center.x+.86)>.14 or hi.z<.1 or hi.y < -14 or lo.y > -12:continue
  bpy.data.objects.remove(o,do_unlink=True);removed+=1
  # Preserve side protection outside the 2 m opening. Posts inside it are removed.
  if hi.z<1.2:
   for a,b in [(lo.y,min(hi.y,-14)),(max(lo.y,-12),hi.y)]:
    if b-a<.01:continue
    bpy.ops.mesh.primitive_cube_add(size=1,location=(center.x,(a+b)/2,.5));part=bpy.context.object;part.name='COL_bamboo_walk_rail';part.scale=(.09,b-a,1)
    for old in list(part.users_collection):old.objects.unlink(part)
    col.objects.link(part)
  continue
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_basis)
 for y in [-14,-12]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=(0,y,0),plane_no=(0,1,0))
 faces=[f for f in bm.faces if abs(f.calc_center_median().x+.86)<.14 and -14.0001<f.calc_center_median().y<-11.9999 and .1<f.calc_center_median().z<2.95]
 bmesh.ops.delete(bm,geom=faces,context='FACES');bm.transform(o.matrix_basis.inverted());bm.to_mesh(o.data);bm.free()
# Frame the opening with replacement posts at its ends, outside the clear crossing.
if not any(o.name.startswith('BAMBOO_walk_junction_post') for o in col.objects):
 for y in [-14,-12]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.065,depth=2.9,location=(-.86,y,1.45));o=bpy.context.object;o.name='BAMBOO_walk_junction_post';o.data.materials.append(bpy.data.materials['MAT_lattice_wood'])
  for old in list(o.users_collection):old.objects.unlink(o)
  col.objects.link(o)
  bpy.ops.mesh.primitive_cube_add(size=1,location=(-.86,y,1.45));o=bpy.context.object;o.name='COL_bamboo_walk_junction_post';o.scale=(.15,.15,2.9)
  for old in list(o.users_collection):old.objects.unlink(o)
  col.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
bpy.data.libraries.write(str(R/'blender/sites/SITE_qinfang-ting.blend'),{col},fake_user=True,compress=True)
print('BAMBOO_WALK_OPENING_PASS',removed,'rail/post colliders replaced; 2m opening')
