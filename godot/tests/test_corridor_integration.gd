extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await process_frame
 var bodies=route.find_children("COL_QINFANG_corridor_*","StaticBody3D",true,false)
 if bodies.size()!=80:
  push_error("Expected sixteen corridor bays with five collision meshes each: "+str(bodies.size()));quit(1);return
 for path in [route.STUDY_PATH,route.WEST_PATH,route.NORTH_PATH,route.GATE_PATH.slice(11)]:
  route.player.position=path[0]+Vector3(0,.04,0)
  route._arrive("qinfang_ting",true)
  for reverse in [false,true]:
   var points=path.duplicate()
   if reverse:points.reverse()
   route._travel(points,"qinfang_ting")
   for i in range(2100):
    await physics_frame
    if not route.travelling:break
   if route.travelling or route.player.position.distance_to(points[-1])>.25 or route.player.position.y<-.1:
    push_error("Corridor route obstructed: "+str(points)+" at "+str(route.player.position));quit(1);return
 print("CORRIDOR_INTEGRATION_PASS: sixteen bays, four full approaches and their end junctions, both directions")
 quit(0)
