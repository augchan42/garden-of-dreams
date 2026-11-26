import bpy,sys,hashlib
from pathlib import Path
r=Path('/tmp/garden-stage-kit-atlas-20261011');sys.path.insert(0,str(r/'candidate/scripts'))
from stage_kit_export_texture import exported_stage_paints
bpy.ops.wm.open_mainfile(filepath=str(r/'candidate/blender/kits/KIT_stage.blend'))
materials=[m for m in bpy.data.materials if m.name.startswith('MAT_stage_cyclorama_')]
originals={n:n.image for m in materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE'}
packed={i:hashlib.sha256(i.packed_file.data).hexdigest() for i in originals.values()}
try:
 with exported_stage_paints(materials):
  assert all(tuple(n.image.size)==(2048,2048) for n in originals)
  raise RuntimeError('Injected export failure')
except RuntimeError as error:assert str(error)=='Injected export failure'
assert all(n.image==i and tuple(i.size)==(4096,4096) for n,i in originals.items())
assert all(hashlib.sha256(i.packed_file.data).hexdigest()==h for i,h in packed.items())
assert not any('.export2048' in i.name for i in bpy.data.images)
print('STAGE_EXPORT_EXCEPTION_CLEANUP_PASS',len(materials))
