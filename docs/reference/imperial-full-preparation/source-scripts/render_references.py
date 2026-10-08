import bpy
from pathlib import Path
R=Path('/Users/auchan/projects/garden-of-dreams');s=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=s
s.render.resolution_x=1410;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for name,cam in [('look-test-01','CAM_stage_wide'),('garden-overview','CAM_garden_overview'),('terminal-cells','CAM_cell_entry'),('rockery-reveal','CAM_gate_reveal'),('qiushuang-zhai','CAM_qiushuang-zhai_wide')]:
 s.camera=next(o for o in s.objects if o.name==cam);s.render.filepath=str(R/'docs/reference'/(name+'-raw.png'));bpy.ops.render.render(write_still=True)
print('Five references rendered')
