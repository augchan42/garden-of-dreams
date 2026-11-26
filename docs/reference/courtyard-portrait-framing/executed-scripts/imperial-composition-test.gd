extends SceneTree

var errors: Array[String] = []
var rows: Array = []
var output := "/tmp/garden-portrait-architecture"
var route
var contract: Dictionary
var touch := false
var density := false
var selected_room := ""

func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="): output = arg.trim_prefix("--output=")
  if arg=="--touch":touch=true
  if arg=="--density":density=true;touch=true
  if arg.begins_with("--room="):selected_room=arg.trim_prefix("--room=")
 create_timer(120).timeout.connect(func():push_error("PORTRAIT_ARCHITECTURE_REJECTED: Native deadline exceeded");quit(1))
 call_deferred("run")

func check(value: bool, message: String) -> void:
 if not value:
  errors.append(message)
  push_error("PORTRAIT_ARCHITECTURE_REJECTED: " + message)

func settle(frames: int = 110) -> void:
 for frame in range(frames): await process_frame
 # Render-frame counts do not establish that a timed camera tween has finished.
 var deadline := Time.get_ticks_msec() + 10000
 while is_instance_valid(route) and route.camera_tween != null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec() < deadline:
  await process_frame
 check(route.camera_tween == null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(), "Camera transition timed out")
 var drawn := [false]
 RenderingServer.frame_post_draw.connect(func():drawn[0]=true,CONNECT_ONE_SHOT)
 RenderingServer.force_draw()
 var draw_deadline:=Time.get_ticks_msec()+10000
 while not drawn[0] and Time.get_ticks_msec()<draw_deadline:await process_frame
 check(drawn[0],"Native draw deadline")

func inspect(room: String, phase: String, fitted: bool = true) -> void:
 var low := Vector2(INF, INF)
 var high := Vector2(-INF, -INF)
 var behind := 0
 for name in contract.rooms[room].meshes:
  var mesh = route.find_child(name, true, false) as MeshInstance3D
  check(mesh != null, "Missing contracted architecture " + name)
  if mesh == null: return
  for surface in range(mesh.mesh.get_surface_count()):
   for local in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
    var world: Vector3 = mesh.global_transform * local
    if route.camera.is_position_behind(world): behind += 1
    var pixel: Vector2 = route.camera.unproject_position(world)
    low = low.min(pixel)
    high = high.max(pixel)
 var visible: Vector2 = root.get_visible_rect().size
 var header: Rect2 = route.status.get_global_rect()
 var panel: Rect2 = route.command_panel.get_global_rect()
 if fitted:
  check(behind == 0 and low.x >= 8 and high.x <= visible.x-8 and low.y >= header.end.y+8 and high.y <= panel.position.y-8, room + " architecture obscured/clipped: " + phase)
  check((high.x-low.x) / visible.x >= contract.rooms[room].minimum_width_fraction, room + " architecture too small: " + phase)
  check(absf((low.x+high.x)*.5 - visible.x*.5) < visible.x*.15, room + " architecture off center: " + phase)
  if contract.rooms[room].has("minimum_height_fraction"):
   check((high.y-low.y)/(panel.position.y-header.end.y)>=contract.rooms[room].minimum_height_fraction,room+" architecture occupies too little scene height: "+phase)
   check((low.y-header.end.y)/(panel.position.y-header.end.y)<=contract.rooms[room].maximum_top_fraction,room+" excessive ceiling above facade: "+phase)
 var path := output + "/" + room + "-" + phase + ".png"
 var image := root.get_texture().get_image()
 check(image.save_png(path) == OK, "Cannot save original " + phase)
 rows.append({"room": room, "phase": phase, "capture": path, "sha256": FileAccess.get_sha256(path), "logical_viewport": [visible.x, visible.y], "capture_pixels": [image.get_width(), image.get_height()], "bounds": [[low.x, low.y], [high.x, high.y]], "behind_camera": behind, "header_bottom": header.end.y, "panel_top": panel.position.y, "camera_position": [route.camera.position.x, route.camera.position.y, route.camera.position.z], "camera_transition_running": route.camera_tween != null and route.camera_tween.is_valid() and route.camera_tween.is_running()})

func run() -> void:
 if DisplayServer.get_name() == "headless":
  push_error("Graphical renderer required")
  quit(1)
  return
 DirAccess.make_dir_recursive_absolute(output)
 contract = JSON.parse_string(FileAccess.get_file_as_string("res://tests/portrait-architecture-contract.json"))
 if FileAccess.get_sha256("res://assets/garden-of-dreams.glb") != contract.source_glb_sha256:
  push_error("Contract is for another source")
  quit(1)
  return
 route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await settle(12)
 check(selected_room=="" or contract.rooms.has(selected_room),"Unknown selected architecture room")
 for room in contract.rooms:
  if selected_room!="" and room!=selected_room:continue
  root.size = Vector2i(1080,2340) if density else Vector2i(390,844)
  route._configure_ui_scale(touch,420 if density else 160)
  await settle(12)
  route._arrive(room, true)
  await settle(12)
  inspect(room, "arrival-390x844")
  var position_before: Vector3 = route.player.position
  route.execute_command("doors")
  await settle()
  var detail: Transform3D = route.camera.transform
  var text: String = route.output_label.text
  inspect(room, "doors-390x844", false)
  root.size = Vector2i(945,2100) if density else Vector2i(360,800)
  await settle(12)
  check(route.camera.transform.is_equal_approx(detail), room + " resize replaced selected detail view")
  check(route.output_label.text == text, room + " resize replaced detail text")
  route.execute_command("look")
  await settle()
  inspect(room, "look-360x800")
  check(route.player.position.is_equal_approx(position_before), room + " camera action moved visitor")
  check(route.room_id == room, room + " camera action changed room")
  text = route.output_label.text
  root.size = Vector2i(2340,1080) if density else Vector2i(1410,600)
  await settle(12)
  var expected: Array = contract.rooms[room].desktop_position
  check(route.camera.position.is_equal_approx(Vector3(expected[0], expected[1], expected[2])), room + " resizing did not restore desktop overview")
  check(route.output_label.text == text, room + " overview resize changed the text")
  inspect(room, "overview-landscape", false)
  root.size = Vector2i(1080,2340) if density else Vector2i(390,844)
  await settle(12)
  inspect(room, "resized-390x844")
  check(route.output_label.text == text, room + " portrait resize changed the text")
  if touch:
   check(route.input.size.y>=48,room+" touch input smaller than48 logical units")
   for button in route.actions.get_children():check(button.size.y>=48,room+" touch action smaller than48 logical units")
   route.action_scroll.scroll_vertical=10000;await settle(12)
   var last=route.actions.get_child(route.actions.get_child_count()-1) as Button
   check(route.action_scroll.get_global_rect().encloses(last.get_global_rect()),room+" final action unreachable by scrolling")
 var file := FileAccess.open(output + "/report.json", FileAccess.WRITE)
 file.store_string(JSON.stringify({"status": "portrait_architecture_behavior_passed" if errors.is_empty() else "rejected", "source_glb_sha256": contract.source_glb_sha256, "route_sha256": FileAccess.get_sha256("res://runtime/entry_route.gd"), "test_sha256": FileAccess.get_sha256("res://tests/test_portrait_architecture.gd"), "errors": errors, "rows": rows, "touch":touch, "density":density, "selected_room":selected_room, "scope": "Measured architecture fit/scale/centering, detail persistence, look restoration and real viewport orientation changes for three rooms. Direct arrival state; travel and final art acceptance are separate."}, " "))
 file.close()
 print("PORTRAIT_ARCHITECTURE_RESULT ", rows.size(), " captures; ", errors.size(), " failures")
 quit(0 if errors.is_empty() else 1)
