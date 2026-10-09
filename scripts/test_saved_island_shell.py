"""Check that the saved island is a consistently wound closed stone shell."""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
obj=bpy.data.objects['SITE_ziling_island']
mesh=obj.data;bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
points=[obj.matrix_world@v.co for v in mesh.vertices]
centre=sum(points,Vector())/len(points)
transform=obj.matrix_world.to_3x3().inverted().transposed()
outward=[];inward=[]
for face in mesh.polygons:
 normal=(transform@face.normal).normalized()
 if abs(normal.z)>.1:continue
 middle=sum((points[i] for i in face.vertices),Vector())/len(face.vertices)
 direction=middle-centre;direction.z=0
 dot=normal.dot(direction.normalized())
 (outward if dot>.9 else inward).append({'face':face.index,'normal_dot_outside':dot})
errors=[]
if len(outward)!=24 or inward:errors.append('The24 vertical exterior faces must point outside the island.')
if any(not e.is_manifold or not e.is_contiguous for e in bm.edges):errors.append('The complete shell must be manifold with consistent adjacent winding.')
if len(mesh.vertices)!=48 or len(mesh.polygons)!=26:errors.append('The saved24-sided island shell topology changed.')
if [m.name for m in mesh.materials]!=['MAT_plaster_rock']:errors.append('Stone material changed.')
lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
if abs(lo[2]+1.35)>1e-6 or abs(hi[2]+.08)>1e-6:errors.append('The original top/bottom island heights changed.')
bad=sum(not e.is_manifold or not e.is_contiguous for e in bm.edges);bm.free()
report={'status':'saved_island_shell_passed' if not errors else 'saved_island_shell_rejected','source_authoring_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'outward_side_faces':len(outward),'inward_side_faces':inward,'noncontiguous_or_nonmanifold_edges':bad,'bounds_z_up':[lo,hi],'errors':errors,'scope':'Actual saved mesh exterior orientation, closed winding, shape and material contract. No lighting/render/camera/collision/whole-site acceptance.'}
args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n')
print('ISLAND_SHELL_CONTRACT_RESULT',len(outward),'outward;',bad,'inconsistent edges;',len(errors),'failures',flush=True)
assert not errors,'; '.join(errors)
