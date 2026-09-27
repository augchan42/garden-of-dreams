extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func wait_for_room(route: Node, id: String) -> bool:
 for i in range(3600):
  await physics_frame
  if route.room_id == id and not route.travelling:return true
 return false

func run() -> void:
 root.size = Vector2i(1410, 600)
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 await create_timer(1.0).timeout
 route.execute_command("terminal")
 await create_timer(2.0).timeout
 route.execute_command("exit")
 if not await wait_for_room(route, "rockery_gate"):quit(1);return
 await create_timer(1.0).timeout
 route.execute_command("enter")
 if not await wait_for_room(route, "qinfang_ting"):quit(1);return
 await create_timer(1.0).timeout
 route.execute_command("table")
 await create_timer(1.5).timeout
 route.cast_rng.seed = 2817
 route.execute_command("cast")
 await create_timer(3.0).timeout
 route.get_node("ReadingResult").find_child("CloseReading", true, false).pressed.emit()
 await process_frame
 await create_timer(1.5).timeout
 route.execute_command("finish")
 await create_timer(2.0).timeout
 route.get_node("DemoFinale").find_child("ReplayDemo", true, false).pressed.emit()
 await create_timer(1.0).timeout
 print("DEMO_CAPTURE_PASS")
 for player in route.demo_audio.players.values():player.stop()
 await create_timer(.2).timeout
 route.queue_free()
 await create_timer(.2).timeout
 quit(0)
