extends SceneTree
func _initialize() -> void:call_deferred("run")
func fail(message:String) -> void:push_error(message);quit(1)
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await process_frame
 route._arrive("qinfang_ting",true)
 route.cast_rng.seed=2817
 route.execute_command("cast")
 if not route.has_node("ReadingResult"):fail("Cast did not open a result");return
 var card=route.get_node("ReadingResult")
 var first=card.result
 if first.is_empty() or route.hexagram_table.current_lines!=first.primary_lines:fail("Bronze lines do not match primary hexagram");return
 if not card.card.text.contains(str(first.primary.meaning)) or not card.card.text.to_lower().contains("local"):
  fail("Result card lacks name or local label");return
 if route.input.editable:fail("Input remains active under modal");return
 var moving=route.cast_model.from_coin_values([6,7,8,9,6,9])
 card.show_result(moving)
 if not card.card.text.contains("Moving lines: 1, 4, 5, 6") or not card.card.text.contains(str(moving.transformed.meaning)):
  fail("Moving lines or transformed hexagram are absent");return
 card.get_node("ReadingPanel").find_child("RecastReading",true,false).pressed.emit()
 if not route.has_node("ReadingResult") or route.hexagram_table.current_lines!=card.result.primary_lines:
  fail("Recast did not update the same card and table");return
 var recast_lines=card.result.primary_lines.duplicate()
 card.find_child("CloseReading",true,false).pressed.emit()
 await process_frame
 if route.has_node("ReadingResult") or not route.input.editable:fail("Closing did not restore the route controls");return
 if route.hexagram_table.current_lines!=recast_lines:fail("Closing erased the table pattern");return
 route.execute_command("look")
 if route.room_id!="qinfang_ting":fail("Look left the pavilion");return
 print("DEMO_READING_PASS: cast, matching bronze lines, recast, close, retained pattern")
 quit(0)
