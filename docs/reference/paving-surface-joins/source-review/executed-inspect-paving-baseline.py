from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector

root=Path('/Users/auchan/projects/garden-of-dreams')
out=root/'.superpowers/sdd/2026-09-23-garden-completion/paving-site-joins'
source=Path(bpy.data.filepath)
digest=hashlib.sha256(source.read_bytes()).hexdigest()
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=scene
bpy.context.view_layer.update()
records=[]
for obj in scene.objects:
    if obj.type!='MESH' or obj.name.startswith('COL_') or obj.hide_render:
        continue
    top=[]
    for poly in obj.data.polygons:
        points=[obj.matrix_world@obj.data.vertices[i].co for i in poly.vertices]
        if len(points)!=4 or max(p.z for p in points)-min(p.z for p in points)>1e-5:
            continue
        if abs(points[0].z)>.006:
            continue
        normal=obj.matrix_world.to_3x3().inverted().transposed()@poly.normal
        if normal.z<.9:
            continue
        top.append({'polygon':poly.index,'xy':[list(p)[:2] for p in points],'height':points[0].z,'material':obj.data.materials[poly.material_index].name if obj.data.materials else None})
    if top:
        points=[obj.matrix_world@v.co for v in obj.data.vertices]
        records.append({'name':obj.name,'collections':[c.name for c in obj.users_collection],
                        'materials':[m.name for m in obj.data.materials],
                        'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]],
                        'top_faces':top})
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
report={'status':'readonly_current_saved_paving_inspected','authoring_sha256':digest,'objects':records,
        'scope':'Actual saved world-space upward four-corner surfaces near walking height; no edits, save or exports. Top polygons need intersection and native-visibility diagnosis.'}
(out/'saved-paving.json').write_text(json.dumps(report,indent=2)+'\n')
print('SAVED_PAVING_INSPECTED',len(records),flush=True)
