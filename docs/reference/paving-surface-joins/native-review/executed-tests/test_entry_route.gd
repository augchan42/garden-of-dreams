extends SceneTree

func _initialize() -> void:
 if not ResourceLoader.exists("res://runtime/entry_route.tscn"):
  push_error("Entry route scene is missing")
  quit(1)
  return
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await process_frame
 await physics_frame
 var rock_shapes=0
 for shape in route.find_children("*","CollisionShape3D",true,false):
  if "COL_GATE_kit_" in str(shape.get_parent().name):rock_shapes+=1
 assert(rock_shapes==8,"Expected four tunnel segments, two arches and two cliffs")
 var space=route.get_world_3d().direct_space_state
 var obscured=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(0,1.65,32.3),Vector3(0,1.65,18)))
 assert(not obscured.is_empty() and "COL_GATE_kit_tunnel" in str(obscured.collider.name),"Tunnel bends must hide the exit from the entrance")
 var reveal=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(0,1.65,17.5),Vector3(0,1.65,8)))
 assert(reveal.is_empty(),"The exit must have a clear view along the pavilion approach")
 assert(route.room_id == "terminal_room", "Must start in the personal cell")
 route.execute_command("nonsense")
 assert(route.room_id == "terminal_room", "Unknown commands must not move the player")
 route.execute_command("exit")
 assert(route.travelling, "Exit must start movement")
 route.execute_command("exit")
 for i in range(3600):
  await physics_frame
  if not route.travelling: break
 assert(route.room_id == "rockery_gate", "Physics route must reach the gate")
 assert(route.player.position.y > -0.3, "Player must stay on the floor")
 route.execute_command("enter")
 for i in range(3600):
  await physics_frame
  if not route.travelling: break
 assert(route.room_id == "qinfang_ting", "Tunnel route must reach the pavilion")
 route.execute_command("back")
 for i in range(3600):
  await physics_frame
  if not route.travelling: break
 assert(route.room_id == "rockery_gate", "Return from pavilion must work")
 route.execute_command("back")
 for i in range(3600):
  await physics_frame
  if not route.travelling: break
 assert(route.room_id == "terminal_room", "Return to cell must work")
 print("ENTRY_ROUTE_PASS: commands, both-direction physics traversal, floor support")
 quit(0)
