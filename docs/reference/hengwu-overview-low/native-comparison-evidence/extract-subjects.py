"""Read saved semantic objects without saving or reexporting Blender source."""
import bpy,json,hashlib
from pathlib import Path
root=Path('/tmp/garden-hengwu-arrival-20261010')
source=Path('/Users/auchan/projects/garden-of-dreams/blender/authoring.blend')
assert Path(bpy.data.filepath)==source
collection=bpy.data.collections['SITE_hengwu-yuan']
subjects={}
for obj in collection.objects:
    variant=obj.get('prop_variant','')
    if variant in ['stone_table','stone_stool']:
        label=variant+'-'+obj.name
    elif obj.name=='HENGWU_perforated_rock':label='primary-pierced-stone'
    elif obj.name=='HENGWU_open_book':label='open-book'
    else:continue
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    points=[]
    for vertex in mesh.vertices:
        world=obj.matrix_world@vertex.co
        points.append([world.x,world.z,-world.y])
    subjects[label]={'source_object':obj.name,'points':points,'materials':[m.name for m in obj.data.materials],
                     'variant':variant,'source_vertex_count':len(points)}
    evaluated.to_mesh_clear()
assert len(subjects)==7,subjects.keys()
assert sum(s['variant']=='stone_stool' for s in subjects.values())==4
record={'source_authoring_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'scope':'Evaluated saved semantic render vertices in Godot world coordinates; read-only, no source save/export.',
        'subjects':subjects}
(root/'godot/tests/hengwu-arrival-subjects.json').write_text(json.dumps(record,separators=(',',':'))+'\n')
print('HENGWU_SAVED_SUBJECTS',len(subjects),sum(len(r['points']) for r in subjects.values()))
