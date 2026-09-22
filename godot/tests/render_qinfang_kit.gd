extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 if "--mobile" in OS.get_cmdline_user_args():root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(0,.04,1.8)
 route._arrive("qinfang_ting",true)
 await create_timer(2).timeout
 await RenderingServer.frame_post_draw
 var label="mobile-pavilion" if "--mobile" in OS.get_cmdline_user_args() else "pavilion"
 root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")
 print("QINFANG_RENDER_SAVED ",label)
 quit(0)
