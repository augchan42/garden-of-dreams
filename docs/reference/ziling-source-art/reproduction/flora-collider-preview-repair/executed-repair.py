import bpy,json,hashlib,shutil
from pathlib import Path
w=Path('/Users/auchan/projects/garden-of-dreams/.superpowers/sdd/2026-09-23-garden-completion/ziling-source-art')
out=w/'flora-collider-preview-repair';assert not out.exists();out.mkdir()
source=w/'reeds-volume/blender/kits/KIT_flora.blend';target=out/'KIT_flora.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source_hash=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source))
def snapshot():
 objects={}
 for o in bpy.data.objects:
  row={'type':o.type,'basis':[list(x) for x in o.matrix_basis],'parent':o.parent.name if o.parent else None,'extras':{k:str(v) for k,v in o.items()},'hide_render':o.hide_render,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None}
  if o.type=='MESH':row.update(vertices=[list(v.co) for v in o.data.vertices],edges=[list(e.vertices) for e in o.data.edges],polygons=[list(p.vertices) for p in o.data.polygons],material_indices=[p.material_index for p in o.data.polygons],uv={l.name:[list(v.uv) for v in l.data] for l in o.data.uv_layers})
  if o.type=='CAMERA':row['camera']=[o.data.type,o.data.lens,o.data.clip_start,o.data.clip_end]
  if o.type=='LIGHT':row['light']=[o.data.type,o.data.energy,list(o.data.color)]
  objects[o.name]=row
 return {'objects':objects,'scenes':{s.name:{'objects':sorted(o.name for o in s.objects),'camera':s.camera.name if s.camera else None,'world':s.world.name if s.world else None} for s in bpy.data.scenes},'images':{i.name:sha_bytes(i.packed_file.data) for i in bpy.data.images if i.packed_file}}
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
before=snapshot();flags={o.name:{'hide_viewport':o.hide_viewport,'display_type':o.display_type,'hide_render':o.hide_render} for o in bpy.data.objects}
changed=[]
for obj in bpy.data.objects:
 if not obj.name.startswith('COL_'):continue
 assert obj.hide_viewport and obj.hide_render
 obj.hide_viewport=False;obj.display_type='WIRE';changed.append(obj.name)
assert len(changed)==6 and snapshot()==before
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(target));assert snapshot()==before
for obj in bpy.data.objects:
 if obj.name in changed:assert not obj.hide_viewport and obj.hide_render and obj.display_type=='WIRE'
 else:assert {'hide_viewport':obj.hide_viewport,'display_type':obj.display_type,'hide_render':obj.hide_render}==flags[obj.name]
exports=out/'default-reexports';exports.mkdir();records={}
for variant in ['bamboo_small','bamboo_medium','bamboo_large','plum','willow','banana','reed','potted']:
 for suffix in ['', '_LOD1']:
  bpy.context.window.scene=bpy.data.scenes['Flora '+variant+(' LOD1' if suffix else '')]
  path=exports/('KIT_flora_'+variant+suffix+'.glb')
  bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
  assert path.read_bytes()==(w/'reeds-volume/export/kits/flora'/path.name).read_bytes(),path.name
  records[path.name]=sha(path)
assert sha(source)==source_hash
(out/'repair-report.json').write_text(json.dumps({'status':'saved_reopened_library_default_all16exports_byte_exact','source_sha256':source_hash,'repaired_source_sha256':sha(target),'changed_viewport_objects':changed,'before_preview_flags':{n:flags[n] for n in changed},'preserved_snapshot_sha256':sha_bytes(json.dumps(before,sort_keys=True).encode()),'exports':records,'scope':'Six collider viewport flags/display modes change; render-hidden state, local transforms, all geometry/UV/material slots/images/cameras/lights/scene memberships preserved and all16default reexports exact. Original baked authoring/source/frozen kit unchanged.'},indent=2)+'\n')
shutil.copyfile(__file__,out/'executed-repair.py')
print('FLORA_COLLIDER_PREVIEW_REPAIR_PASS_16')
