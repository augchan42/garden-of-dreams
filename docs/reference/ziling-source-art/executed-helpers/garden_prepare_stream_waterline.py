import bpy,hashlib,json,runpy,sys
from pathlib import Path
repo=Path('/Users/auchan/projects/garden-of-dreams');work=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root']);source=repo/'blender/authoring.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();baseline='19eb386d8e93007ebd8e4ae2d9ee59ec7daa07dcd8dbe3c3a88d4ec84b5e5a08';assert sha(source)==baseline
(work/'waterline/blender').mkdir(parents=True);(work/'waterline/export').mkdir();candidate=work/'waterline'
bpy.ops.wm.open_mainfile(filepath=str(source));scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
stream=bpy.data.objects['KIT_water_stream'];lotus=[o for o in scene.objects if o.get('kit_part')=='lotus'];assert len(lotus)==6
allowed={stream.name}|{o.name for o in lotus}
def signature(o):
 d={'name':o.name,'type':o.type,'matrix':[[*r] for r in o.matrix_world],'extras':{k:str(v) for k,v in o.items()},'hidden':[o.hide_render,o.hide_viewport],'data':o.data.name if o.data else None}
 if o.type=='MESH':d.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],indices=[p.material_index for p in o.data.polygons],materials=[m.name if m else None for m in o.data.materials],uvs={l.name:[list(x.uv) for x in l.data] for l in o.data.uv_layers})
 if o.type=='LIGHT':d.update(light_type=o.data.type,color=list(o.data.color),energy=o.data.energy)
 if o.type=='CAMERA':d.update(camera_type=o.data.type,lens=o.data.lens,sensor=o.data.sensor_width)
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
before={o.name:signature(o) for o in scene.objects};old_mats={m.name:m.diffuse_color[:] for m in bpy.data.materials}
old_stream=[list(v.co) for v in stream.data.vertices];old_lotus={o.name:list(o.location) for o in lotus}
# Raising the stream brings its surface 0.30m below the stone top. The dedicated
# reflection pond remains at its authored elevation; all walking meshes stay fixed.
stream.location.z+=.7
for o in lotus:o.location.z+=.7
colors={'MAT_water':(.25,.32,.4,1),'MAT_aojing_water':(.022,.03,.04,1)}
for name,value in colors.items():
 m=bpy.data.materials[name];bsdf=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');assert not bsdf.inputs['Base Color'].is_linked;m.diffuse_color=value;bsdf.inputs['Base Color'].default_value=value;bsdf.inputs['Emission Color'].default_value=value
bpy.context.view_layer.update();after={o.name:signature(o) for o in scene.objects};assert before.keys()==after.keys();changed={n for n in before if before[n]!=after[n]};assert changed==allowed,changed
assert {m.name for m in bpy.data.materials if tuple(m.diffuse_color[:])!=tuple(old_mats[m.name])}==set(colors)
assert [list(v.co) for v in stream.data.vertices]==old_stream
for o in lotus:assert abs(o.location.z-old_lotus[o.name][2]-.7)<1e-6
assert signature(bpy.data.objects['AOJING_pond'])==before['AOJING_pond']
bpy.ops.wm.save_as_mainfile(filepath=str(candidate/'blender/authoring.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(candidate/'blender/authoring.blend'));scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene;assert {o.name:signature(o) for o in scene.objects}==after
(candidate/'source-review.json').write_text(json.dumps({'status':'isolated_stream_waterline_saved_reopened_source_preserved','baseline_authoring_sha256':baseline,'candidate_authoring_sha256':sha(candidate/'blender/authoring.blend'),'changed_objects':sorted(changed),'changed_materials':colors,'before_fingerprints':before,'after_fingerprints':after,'unchanged_objects':len(before)-len(changed),'stream_translation_z_m':.7,'lotus_translation_z_m':.7,'scope':'Only stream and six lotus objects translated vertically0.7m; two source water colors aligned with installed engine palette. All authored cameras/lights/markers/geometry/colliders/plant placement and dedicated pond elevation unchanged. No production edits or lighting/adoption acceptance.'},indent=2)+'\n')
assert sha(source)==baseline
sys.argv=['export_garden.py','--','--output-root',str(candidate)];runpy.run_path(str(repo/'scripts/export_garden.py'),run_name='__main__')
print('STREAM_WATERLINE_CANDIDATE_SAVED_EXPORTED',candidate)
