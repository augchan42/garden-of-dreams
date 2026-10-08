extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 if not route.ROOMS.has("tubi_tang"):
  push_error("Hilltop room is missing")
  quit(1)
  return
 route.player.position=Vector3(22,.04,-13.5)
 route._arrive("qiushuang_zhai",true)
 for leg in [["hill","tubi_tang",4.0],["back","qiushuang_zhai",0.0]]:
  route.execute_command(leg[0])
  if not route.travelling:
   push_error("Hilltop command did not begin travel")
   quit(1)
   return
  for i in range(3600):
   await physics_frame
   if route.player.position.y < -.3:
    push_error("Hill approach lost floor support")
    quit(1)
    return
   if not route.travelling:break
  if route.room_id!=leg[1] or absf(route.player.position.y-leg[2])>.2:
   push_error("Hill route failed destination or height: "+str(route.player.position))
   quit(1)
   return
  if leg[1]=="tubi_tang":
   route.execute_command("overlook")
   if not "painted" in route.output_label.text:
    push_error("Missing overlook action")
    quit(1)
    return
 print("HILLTOP_ROUTE_PASS: climb to four metres, overlook action, descent to study")
 quit(0)
