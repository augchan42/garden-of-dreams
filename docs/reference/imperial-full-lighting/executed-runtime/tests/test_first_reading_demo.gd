extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func fail(message: String) -> void:
 push_error(message)
 quit(1)

func press_action(route: Node, label: String) -> bool:
 for button in route.actions.get_children():
  if button.text == label:
   button.pressed.emit()
   return true
 return false

func await_room(route: Node, id: String) -> bool:
 for i in range(3600):
  await physics_frame
  if route.room_id == id and not route.travelling:return true
 return false

func run() -> void:
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 await process_frame
 if not route.demo_mode or route.room_id != "terminal_room":fail("Demo must start at the cell");return
 if route.actions.get_child_count() != 2:fail("Cell action list is too long");return
 if not press_action(route, "Read the terminal") or not route.output_label.text.contains("Follow the lanterns"):fail("Terminal invitation is missing");return
 if not press_action(route, "Enter the garden") or not await await_room(route, "rockery_gate"):fail("Button route did not reach gate");return
 if route.demo_audio.last_cue != "lanterns" or route.demo_audio.players.lanterns.stream == null:fail("Gate ambience cue is missing");return
 if not press_action(route, "Follow the lanterns") or not await await_room(route, "qinfang_ting"):fail("Button route did not reach pavilion");return
 if route.demo_audio.last_cue != "water" or route.demo_audio.players.water.stream == null:fail("Pavilion water cue is missing");return
 if route.actions.get_child_count() != 3:fail("Pavilion demo action list is too long");return
 if not press_action(route, "Examine the table") or not route.output_label.text.contains("Six bronze lines"):fail("Table action failed");return
 route.cast_rng.seed = 2817
 if not press_action(route, "Cast at the table") or not route.has_node("ReadingResult"):fail("Cast did not open reading");return
 if route.demo_audio.last_cue != "cast" or route.demo_audio.players.cast.stream == null:fail("Cast cue is missing");return
 var first = route.get_node("ReadingResult").result
 route.get_node("ReadingResult").find_child("CloseReading", true, false).pressed.emit()
 await process_frame
 if not press_action(route, "Finish the demo") or not route.has_node("DemoFinale"):fail("Final beat is missing");return
 var summary = route.get_node("DemoFinale").find_child("ReadingSummary", true, false)
 if not summary.text.contains(str(first.primary.meaning)):fail("Final beat lost the reading");return
 route.get_node("DemoFinale").find_child("ReplayDemo", true, false).pressed.emit()
 await process_frame
 if route.room_id != "terminal_room" or route.demo_has_reading or route.has_node("DemoFinale"):
  fail("Replay did not reset the demo");return
 if route.actions.get_child_count() != 2:fail("Replay cell actions are missing");return
 print("FIRST_READING_DEMO_PASS: button-only cell, gate, pavilion, cast, finale, replay")
 for player in route.demo_audio.players.values():player.stop()
 await create_timer(.2).timeout
 route.queue_free()
 await create_timer(.2).timeout
 quit(0)
