import bpy,json,hashlib,tempfile
from pathlib import Path
repo=Path('/Users/auchan/projects/garden-of-dreams');source=repo/'blender/authoring.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(source)
assert before=='19eb386d8e93007ebd8e4ae2d9ee59ec7daa07dcd8dbe3c3a88d4ec84b5e5a08'
w=Path(tempfile.mkdtemp(prefix='garden-ziling-source-art-'));Path('/tmp/garden-ziling-source-art.json').write_text(json.dumps({'root':str(w)})+'\n')
bpy.ops.wm.open_mainfile(filepath=str(source));scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene;deps=bpy.context.evaluated_depsgraph_get()
rows=[]
for o in scene.objects:
 if o.type!='MESH':continue
 materials=[m.name if m else None for m in o.data.materials]
 if not (any('ziling' in c.name for c in o.users_collection) or 'MAT_water' in materials or 'MAT_aojing_water' in materials or o.get('kit_part')=='lotus'):continue
 ev=o.evaluated_get(deps);m=ev.to_mesh();points=[o.matrix_world@v.co for v in m.vertices]
 rows.append({'name':o.name,'data':o.data.name,'collections':[c.name for c in o.users_collection],'materials':materials,'location':list(o.location),'matrix_world':[[*row] for row in o.matrix_world],'vertices':len(m.vertices),'triangles':sum(len(p.vertices)-2 for p in m.polygons),'uv_layers':[v.name for v in m.uv_layers],'hidden':o.hide_render,'extras':{k:str(v) for k,v in o.items()},'bounds_z_up':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]});ev.to_mesh_clear()
material_rows={}
for name in ['MAT_water','MAT_aojing_water','MAT_flora_atlas','MAT_plaster_rock']:
 m=bpy.data.materials[name];bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 material_rows[name]={'diffuse_color':list(m.diffuse_color),'inputs':{name:{'value':list(bsdf.inputs[name].default_value) if hasattr(bsdf.inputs[name].default_value,'__iter__') else bsdf.inputs[name].default_value,'linked':bsdf.inputs[name].is_linked} for name in ['Base Color','Roughness','Metallic','Alpha','Emission Color','Emission Strength']},'images':[n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]}
assert sha(source)==before
(w/'saved-source-inventory.json').write_text(json.dumps({'status':'readonly_saved_source_inspected','authoring_sha256':before,'source_glb_sha256':sha(repo/'export/garden-of-dreams.glb'),'objects':rows,'materials':material_rows,'scope':'Actual saved source; live MCP scene has older legacy reeds and is preserved unchanged. No source edits or candidate saved yet.'},indent=2)+'\n')
print('ZILING_SOURCE_INSPECTED',w,len(rows))
for row in rows:
 if row['name'] in ['SITE_ziling_island','SITE_ziling_stone_landing','COL_ziling_landing'] or 'MAT_water' in row['materials'] or row['name'].startswith('HERO_flora_ziling'):print(row['name'],row['bounds_z_up'],row['triangles'],row['materials'])
