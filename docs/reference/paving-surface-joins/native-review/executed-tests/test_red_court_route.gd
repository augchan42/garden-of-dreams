extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 if not route.ROOMS.has("yihong_yuan"):
  push_error("Red courtyard route is missing")
  quit(1)
  return
 route.player.position=Vector3(0,.04,1.8)
 route._arrive("qinfang_ting",true)
 for leg in [["east","yihong_yuan"],["back","qinfang_ting"]]:
  route.execute_command(leg[0])
  if not route.travelling:
   push_error("Red court route did not begin")
   quit(1)
   return
  for i in range(3600):
   await physics_frame
   if route.player.position.y < -.3:
    push_error("East path lost floor support")
    quit(1)
    return
   if not route.travelling:break
  if route.room_id!=leg[1]:
   push_error("East path failed at "+str(route.player.position))
   quit(1)
   return
  if leg[1]=="yihong_yuan":
   route.execute_command("doors")
   assert("closed" in route.output_label.text)
   route.execute_command("enter")
   assert(not route.travelling and route.room_id=="yihong_yuan")
   var query=PhysicsRayQueryParameters3D.create(Vector3(24,1.4,1),Vector3(26,1.4,1))
   var hit=route.get_world_3d().direct_space_state.intersect_ray(query)
   if hit.is_empty() or not "yihong_closed_front" in str(hit.collider.name):
    push_error("The closed ceremonial door has no blocking collider")
    quit(1)
    return
 print("RED_COURT_ROUTE_PASS: both directions, floor support, closed-door collision and no entry action")
 quit(0)
