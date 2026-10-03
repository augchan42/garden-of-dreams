extends SceneTree
func _initialize() -> void:
 create_timer(20).timeout.connect(func():quit(1))
 call_deferred("run")
func run() -> void:
 root.content_scale_size=Vector2i.ZERO;root.size=Vector2i(1410,600)
 var route=load("res://runtime/first_reading_demo.tscn").instantiate();root.add_child(route)
 for child in route.get_children():
  if child is CanvasLayer:child.hide()
 route.camera.projection=Camera3D.PROJECTION_ORTHOGONAL;route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.size=17
 route.camera.position=Vector3(0,1.4,38.8);route.camera.look_at(Vector3(0,1.4,40.25))
 await create_timer(1.5).timeout;await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png("res://../docs/reference/stage-backstage-wall.png")==OK)
 print("BACKSTAGE_WALL_RENDER_PASS");quit(0)
