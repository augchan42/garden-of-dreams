extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await process_frame
 var bodies=route.find_children("COL_QINFANG_kit_*","StaticBody3D",true,false)
 if bodies.size()!=15:
  push_error("Expected roof, six posts, six brackets and two benches: "+str(bodies.size()));quit(1);return
 var paths=[route.WEST_PATH.slice(0,4),route.STUDY_PATH.slice(0,4),route.NORTH_PATH.slice(0,5),route.BAMBOO_PATH.slice(0,5)]
 for path in paths:
  route.player.position=path[0]+Vector3(0,.04,0)
  route._arrive("qinfang_ting",true)
  for reverse in [false,true]:
   var points=path.duplicate()
   if reverse:points.reverse()
   route._travel(points,"qinfang_ting")
   for i in range(900):
    await physics_frame
    if not route.travelling:break
   if route.travelling or route.player.position.distance_to(points[-1])>.25 or route.player.position.y<-.1:
    push_error("Pavilion exit obstructed: "+str(points)+" at "+str(route.player.position));quit(1);return
 print("QINFANG_INTEGRATION_PASS: 15 placed collisions, four approaches in both directions")
 quit(0)
