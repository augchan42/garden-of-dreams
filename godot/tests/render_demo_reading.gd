extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route._arrive("qinfang_ting",true)
 route.cast_rng.seed=2817
 route.execute_command("cast")
 await create_timer(1.4).timeout;await RenderingServer.frame_post_draw
 var prefix="mobile-" if mobile else ""
 root.get_texture().get_image().save_png("res://../docs/reference/"+prefix+"demo-reading-card.png")
 var moving=route.cast_model.from_coin_values([6,7,8,9,6,9])
 route.hexagram_table.set_lines(moving.primary_lines)
 route.get_node("ReadingResult").show_result(moving)
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png("res://../docs/reference/"+prefix+"demo-reading-moving.png")
 route.get_node("ReadingResult").queue_free()
 await process_frame
 await create_timer(.6).timeout;await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png("res://../docs/reference/"+prefix+"demo-reading-table.png")
 print("DEMO_READING_RENDER_PASS ",prefix)
 quit(0)
