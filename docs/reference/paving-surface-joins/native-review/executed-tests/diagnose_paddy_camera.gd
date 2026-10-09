extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(-32,.04,-19.3)
 route._arrive("daoxiang_cun",true)
 route.execute_command("paddy")
 await create_timer(1.6).timeout
 var variants={
  "side": [Vector3(-39,3,-22),Vector3(-34.5,1.7,-26)],
  "near": [Vector3(-38.5,2.8,-24.8),Vector3(-35.5,2,-26)],
  "gap": [Vector3(-38.8,2.6,-23),Vector3(-35.8,1.5,-26)]}
 for label in variants:
  route._camera_to(variants[label][0],variants[label][1],true)
  for i in range(6):await process_frame
  await RenderingServer.frame_post_draw
  assert(root.get_texture().get_image().save_png("res://../docs/reference/paddy-camera-"+label+".png")==OK)
 print("PADDY_CAMERA_COMPARISONS_SAVED")
 quit(0)
