import bpy, io_scene_gltf2
from pathlib import Path
R=Path('/Users/auchan/projects/garden-of-dreams')
generated=0
for path in sorted((R/'export/kits').glob('KIT_*.glb')):
 if '_LOD1' in path.stem:continue
 if (R/'export/kits'/path.stem.removeprefix('KIT_')/'manifest.json').exists():continue
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(path))
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and not o.name.startswith('COL_') and len(o.data.polygons)>6:
   mod=o.modifiers.new('LOD1_40_percent','DECIMATE');mod.ratio=.4;o['lod_ratio']=.4
 fmt=next(i[0] for i in io_scene_gltf2.get_format_items(None,bpy.context) if i[0]=='GLB')
 bpy.ops.export_scene.gltf(filepath=str(path.with_stem(path.stem+'_LOD1')),export_format=fmt,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False)
 generated+=1
print('Generated',generated,'fallback LODs; completed kit manifests preserved')
