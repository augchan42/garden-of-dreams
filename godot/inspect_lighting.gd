extends SceneTree
func _initialize():
 var s=load('res://garden_preview.tscn').instantiate()
 var nodes=[s]
 while not nodes.is_empty():
  var n=nodes.pop_back()
  nodes.append_array(n.get_children())
  if n is Light3D: print(n.name,' energy=',n.light_energy,' physical=',n.light_intensity_lumens if n is OmniLight3D else 'other',' color=',n.light_color)
 s.free()
 quit()
