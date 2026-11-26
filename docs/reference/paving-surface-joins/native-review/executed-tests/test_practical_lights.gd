extends SceneTree
func _initialize() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await process_frame
 if not route.has_node("PracticalLights"):
  push_error("Practical light budget manager missing")
  quit(1)
  return
 var manager=route.get_node("PracticalLights")
 for point in [Vector3(-1.3,0,37.4),Vector3(0,0,25),Vector3(0,0,1.8),Vector3(-23,0,0),Vector3(22,0,-13.5)]:
  route.player.position=point
  manager.update_lights()
  var active=0
  var expected:Array=[]
  for light in manager.lights:
   if light.global_position.distance_to(point)<=manager.activation_distance:
    expected.append(light)
  expected.sort_custom(func(a,b):return a.global_position.distance_squared_to(point)<b.global_position.distance_squared_to(point))
  expected.resize(mini(4,expected.size()))
  for light in manager.lights:
   if light.visible:active+=1
   if light.visible != expected.has(light) or light.shadow_enabled:
    push_error("Wrong practical selected or shadow enabled")
    quit(1)
    return
  if active>4:
   push_error("Practical budget exceeded")
   quit(1)
   return
 print("PRACTICAL_LIGHT_PASS: nearest four within range, no practical shadows")
 quit(0)
