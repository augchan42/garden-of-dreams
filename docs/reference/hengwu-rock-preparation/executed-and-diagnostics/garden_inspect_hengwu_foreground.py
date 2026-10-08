import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('/Users/auchan/projects/garden-of-dreams');source=root/'blender/authoring.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
site=scene.collection.children['SITE_hengwu-yuan'];deps=bpy.context.evaluated_depsgraph_get()
objects=[]
for o in site.all_objects:
 if o.type!='MESH' or o.hide_render or o.name.startswith('COL_'):continue
 evaluated=o.evaluated_get(deps);mesh=evaluated.to_mesh()
 vertices=[o.matrix_world@v.co for v in mesh.vertices]
 objects.append({'name':o.name,'materials':[m.name if m else None for m in mesh.materials],'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'bounds':[[min(v[i] for v in vertices) for i in range(3)],[max(v[i] for v in vertices) for i in range(3)]],'location':list(o.location),'scale':list(o.scale)})
 evaluated.to_mesh_clear()
points=[[-16.023136065877704,12.353960053640897,2.590962463192585],[-13.670000076293945,17.111032389271664,2.760179909113193],[-16.15131575767003,12.181222552414,2.1132614443378412]]
nearest=[]
for point in points:
 matches=[]
 for o in site.all_objects:
  if o.type!='MESH' or o.hide_render or o.name.startswith('COL_'):continue
  tree=BVHTree.FromObject(o,deps);local=o.matrix_world.inverted()@Vector(point);result=tree.find_nearest(local)
  if result[0] is not None:
   distance=(o.matrix_world@result[0]-Vector(point)).length
   if distance<.01:matches.append({'object':o.name,'world_distance_m':distance,'polygon':result[2]})
 nearest.append({'world_point_source_z_up':point,'objects_on_sample_surface':matches})
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report={'status':'readonly_saved_hengwu_foreground_inspected','authoring_sha256':before,'objects':objects,'sample_surface_identity':nearest,'scope':'Read-only actual saved source inspection; closest surface matches native/CPU sampled locations, no edits or exports.'}
Path('/tmp/garden-hengwu-saved-foreground.json').write_text(json.dumps(report,indent=2)+'\n')
print('HENGWU_SOURCE_FOREGROUND_INSPECTED',len(objects));print(json.dumps(nearest,indent=2))
