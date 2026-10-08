"""Read saved Ouxiang source ownership and normals; never save the scene."""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
repo=Path('/Users/auchan/projects/garden-of-dreams')
out=Path(json.loads(Path('/tmp/garden-oux-roof-probe.json').read_text())['folder'])
source=repo/'blender/authoring.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest=='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c'
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene;bpy.context.view_layer.update()
rows=[]
for obj in sorted(bpy.data.collections['SITE_ouxiang-xie'].objects,key=lambda o:o.name):
 if obj.type!='MESH' or not (obj.name.startswith('KIT_pavilion_water_tiles') or obj.name=='KIT_pavilion_water_hipped_roof'):continue
 mesh=obj.data;positions=[tuple(obj.matrix_world@v.co) for v in mesh.vertices]
 center=sum((Vector(v) for v in positions),Vector())/len(positions)
 normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
 values=[float((normal_matrix@p.normal).normalized().dot(obj.matrix_world@p.center-center)) for p in mesh.polygons]
 row={'name':obj.name,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'triangles':sum(len(p.vertices)-2 for p in mesh.polygons),'material_names':[m.name for m in mesh.materials],'world_positions_z_up':positions,'face_center_outward_dot':values}
 if obj.name.startswith('KIT_pavilion_water_tiles'):
  assert len(mesh.vertices)==16 and len(mesh.polygons)==10 and all(v>0 for v in values),obj.name
  first=[v.co for v in list(mesh.vertices)[:8]];second=[v.co for v in list(mesh.vertices)[8:]]
  a=sum(first,Vector())/8;b=sum(second,Vector())/8
  row.update(radius_metres=float((first[0]-a).length),length_metres=float((b-a).length))
  assert abs(row['radius_metres']-.018)<1e-6,obj.name
 rows.append(row)
assert len([r for r in rows if r['name'].startswith('KIT_pavilion_water_tiles')])==168
assert len(rows)==169 and sum(r['triangles'] for r in rows)==4730
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
report={'status':'saved_oux_geometry_inspected','source_authoring_sha256':digest,'scope':'Saved object names, world-space vertices and closed-cylinder outward face-center dots. No save, UV allocation, lighting or rendered acceptance.','objects':rows}
(out/'source-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print('OUX_SOURCE_GEOMETRY_PASS',len(rows),'objects, 168 outward closed eight-sided cylinders')
