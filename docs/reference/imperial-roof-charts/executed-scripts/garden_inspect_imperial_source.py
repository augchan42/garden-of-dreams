"""Read saved imperial roof source geometry; never save the scene."""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT=Path('/Users/auchan/projects/garden-of-dreams')
out=Path(json.loads(Path('/tmp/garden-imperial-roof-probe.json').read_text())['folder'])
source=ROOT/'blender/authoring.blend'
original=hashlib.sha256(source.read_bytes()).hexdigest()
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
bpy.context.view_layer.update()
collection=bpy.data.collections['SITE_daguan-lou']
rows=[]
for obj in sorted(collection.objects,key=lambda o:o.name):
    if obj.type!='MESH' or not (obj.name.startswith('DAGUAN_tile_strip') or obj.name in ['DAGUAN_lower_roof','DAGUAN_upper_roof']):
        continue
    mesh=obj.data
    positions=[tuple(obj.matrix_world@v.co) for v in mesh.vertices]
    # For a closed cylinder, each face's geometric normal must point away
    # from its center. World-space normals include the actual saved transform.
    center=sum((Vector(v) for v in positions),Vector())/len(positions)
    normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
    values=[float((normal_matrix@p.normal).normalized().dot(obj.matrix_world@p.center-center)) for p in mesh.polygons]
    row={'name':obj.name,'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),
         'triangles':sum(len(p.vertices)-2 for p in mesh.polygons),
         'material_names':[m.name for m in mesh.materials],
         'world_positions_z_up':positions,'face_center_outward_dot':values}
    if obj.name.startswith('DAGUAN_tile_strip'):
        assert len(mesh.vertices)==16 and len(mesh.polygons)==10
        assert all(v>0 for v in values),'Inward cylinder face'
        first=[v.co for v in list(mesh.vertices)[:8]]
        second=[v.co for v in list(mesh.vertices)[8:]]
        a=sum(first,Vector())/8;b=sum(second,Vector())/8
        row.update(radius_metres=float((first[0]-a).length),length_metres=float((b-a).length))
        assert abs(row['radius_metres']-.022)<1e-6
    rows.append(row)
assert len([r for r in rows if r['name'].startswith('DAGUAN_tile_strip')])==576
assert len(rows)==578
assert hashlib.sha256(source.read_bytes()).hexdigest()==original
report={'status':'saved_imperial_geometry_inspected','source_authoring_sha256':original,
        'scope':'Exact saved world-space source vertices and closed-cylinder face-center normal dots. No save, UV allocation, lighting or rendered acceptance.',
        'objects':rows}
(out/'source-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
print('IMPERIAL_SOURCE_GEOMETRY_PASS',len(rows),'objects, 576 outward closed eight-sided cylinders')
