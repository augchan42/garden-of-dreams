extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func capture(route: Node, name: String) -> void:
 await create_timer(1.5).timeout
 RenderingServer.force_draw()
 root.get_texture().get_image().save_png("res://../docs/reference/demo-" + name + ".png")

func run() -> void:
 var portrait = "--portrait" in OS.get_cmdline_user_args()
 root.size = Vector2i(390, 844) if portrait else Vector2i(1410, 600)
 var suffix = "portrait" if portrait else "desktop"
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 await capture(route, suffix + "-cell")
 route.player.position = Vector3(0, .03, 32.5)
 route._arrive("rockery_gate", true)
 await capture(route, suffix + "-gate")
 route.player.position = Vector3(0, .03, 1.8)
 route._arrive("qinfang_ting", true)
 await capture(route, suffix + "-pavilion")
 route.cast_rng.seed = 2817
 route.execute_command("cast")
 await capture(route, suffix + "-reading")
 route.get_node("ReadingResult").queue_free()
 await process_frame
 await capture(route, suffix + "-table")
 route.execute_command("finish")
 await capture(route, suffix + "-finale")
 print("DEMO_RENDER_PASS ", suffix)
 quit(0)
