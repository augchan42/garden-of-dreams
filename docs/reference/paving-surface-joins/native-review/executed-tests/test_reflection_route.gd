extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 if not route.ROOMS.has("aojing_guan"):
  push_error("Reflection hall courtyard route is missing")
  quit(1)
  return
 route.player.position=Vector3(22.6,.04,1)
 route._arrive("yihong_yuan",true)
 for leg in [["pond","aojing_guan"],["back","yihong_yuan"]]:
  route.execute_command(leg[0])
  if not route.travelling:
   push_error("Reflection hall court route did not begin")
   quit(1)
   return
  for i in range(3600):
   await physics_frame
   if route.player.position.y < -.95:
    push_error("Reflection hall path lost floor support")
    quit(1)
    return
   if not route.travelling:break
  if route.room_id!=leg[1]:
   push_error("Reflection hall path failed at "+str(route.player.position))
   quit(1)
   return
  if leg[1]=="aojing_guan":
   assert(abs(route.player.position.y + .65) < .1)
   route.execute_command("doors")
   assert("closed" in route.output_label.text)
   route.execute_command("enter")
   assert(not route.travelling and route.room_id=="aojing_guan")
   var query=PhysicsRayQueryParameters3D.create(Vector3(26,.8,13),Vector3(26,.8,11))
   var hit=route.get_world_3d().direct_space_state.intersect_ray(query)
   if hit.is_empty() or not "aojing_closed_front" in str(hit.collider.name):
    push_error("The closed ceremonial door has no blocking collider")
    quit(1)
    return
 print("REFLECTION_ROUTE_PASS: both directions, floor support, closed-door collision and no entry action")
 quit(0)
