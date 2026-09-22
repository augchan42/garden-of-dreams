extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route.player.position=Vector3(-18,.04,-14.7);route._arrive("hengwu_yuan",true)
 for view in ["arrival","rocks","read"]:
  if view!="arrival":route.execute_command(view)
  await create_timer(2).timeout;await RenderingServer.frame_post_draw
  var label=("mobile-" if mobile else "")+"hengwu-kit-"+view
  root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")
  print("HENGWU_RENDER_SAVED ",label)
 quit(0)
