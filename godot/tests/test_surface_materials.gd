extends SceneTree
func _initialize():call_deferred("run")
func run():
 var scene=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(scene)
 var fog=load("res://materials/stage/fog.tres")
 var nodes:Array[Node]=[scene]
 var counts={"MAT_water":0,"MAT_aojing_water":0,"stage_fog":0}
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D:
   for i in range(node.mesh.get_surface_count()):
    var original=node.mesh.surface_get_material(i)
    var key="stage_fog" if original==fog else (original.resource_name if original else "")
    if key in counts:
     var material=node.get_active_material(i)
     var expected_shader=load("res://shaders/floor_fog.gdshader") if key=="stage_fog" else load("res://shaders/pond_reflection.gdshader") if key=="MAT_aojing_water" else load("res://shaders/water.gdshader")
     if not material is ShaderMaterial or material.shader!=expected_shader:
      push_error("Animated surface missing after full bake application: "+key)
      quit(1)
      return
     counts[key]+=1
 if counts.MAT_aojing_water!=1 or counts.MAT_water<1 or counts.stage_fog<1:
  push_error("Water/fog surfaces were not checked")
  quit(1)
  return
 print("SURFACE_MATERIAL_PASS ",counts)
 quit(0)
