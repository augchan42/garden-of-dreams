"""Repair only the reversed exterior faces in an isolated saved source."""
from pathlib import Path
import bpy, bmesh, hashlib, json, sys
from mathutils import Vector

repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/island-face-source'
src=repo/'blender/authoring.blend';out=work/'candidate/blender/authoring.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='074ab2014d9122e207783d9e7c7992f9dfc9197a6f380a2d6f5e8c0c05e31978'
assert Path(bpy.data.filepath)==src and sha(src)==expected
assert not out.exists()
sys.path.insert(0,str(repo/'scripts'))
from moon_paint_contract import snapshot,check
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene;bpy.context.view_layer.update()
before=snapshot();moon=check()
obj=bpy.data.objects['SITE_ziling_island'];mesh=obj.data
vertices=[list(v.co) for v in mesh.vertices]
topology=sorted(tuple(sorted(p.vertices)) for p in mesh.polygons)
assert len(mesh.vertices)==48 and len(mesh.polygons)==26 and not mesh.uv_layers
bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
centre=sum((v.co for v in bm.verts),Vector())/len(bm.verts)
faces=[]
for face in bm.faces:
 radial=face.calc_center_median()-centre;radial.z=0
 if abs(face.normal.z)<.1:
  assert face.normal.dot(radial.normalized())<-.9
  faces.append(face)
assert len(faces)==24
assert sum(not e.is_contiguous for e in bm.edges)==48
bmesh.ops.reverse_faces(bm,faces=faces);bm.normal_update()
assert all(e.is_manifold and e.is_contiguous for e in bm.edges)
assert bm.calc_volume(signed=True)>0
bm.to_mesh(mesh);bm.free();mesh.update();bpy.context.view_layer.update()
assert [list(v.co) for v in mesh.vertices]==vertices
assert sorted(tuple(sorted(p.vertices)) for p in mesh.polygons)==topology
after=snapshot();changed=[k for k in before['objects'] if before['objects'][k]!=after['objects'][k]]
assert changed==['SITE_ziling_island']
assert set(after['objects'])==set(before['objects']) and after['materials']==before['materials']
assert check()==moon
assert obj.matrix_world==bpy.data.objects['SITE_ziling_island'].matrix_world
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert sha(src)==expected
report={'status':'isolated_saved_island_winding_repaired','baseline_authoring_sha256':expected,'candidate_authoring_sha256':sha(out),'changed_objects':changed,'reversed_side_faces':24,'preserved_other_objects':len(before['objects'])-1,'vertices':48,'faces':26,'original_vertices_and_unoriented_faces_preserved':True,'materials_moon_and_all_other_objects_preserved':True,'scope':'Only24 island exterior face windings corrected in an isolated saved source. No canonical mutation, new geometry, lighting/export/native appearance or final-site acceptance.'}
(work/'candidate/source-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED_ISLAND_WINDING_REPAIR',24,'faces;',report['preserved_other_objects'],'other objects unchanged',flush=True)
