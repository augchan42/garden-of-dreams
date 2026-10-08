"""Save an isolated whole-Garden candidate with outward pavilion tile normals."""
import argparse
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from moon_paint_contract import ROOT,snapshot,check
from pavilion_roof_geometry import orient_tile_ridges
from pavilion_roof_geometry import components,face_uv_signature
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-root',type=Path,required=True)
parser.add_argument('--ridge-rise',type=float,default=.026)
parser.add_argument('--ridge-half-width',type=float,default=.023)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
out=args.output_root.resolve()
assert out!=ROOT and ROOT not in out.parents
assert not (out/'blender/authoring.blend').exists()
source=Path(bpy.data.filepath);original=hashlib.sha256(source.read_bytes()).hexdigest()
assert original=='a273a4c0ea33c9897f3096f51b5833b905e04a6d0ca62cab001e8291aa93b8de','Candidate must begin from inspected current source'
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
roof=bpy.data.objects['QINFANG_kit_roof_hex'];before=snapshot();moon=check()
assert .004<=args.ridge_rise<=.026 and .023<=args.ridge_half_width<=.045
positions=[tuple(v.co) for v in roof.data.vertices]
uv=face_uv_signature(roof.data)
allowed=set()
for vertices,faces in components(roof.data):
 if len(vertices)!=15 or len(faces)!=8:continue
 indices=sorted(vertices);allowed.update(indices)
 for offset in range(0,15,3):
  left,top,right=[roof.data.vertices[i] for i in indices[offset:offset+3]]
  center=(left.co+right.co)*.5
  tangent=(right.co-left.co)*.5
  assert abs(tangent.length-.023)<1e-6 and abs(tangent.z)<1e-6
  assert abs(top.co.z-center.z-.026)<1e-6 and (top.co.xy-center.xy).length<1e-6
  if args.ridge_rise==.026 and args.ridge_half_width==.023:continue
  left.co=center-tangent*(args.ridge_half_width/.023)
  right.co=center+tangent*(args.ridge_half_width/.023)
  top.co.z=center.z+args.ridge_rise
roof.data.update()
changed_vertices=[i for i,v in enumerate(roof.data.vertices) if (v.co-Vector(positions[i])).length>1e-7]
assert set(changed_vertices)<=allowed
assert uv==face_uv_signature(roof.data)
change=orient_tile_ridges(roof);assert len(change['flipped_faces'])==336
bpy.context.view_layer.update();after=snapshot()
changed={name for name in before['objects'] if before['objects'][name]!=after['objects'][name]}
assert changed=={roof.name}
after['objects'][roof.name]['mesh']=before['objects'][roof.name]['mesh']
assert after==before,'Unrelated source record changed'
assert check()==moon
(out/'blender').mkdir(parents=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'blender/authoring.blend'),compress=True)
bpy.data.libraries.write(str(out/'blender/SITE_qinfang-ting.blend'),{bpy.data.collections['SITE_qinfang-ting']},fake_user=True,compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==original
report={'status':'scratch_candidate_fresh_lighting_pending','source_authoring_sha256':original,'candidate_authoring_sha256':hashlib.sha256((out/'blender/authoring.blend').read_bytes()).hexdigest(),'candidate_site_sha256':hashlib.sha256((out/'blender/SITE_qinfang-ting.blend').read_bytes()).hexdigest(),'unchanged_object_records':len(before['objects'])-1,'unchanged_materials':len(before['materials']),'moon_preserved':moon,'changes':change,'scope':'Only 336 inward raised tile faces reverse winding in the separate complete saved candidate. Positions, vertex UV ownership, material assignments, shell/underside/hips/rafters, camera/collision/lights and every other source object remain unchanged. Not adopted; export/fresh lighting/native appearance remain required.'}
report['ridge_profile']={'rise_metres':args.ridge_rise,'half_width_metres':args.ridge_half_width,'changed_vertex_indices':changed_vertices,'uv_ownership_preserved':True,'non_ridge_positions_preserved':True}
if changed_vertices:
 report['scope']='Separate whole-scene candidate changes only the 42 raised tile caps to the recorded profile and reverses their 336 inward faces. Primary vertex UV ownership, material assignment, shell/underside/hips/rafters, camera/collision/lights and every other source object remain unchanged. Not adopted; export/fresh lighting/native appearance remain required.'
(out/'source-preparation.json').write_text(json.dumps(report,indent=2)+'\n')
print('TILE_RIDGE_CANDIDATE_PASS',change['tile_strips'],len(change['flipped_faces']),report['unchanged_object_records'])
