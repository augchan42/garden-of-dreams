extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route._arrive("rockery_gate",true)
 await create_timer(1.5).timeout;await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png("res://../docs/reference/"+("mobile-" if mobile else "")+"gate-inscription-arrival.png")
 route._camera_to(Vector3(0,2.6,34.1),Vector3(0,3,32.4),true)
 await create_timer(.5).timeout;await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png("res://../docs/reference/"+("mobile-" if mobile else "")+"gate-inscription-close.png")
 print("GATE_INSCRIPTION_RENDER_PASS")
 quit(0)
