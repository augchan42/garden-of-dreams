"""Add one clipped canvas infill west of Aojing's pond in the isolated source."""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1];path=R/'blender/authoring.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=sha(path);assert base=='4eb31445889e5f30f57bb7935759d83169655eefea6c6cfa798879e9f384b0f6'
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene;bpy.context.view_layer.update();name='AOJING_ground_west_infill';assert name not in bpy.data.objects

def snapshot(obj):
 value={'type':obj.type,'matrix_world':[list(row) for row in obj.matrix_world],'matrix_basis':[list(row) for row in obj.matrix_basis],'hide_render':obj.hide_render,'hide_viewport':obj.hide_viewport,'collections':sorted(c.name for c in obj.users_collection),'properties':{k:str(v) for k,v in obj.items() if k!='_RNA_UI'}}
 if obj.type=='MESH':value['mesh']={'vertices':[list(v.co) for v in obj.data.vertices],'edges':[list(e.vertices) for e in obj.data.edges],'polygons':[(list(p.vertices),p.material_index,p.use_smooth) for p in obj.data.polygons],'materials':[m.name if m else None for m in obj.data.materials],'uv_layers':{layer.name:[list(v.uv) for v in layer.data] for layer in obj.data.uv_layers}}
 elif obj.type=='LIGHT':value['light']={k:str(getattr(obj.data,k,None)) for k in ['type','energy','color','angle','spot_size','spot_blend','shadow_soft_size','shape','size','size_y']}
 elif obj.type=='CAMERA':value['camera']={k:str(getattr(obj.data,k,None)) for k in ['type','lens','sensor_width','sensor_height','clip_start','clip_end','shift_x','shift_y','ortho_scale']}
 elif obj.type=='FONT':value['font']={'body':obj.data.body,'font':obj.data.font.filepath,'size':obj.data.size}
 return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
before={o.name:snapshot(o) for o in bpy.data.objects};canvas=bpy.data.materials['MAT_stage_canvas'];material_before={n.name:{i.name:str(i.default_value) for i in n.inputs if hasattr(i,'default_value')} for n in canvas.node_tree.nodes}
verts=[(x,y,z) for z in [-.63,-.13] for x,y in [(18,-21),(20.2,-21),(20.2,-14),(18,-14)]];faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
# Keep the same UV-free source convention as all five existing canvas users.
# Canonical batching initializes primary UVs for the complete joined canvas.
obj=bpy.data.objects.new(name,mesh);bpy.data.collections['SITE_stage'].objects.link(obj);mesh.materials.append(canvas);obj['stage_ground_infill']='aojing_west_strip';bpy.context.view_layer.update()
after={o.name:snapshot(o) for o in bpy.data.objects};assert set(after)-set(before)=={name} and set(before).issubset(after);assert all(after[n]==h for n,h in before.items())
assert material_before=={n.name:{i.name:str(i.default_value) for i in n.inputs if hasattr(i,'default_value')} for n in canvas.node_tree.nodes}
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
report={'status':'one_clipped_source_infill_added_original_objects_unchanged','base_authoring_sha256':base,'candidate_authoring_sha256':sha(path),'new_objects':[name],'unchanged_original_object_count':len(before),'unchanged_original_object_hashes':before,'material_nodes_unchanged':material_before,'patch_bounds_min_xyz':[18,-21,-.63],'patch_bounds_max_xyz':[20.2,-14,-.13],'top_area_m2':15.4,'scope':'One isolated source cube, existing canvas material. All original mesh topology/coordinates/primaryUV/material slots, transforms, collections/properties and light/camera/font fields checked unchanged in memory. Saved-source contract, canonical export, UV/lightmaps, collision/native rendering and final-art acceptance remain separate.'}
(R/'export/aojing-source-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print('AOJING_ISOLATED_SOURCE_INFILL_PASS',len(before))
