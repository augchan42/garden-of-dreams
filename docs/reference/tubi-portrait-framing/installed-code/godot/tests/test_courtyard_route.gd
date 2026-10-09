extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await physics_frame
 var wall_shapes=0
 for shape in route.find_children("*","CollisionShape3D",true,false):
  if "COL_HENGWU_kit_" in str(shape.get_parent().name):wall_shapes+=1
 if wall_shapes!=9:
  push_error("Expected nine placed wall collisions, found "+str(wall_shapes));quit(1);return
 var space=route.get_world_3d().direct_space_state
 for segment in [[Vector3(-23,1.4,-14),Vector3(-22,1.4,-14)],
                 [Vector3(-13,1.4,-14),Vector3(-14,1.4,-14)],
                 [Vector3(-19.3,1.4,-9),Vector3(-19.3,1.4,-11)],
                 [Vector3(-16.7,1.4,-9),Vector3(-16.7,1.4,-11)]]:
  var hit=space.intersect_ray(PhysicsRayQueryParameters3D.create(segment[0],segment[1]))
  if hit.is_empty() or not "COL_HENGWU_kit_" in str(hit.collider.name):
   push_error("Courtyard window or gate pier lacks blocking collision");quit(1);return
 if not route.ROOMS.has("hengwu_yuan"):
  push_error("Study courtyard is missing")
  quit(1)
  return
 route.player.position=Vector3(0,.04,1.8)
 route._arrive("qinfang_ting",true)
 for leg in [["study","hengwu_yuan"],["back","qinfang_ting"]]:
  route.execute_command(leg[0])
  if not route.travelling:
   push_error("Courtyard command did not begin travel")
   quit(1)
   return
  for i in range(3600):
   await physics_frame
   if route.player.position.y < -.3:
    push_error("Courtyard approach lost floor support")
    quit(1)
    return
   if not route.travelling:break
  if route.room_id!=leg[1]:
   push_error("Courtyard traversal failed at "+str(route.player.position))
   quit(1)
   return
  if leg[1]=="hengwu_yuan":
   route.execute_command("rocks")
   assert("holes" in route.output_label.text)
   route.execute_command("read")
   assert("not connected" in route.output_label.text)
 print("COURTYARD_ROUTE_PASS: both-direction traversal, floor support and local inspection actions")
 quit(0)
