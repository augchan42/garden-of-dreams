extends SceneTree
func _initialize() -> void:
 create_timer(20).timeout.connect(func():quit(1))
 call_deferred("run")
func run() -> void:
 var portrait="--portrait" in OS.get_cmdline_user_args()
 root.content_scale_size=Vector2i.ZERO;root.size=Vector2i(390,844) if portrait else Vector2i(1410,600)
 var route=load("res://runtime/first_reading_demo.tscn").instantiate();root.add_child(route)
 for child in route.get_children():
  if child is CanvasLayer:child.hide()
 route.camera.position=Vector3(-1.8,1.7,38.05);route.camera.look_at(Vector3(-.67,1.5,35.9))
 route.camera.fov=65 if portrait else 48
 await create_timer(1.5).timeout;await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png("res://../docs/reference/terminal-scrolls"+("-portrait" if portrait else "")+".png")==OK)
 print("TERMINAL_SCROLL_RENDER_PASS");quit(0)
