"""Add matched chair collision at the six placed terminal seats."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=s
col=bpy.data.collections['SITE_terminal-cells']
for o in list(col.objects):
 if o.get('terminal_chair_collision'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(R/'blender/kits/KIT_props.blend'),link=False) as (src,dst):dst.collections=['KIT_props_folding_chair']
proxies=[o for o in dst.collections[0].objects if o.name.startswith('COL_')]
chairs=[o for o in col.objects if o.get('prop_variant')=='folding_chair'];assert len(chairs)==6 and len(proxies)==2
for index,chair in enumerate(chairs):
 for j,proxy in enumerate(proxies):
  o=proxy.copy();o.data=proxy.data;o.parent=None;o.name='COL_terminal_chair_'+str(index)+'_'+str(j);o.matrix_basis=chair.matrix_basis@proxy.matrix_basis;o.hide_render=True;o.hide_viewport=True;o['terminal_chair_collision']=True;col.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
bpy.data.libraries.write(str(R/'blender/sites/SITE_terminal-cells.blend'),{col},fake_user=True,compress=True)
print('TERMINAL_CHAIR_COLLISIONS_PASS',len(chairs)*len(proxies))
