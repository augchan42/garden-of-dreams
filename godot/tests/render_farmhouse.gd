extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func capture(label:String) -> void:
 await create_timer(1.8).timeout
 await RenderingServer.frame_post_draw
 if root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")!=OK:
  push_error("Farmhouse reference could not be saved")
  quit(1)
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(-32,.04,-19.3)
 route._arrive("daoxiang_cun",true)
 var prefix="mobile-farmhouse" if mobile else "farmhouse"
 await capture(prefix)
 route.execute_command("doors")
 await capture(prefix+"-doors")
 route.execute_command("tools")
 await capture(prefix+"-tools")
 route.execute_command("paddy")
 await capture(prefix+"-paddy")
 print("FARMHOUSE_VIEWS_SAVED ",prefix)
 quit(0)
