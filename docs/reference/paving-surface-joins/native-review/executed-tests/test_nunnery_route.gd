extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 if not route.ROOMS.has("longcui_an"):
  push_error("Nunnery courtyard route is missing")
  quit(1)
  return
 route.player.position=Vector3(-23,.04,0)
 route._arrive("ouxiang_xie",true)
 for leg in [["nunnery","longcui_an"],["back","ouxiang_xie"]]:
  route.execute_command(leg[0])
  if not route.travelling:
   push_error("Nunnery court route did not begin")
   quit(1)
   return
  for i in range(3600):
   await physics_frame
   if route.player.position.y < -.3:
    push_error("Nunnery path lost floor support")
    quit(1)
    return
   if not route.travelling:break
  if route.room_id!=leg[1]:
   push_error("Nunnery path failed at "+str(route.player.position))
   quit(1)
   return
  if leg[1]=="longcui_an":
   route.execute_command("doors")
   assert("closed" in route.output_label.text)
   route.execute_command("enter")
   assert(not route.travelling and route.room_id=="longcui_an")
   var query=PhysicsRayQueryParameters3D.create(Vector3(-25,1.4,12),Vector3(-25,1.4,14))
   var hit=route.get_world_3d().direct_space_state.intersect_ray(query)
   if hit.is_empty() or not "longcui_closed_front" in str(hit.collider.name):
    push_error("The closed ceremonial door has no blocking collider")
    quit(1)
    return
 print("NUNNERY_ROUTE_PASS: both directions, floor support, closed-door collision and no entry action")
 quit(0)
