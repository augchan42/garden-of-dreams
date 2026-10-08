from pathlib import Path
import bpy,hashlib,json
root=Path('/Users/auchan/projects/garden-of-dreams')
out=Path('/tmp/garden-saved-kit-export-probe');out.mkdir(exist_ok=True)
source=root/'blender/kits/KIT_pavilion.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.context.window.scene=bpy.data.scenes['Pavilion bench']
bpy.context.view_layer.update()
path=out/'KIT_pavilion_bench.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_loglevel=-1)
a=root/'export/kits/pavilion'/path.name
r={'status':'readonly_saved_export_probe','source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==before,'byte_equal':a.read_bytes()==path.read_bytes(),'before_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('SAVED_KIT_EXPORT_PROBE',r)
