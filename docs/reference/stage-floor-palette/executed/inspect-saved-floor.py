"""Read the actual saved canvas floor without changing Blender data."""
from pathlib import Path
import hashlib
import json
import bpy
from mathutils import Vector

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = repo / '.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette'
expected = '2b07ce48ffa3011f9a2da01535a3fc84171bdc00b2ced2abad0ce8f338fd49ed'
source = Path(bpy.data.filepath)
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
material = bpy.data.materials['MAT_stage_canvas']
principled = [node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED']
assert len(principled) == 1
rows = []
for obj in sorted(bpy.data.objects, key=lambda o: o.name):
    if obj.type != 'MESH' or material not in list(obj.data.materials):
        continue
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    rows.append({'name': obj.name, 'collections': [c.name for c in obj.users_collection],
                 'vertices': len(obj.data.vertices), 'faces': len(obj.data.polygons),
                 'bounds_z_up': [[min(p[i] for p in points) for i in range(3)],
                                 [max(p[i] for p in points) for i in range(3)]],
                 'materials': [m.name for m in obj.data.materials],
                 'top_faces': [p.index for p in obj.data.polygons if p.normal.z > .9]})
assert rows
floor = bpy.data.objects.get('SITE_stage_floor')
black = {'name': floor.name, 'materials': [m.name for m in floor.data.materials]} if floor else None
report = {'status': 'actual_saved_canvas_floor_inspected_no_mutation',
          'source_authoring_sha256': expected,
          'material': material.name,
          'base_color': list(principled[0].inputs['Base Color'].default_value),
          'diffuse_color': list(material.diffuse_color),
          'base_color_linked': principled[0].inputs['Base Color'].is_linked,
          'roughness': principled[0].inputs['Roughness'].default_value,
          'texture_nodes': [{'name': n.name, 'image': n.image.name if n.image else None}
                            for n in material.node_tree.nodes if n.type == 'TEX_IMAGE'],
          'users': rows, 'black_stage_floor': black,
          'scope': 'Actual saved floor material/object identification for the next reduced-green art pass. No palette candidate, source save, native appearance or final-site acceptance.'}
work.mkdir(parents=True, exist_ok=True)
(work / 'saved-floor-inspection.json').write_text(json.dumps(report, indent=2) + '\n')
print('SAVED_CANVAS_FLOOR_INSPECTED', len(rows), 'objects;', report['base_color'], flush=True)
