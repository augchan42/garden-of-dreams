import bpy,sys,pathlib,json,hashlib,collections
root=pathlib.Path('/Users/auchan/projects/garden-of-dreams');sys.path.insert(0,str(root/'scripts'))
from pavilion_roof_geometry import components,outer_shell
out=pathlib.Path('/tmp/garden-native-roof-components.json');obj=bpy.data.objects['QINFANG_kit_roof_hex'];mesh=obj.data
assert hashlib.sha256((root/'blender/authoring.blend').read_bytes()).hexdigest()=='a273a4c0ea33c9897f3096f51b5833b905e04a6d0ca62cab001e8291aa93b8de'
parts=[]
for vertices,faces in components(mesh):
 z=[mesh.vertices[i].co.z for i in vertices];weight=sum(p.area for p in faces)
 parts.append({'vertices':len(vertices),'faces':len(faces),'min_z':min(z),'max_z':max(z),'normal_z_min':min(p.normal.z for p in faces),'normal_z_max':max(p.normal.z for p in faces),'area':weight,'area_weighted_normal_z':sum(p.normal.z*p.area for p in faces)/weight,'negative_normal_faces':sum(p.normal.z<-.05 for p in faces),'positive_normal_faces':sum(p.normal.z>.05 for p in faces),'face_indices':[p.index for p in faces],'vertex_indices':sorted(vertices),'material_indices':sorted({p.material_index for p in faces})})
shell=outer_shell(mesh)
report={'status':'inspected_saved_source','source_authoring_sha256':hashlib.sha256((root/'blender/authoring.blend').read_bytes()).hexdigest(),'object':obj.name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'materials':[m.name for m in mesh.materials],'matrix':[list(row) for row in obj.matrix_world],'shell_faces':[p.index for p in shell],'components':parts,'scope':'Native saved-source disconnected roof components/normals only. No source modification or rendered art acceptance.'}
out.write_text(json.dumps(report,indent=2)+'\n')
summary=collections.defaultdict(list)
for p in parts:summary[(p['vertices'],p['faces'])].append(p)
for k,group in summary.items():print('ROOF_COMPONENT_GROUP',k,'count',len(group),'normalsZ',[(round(p['normal_z_min'],4),round(p['normal_z_max'],4),p['negative_normal_faces']) for p in group][:5],flush=True)
print('NATIVE_ROOF_COMPONENTS_PASS',len(parts),len(shell),flush=True)
