from pathlib import Path
p=Path('/tmp/garden_render_stream_waterline.gd');s=p.read_text().replace('var route\n','var route\nvar forced_lod:=false\n');s=s.replace(' if DisplayServer.get_name()', '  if arg=="--force-lod":forced_lod=true\n if DisplayServer.get_name()',1)
s=s.replace(' var waters:Array=[];', ''' if forced_lod:
  route.get_node("FloraLOD").set_process(false)
  for plant in route.get_node("FloraLOD").plants:
   if str(plant.node.name).begins_with("HERO_flora_ziling"):plant.node.mesh=plant.lower
 var waters:Array=[];''')
s=s.replace('"actual_stream_bounds_y_up":[low,high]', '"forced_reed_lod1":forced_lod,"actual_stream_bounds_y_up":[low,high]')
s=s.replace('res://tests/render_stream_waterline.gd','res://tests/render_reed_candidate.gd').replace('STREAM_WATERLINE_NATIVE_RESULT','REED_NATIVE_RESULT')
s=s.replace('Geometry comparison only, not fresh lighting','Full or explicitly forced reed LOD1 geometry comparison only, not fresh lighting');Path('/tmp/garden_render_reed_candidate.gd').write_text(s)
