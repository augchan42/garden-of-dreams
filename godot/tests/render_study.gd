extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func capture(label: String) -> void:
 await create_timer(1.8).timeout
 await RenderingServer.frame_post_draw
 var result = root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")
 if result != OK:
  push_error("Study render save failed")
  quit(1)
func run() -> void:
 var mobile = "--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(22,.04,-13.5)
 route._arrive("qiushuang_zhai",true)
 var prefix="mobile-study" if mobile else "study"
 await capture(prefix)
 for command in ["left","centre","right"]:
  route.execute_command(command)
  await capture(prefix+"-"+command)
 print("STUDY_VIEWS_SAVED ",prefix)
 quit(0)
