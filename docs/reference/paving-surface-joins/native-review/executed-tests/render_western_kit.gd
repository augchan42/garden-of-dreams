extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 for pair in [["ouxiang_xie","ouxiang",Vector3(-23,.04,0)],["ziling_zhou","ziling",Vector3(-35.4,.04,0)]]:
  route.player.position=pair[2];route._arrive(pair[0],true)
  await create_timer(2).timeout;await RenderingServer.frame_post_draw
  var label=("mobile-" if mobile else "")+pair[1]
  root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")
  print("WESTERN_RENDER_SAVED ",label)
 quit(0)
