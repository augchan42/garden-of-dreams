"""Store the runtime reveal's camera rail in the editable Blender site."""
import bpy,ast,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene
C=scene.collection.children['SITE_rockery-gate']
exec(compile(ast.Module(body=[n for n in ast.parse((R/'scripts/build_garden.py').read_text()).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for o in list(C.objects):
 if o.get('gate_reveal_rail'):bpy.data.objects.remove(o,do_unlink=True)
positions=[(-2.5,-16.7,1.8),(-3,-16,5.8),(10,-12,5.5)]
for i,(name,p) in enumerate(zip(['slide','lift','wide'],positions)):
 o=camera('CAM_gate_reveal_'+name,p,(0,0,1.8),35)
 o.data.sensor_fit=next(i.identifier for i in bpy.types.Camera.bl_rna.properties['sensor_fit'].enum_items if i.identifier=='VERTICAL')
 o.data.sensor_height=24
 o.data.lens=12/__import__('math').tan(__import__('math').radians(55)/2)
 o['gate_reveal_rail']=True;o['rail_order']=i
curve=bpy.data.curves.new('Gate reveal rail','CURVE');curve.dimensions='3D'
spline=curve.splines.new('POLY');spline.points.add(3)
for point,p in zip(spline.points,[(0,-17.35,1.6)]+positions):point.co=(*p,1)
o=bpy.data.objects.new('CAM_rail_gate_reveal',curve);C.objects.link(o);o['gate_reveal_rail']=True;o.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/authoring.blend'),compress=True)
file=R/'blender/sites/SITE_rockery-gate.blend';bpy.data.libraries.write(str(file),{C},fake_user=True,compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(file),link=False) as (src,dst):dst.collections=['SITE_rockery-gate']
s=bpy.context.scene;s.name='SITE_rockery-gate';s.collection.children.link(dst.collections[0]);s.unit_settings.system='METRIC'
s.render.resolution_x=1410;s.render.resolution_y=600;s.render.resolution_percentage=100
s.camera=next(o for o in s.objects if o.name.startswith('CAM_gate_reveal_wide'))
tmp=file.with_name(file.stem+'-packaged.blend');bpy.ops.wm.save_as_mainfile(filepath=str(tmp),compress=True);os.replace(tmp,file)
print('GATE_REVEAL_CAMERAS_SAVED: slide, lift, wide and editable rail curve')
