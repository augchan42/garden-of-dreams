extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 if not route.ROOMS.has("daoxiang_cun"):
  push_error("Farmhouse courtyard route is missing")
  quit(1)
  return
 route.player.position=Vector3(-18,.04,-14.7)
 route._arrive("hengwu_yuan",true)
 for leg in [["farm","daoxiang_cun"],["back","hengwu_yuan"]]:
  route.execute_command(leg[0])
  if not route.travelling:
   push_error("Farmhouse court route did not begin")
   quit(1)
   return
  for i in range(3600):
   await physics_frame
   if route.player.position.y < -.3:
    push_error("Farmhouse path lost floor support")
    quit(1)
    return
   if not route.travelling:break
  if route.room_id!=leg[1]:
   push_error("Farmhouse path failed at "+str(route.player.position))
   quit(1)
   return
  if leg[1]=="daoxiang_cun":
   route.execute_command("doors")
   assert("closed" in route.output_label.text)
   route.execute_command("enter")
   assert(not route.travelling and route.room_id=="daoxiang_cun")
   var query=PhysicsRayQueryParameters3D.create(Vector3(-32,1.4,-21),Vector3(-32,1.4,-23))
   var hit=route.get_world_3d().direct_space_state.intersect_ray(query)
   if hit.is_empty() or not "daoxiang_closed_front" in str(hit.collider.name):
    push_error("The closed ceremonial door has no blocking collider")
    quit(1)
    return
 print("FARMHOUSE_ROUTE_PASS: both directions, floor support, closed-door collision and no entry action")
 quit(0)
