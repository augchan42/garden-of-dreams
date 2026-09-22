extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route._arrive("rockery_gate",true)
 var views=[
  ["drips",Vector3(-1.8,1.45,22.6),Vector3(-.65,1.15,22)],
  ["banana",Vector3(0,1.7,19.1),Vector3(.55,1.6,17.35)],
  ["exit",Vector3(0,1.65,18.5),Vector3(0,1.8,0)]]
 for view in views:
  route.player.position=Vector3(view[1].x,.04,view[1].z)
  route._camera_to(view[1],view[2],true)
  await create_timer(1.5).timeout;await RenderingServer.frame_post_draw
  var label=("mobile-" if mobile else "")+"gate-dressing-"+view[0]
  root.get_texture().get_image().save_png("res://../docs/reference/"+label+".png")
  print("GATE_DRESSING_RENDER_SAVED ",label)
 quit(0)
