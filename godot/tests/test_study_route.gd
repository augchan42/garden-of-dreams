extends SceneTree
func _initialize() -> void:
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await process_frame
 if not route.ROOMS.has("qiushuang_zhai"):
  push_error("Study hall actions missing")
  quit(1)
  return
 route.player.position = Vector3(0,.04,1.8)
 route._arrive("qinfang_ting",true)
 for step in [["board","qiushuang_zhai"],["back","qinfang_ting"]]:
  route.execute_command(step[0])
  for i in range(2400):
   await physics_frame
   if not route.travelling:break
  if route.room_id != step[1] or route.player.position.y < -.3:
   push_error("Study traversal failed: %s at %s" % [step,route.player.position])
   quit(1)
   return
  if route.room_id == "qiushuang_zhai":
   for command in ["left","centre","right"]:
    route.execute_command(command)
    if not "not connected" in route.output_label.text:
     push_error("Unavailable board content must be labelled")
     quit(1)
     return
 print("STUDY_ROUTE_PASS: return traversal and three screen-bank actions")
 quit(0)
