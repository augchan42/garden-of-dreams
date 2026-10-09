extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route.player.position=Vector3(0,.04,1.8);route._arrive("qinfang_ting",true)
 route.execute_command("table")
 await create_timer(1.6).timeout;await RenderingServer.frame_post_draw
 if route.camera.position.distance_to(Vector3(0,2.45,1.15))>.01:
  push_error("Table action did not reach inspection camera");quit(1);return
 var label="mobile-" if mobile else ""
 root.get_texture().get_image().save_png("res://../docs/reference/"+label+"table-action.png")
 route.execute_command("look")
 await create_timer(1.6).timeout
 if route.camera.position.distance_to(Vector3(0,2.45,1.15))<1:
  push_error("Look did not restore the pavilion view");quit(1);return
 print("TABLE_ACTION_PASS ",label,"inspection, visible UI capture and return to pavilion view")
 quit(0)
