import bpy,json,hashlib
from pathlib import Path
w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root']);source=w/'reeds-volume/blender/kits/KIT_flora.blend';out=w/'flora-saved-source-reexports-updated';assert not out.exists();out.mkdir();original=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source))
for variant in ['bamboo_small','bamboo_medium','bamboo_large','plum','willow','banana','reed','potted']:
 for suffix in ['', '_LOD1']:
  bpy.context.window.scene=bpy.data.scenes['Flora '+variant+(' LOD1' if suffix else '')]
  bpy.context.view_layer.update()
  path=out/('KIT_flora_'+variant+suffix+'.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
  assert path.read_bytes()==(w/'reeds-volume/export/kits/flora'/path.name).read_bytes(),path.name
assert hashlib.sha256(source.read_bytes()).hexdigest()==original
(out/'report.json').write_text(json.dumps({'status':'all16saved_flora_exports_byte_exact','saved_source_sha256':original,'exports':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.glb'))}},indent=2)+'\n');print('SAVED_FLORA_REEXPORT_PASS_16')
