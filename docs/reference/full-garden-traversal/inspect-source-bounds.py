from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
r=Path('/Users/auchan/projects/garden-of-dreams');records=[]
s=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=s
bpy.context.view_layer.update()
exact=('entry_corridor','bridge_crosswalk','QINFANG_corridor_east_0','QINFANG_corridor_west_0','cell_floor','stage_cell_floor')
for o in s.objects:
 if o.type!='MESH' or not any(n in o.name for n in exact):continue
 xf=o.matrix_basis if not o.parent else o.parent.matrix_world@o.matrix_parent_inverse@o.matrix_basis
 points=[xf@Vector(c) for c in o.bound_box];bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
 records.append({'name':o.name,'collections':[c.name for c in o.users_collection],'bounds_source_z_up':bounds,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'matrix':list(map(list,xf)),'parent':o.parent.name if o.parent else None,'matrix_basis':list(map(list,o.matrix_basis)),'materials':[m.name if m else None for m in o.data.materials]})
report={'scope':'Read-only saved collision and visible floor bounds at the three independently observed physical seams. No source edits or renders.','authoring_sha256':hashlib.sha256((r/'blender/authoring.blend').read_bytes()).hexdigest(),'records':records};Path('/tmp/garden-floor-seam-source-inspection-v4.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
