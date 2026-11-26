extends SceneTree
func _initialize() -> void:
 create_timer(20).timeout.connect(func():quit(1))
 call_deferred("run")
func run() -> void:
 var portrait="--portrait" in OS.get_cmdline_user_args()
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(390,844) if portrait else Vector2i(1410,600)
 var route=load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 for child in route.get_children():
  if child is CanvasLayer:child.hide()
 route.camera.position=Vector3(-2.1,1.25,38.03)
 route.camera.look_at(Vector3(-1.3,.48,37.4))
 if portrait:route.camera.fov=85
 await create_timer(1.5).timeout
 await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png("res://../docs/reference/terminal-chair-placed"+("-portrait" if portrait else "")+".png")==OK)
 print("TERMINAL_CHAIR_RENDER_PASS")
 quit(0)
