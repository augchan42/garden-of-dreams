extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func capture(label:String) -> void:
 await create_timer(1.8).timeout
 await RenderingServer.frame_post_draw
 if root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")!=OK:
  push_error("Reflection hall reference could not be saved")
  quit(1)
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1)
 route._arrive("aojing_guan",true)
 var prefix="mobile-reflection" if mobile else "reflection"
 await capture(prefix)
 route.execute_command("doors")
 await capture(prefix+"-doors")
 route.execute_command("reflection")
 await capture(prefix+"-water")
 print("REFLECTION_VIEWS_SAVED ",prefix)
 quit(0)
