extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await process_frame
 var garden = route.get_node("GardenOfDreams")
 var wash = garden.get_node("BackdropWash")
 assert(wash is DirectionalLight3D)
 assert(wash.light_cull_mask == 4 and not wash.shadow_enabled)
 var receivers = 0
 var stack: Array[Node] = [garden]
 while not stack.is_empty():
  var node = stack.pop_back()
  stack.append_array(node.get_children())
  if node is MeshInstance3D and node.layers & 4:
   assert(str(node.name).begins_with("SITE_stage_MAT_cyclorama") or str(node.name).begins_with("SITE_stage_MAT_painted_mountains_") or str(node.name).begins_with("SITE_stage_MAT_painted_moon"))
   receivers += 1
 assert(receivers == 5)
 print("BACKDROP_WASH_PASS: five painted receivers, no building receivers")
 quit(0)
