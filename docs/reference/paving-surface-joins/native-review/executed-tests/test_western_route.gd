extends SceneTree
func _initialize() -> void:
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await process_frame
 if not route.ROOMS.has("ouxiang_xie") or not route.ROOMS.has("ziling_zhou"):
  push_error("Western room actions missing")
  quit(1)
  return
 route.player.position = Vector3(0,.04,1.8)
 route._arrive("qinfang_ting",true)
 for step in [["west","ouxiang_xie"],["island","ziling_zhou"],["back","ouxiang_xie"],["back","qinfang_ting"]]:
  route.execute_command(step[0])
  for i in range(1800):
   await physics_frame
   if not route.travelling:break
  if route.room_id != step[1] or route.player.position.y < -.3:
   push_error("Western collision traversal failed: %s at %s" % [step,route.player.position])
   quit(1)
   return
 print("WESTERN_ROUTE_PASS: pavilion and island reached in both directions with floor support")
 quit(0)
