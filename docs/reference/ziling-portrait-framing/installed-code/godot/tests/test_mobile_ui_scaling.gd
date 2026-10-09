extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 create_timer(30).timeout.connect(func():push_error("Mobile UI test timed out");quit(1))
 root.size = Vector2i(1080,2340)
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 # Exercise the same window setup used on a real 420-DPI Android phone.
 if not route.has_method("_configure_ui_scale"):
  push_error("Mobile UI still uses physical pixels without density scaling")
  quit(1)
  return
 route._configure_ui_scale(true,420)
 for frame in range(12):await process_frame
 var logical = root.get_visible_rect().size
 assert(absf(logical.x - 1080.0/2.625)<1.0 and absf(logical.y-2340.0/2.625)<1.0)
 assert(root.content_scale_mode == Window.CONTENT_SCALE_MODE_CANVAS_ITEMS, "Keep native 3D resolution")
 assert(route.actions.get_child(0).size.y >= 48, "Touch actions must be at least 48 logical units")
 assert(route.input.size.y >= 48)
 route._arrive("qinfang_ting",true)
 for frame in range(12):await process_frame
 assert(route.command_panel.size.y < logical.y*.5, "Commands obscure over half the portrait scene")
 route.execute_command("cast")
 for frame in range(12):await process_frame
 var reading = route.get_node("ReadingResult")
 assert(reading.find_child("CloseReading",true,false).size.y >= 48)
 assert(reading.find_child("RecastReading",true,false).size.y >= 48)
 reading.queue_free()
 route._configure_ui_scale(false,420)
 root.size=Vector2i(1410,600)
 for frame in range(12):await process_frame
 assert(root.content_scale_factor == 1 and root.get_visible_rect().size == Vector2(1410,600), "Desktop density should stay unchanged")
 for player in route.demo_audio.players.values():player.stop()
 route.queue_free()
 for frame in range(3):await process_frame
 # Audio cleanup runs asynchronously; fast headless frames can end too early.
 await create_timer(.2).timeout
 print("MOBILE_UI_SCALE_PASS: density units, 48-unit touch actions, native 3D, reading controls, desktop reset")
 quit(0)
