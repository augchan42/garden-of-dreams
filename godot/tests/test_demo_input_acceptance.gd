extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func fail(message: String) -> void:
 push_error(message)
 quit(1)

func button_with_text(container: Node, label: String) -> Button:
 for node in container.get_children():
  if node is Button and node.text == label:return node
 return null

func click(button: Button) -> void:
 # Deferred container fitting can span multiple draws on a cold pack launch.
 # Require drawn bounds to settle before sending real pointer events.
 # Force the draw: a background macOS window can skip automatic draws while
 # physics continues, leaving a frame_post_draw wait suspended indefinitely.
 var previous=Rect2()
 var stable_frames=0
 for i in range(30):
  await process_frame
  RenderingServer.force_draw()
  var bounds=button.get_global_rect()
  stable_frames=stable_frames+1 if bounds==previous else 0
  previous=bounds
  if stable_frames>=2:break
 if stable_frames<2:
  fail("Pointer target did not settle within 30 drawn frames")
  return
 var position = previous.get_center()
 var motion = InputEventMouseMotion.new()
 motion.position = position
 # Native startup mouse events can replace the injected hover between frames.
 # Send the same pointer position with each edge of the test click.
 for down in [true, false]:
  root.push_input(motion, true)
  var event = InputEventMouseButton.new()
  event.button_index = MOUSE_BUTTON_LEFT
  event.position = position
  event.pressed = down
  root.push_input(event, true)
  await process_frame

func enter(button: Button) -> void:
 button.grab_focus()
 await process_frame
 for down in [true, false]:
  var event = InputEventKey.new()
  event.keycode = KEY_ENTER
  event.pressed = down
  root.push_input(event, true)
  await process_frame

func await_room(route: Node, id: String) -> bool:
 for i in range(3600):
  await physics_frame
  if route.room_id == id and not route.travelling:return true
 return false

func run() -> void:
 root.size = Vector2i(1410, 600)
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 await process_frame
 await click(button_with_text(route.actions, "Read the terminal"))
 if not route.output_label.text.contains("Follow the lanterns"):fail("Pointer did not activate terminal");return
 await enter(button_with_text(route.actions, "Enter the garden"))
 if not await await_room(route, "rockery_gate"):fail("Keyboard did not leave cell");return
 await click(button_with_text(route.actions, "Follow the lanterns"))
 if not await await_room(route, "qinfang_ting"):fail("Pointer did not follow lanterns");return
 await enter(button_with_text(route.actions, "Cast at the table"))
 if not route.has_node("ReadingResult"):fail("Keyboard did not cast");return
 await click(route.get_node("ReadingResult").find_child("CloseReading", true, false))
 await process_frame
 await enter(button_with_text(route.actions, "Finish the demo"))
 if not route.has_node("DemoFinale"):fail("Keyboard did not open finale");return
 await click(route.get_node("DemoFinale").find_child("ReplayDemo", true, false))
 await process_frame
 if route.room_id != "terminal_room" or route.demo_has_reading:fail("Pointer did not replay");return
 print("DEMO_INPUT_ACCEPTANCE_PASS: pointer and keyboard through full route and replay")
 for player in route.demo_audio.players.values():player.stop()
 await create_timer(.2).timeout
 route.queue_free()
 await create_timer(.2).timeout
 quit(0)
