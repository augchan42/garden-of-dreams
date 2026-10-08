extends SceneTree

# One visitor and one scene, starting in the actual cell. No position writes,
# private arrival calls, path replacement or time-scale changes.
const TOUR = [
 ["exit", "rockery_gate"], ["enter", "qinfang_ting"],
 ["board", "qiushuang_zhai"], ["hill", "tubi_tang"],
 ["back", "qiushuang_zhai"], ["back", "qinfang_ting"],
 ["west", "ouxiang_xie"], ["island", "ziling_zhou"],
 ["back", "ouxiang_xie"], ["nunnery", "longcui_an"],
 ["back", "ouxiang_xie"], ["back", "qinfang_ting"],
 ["study", "hengwu_yuan"], ["farm", "daoxiang_cun"],
 ["back", "hengwu_yuan"], ["back", "qinfang_ting"],
 ["north", "daguan_lou"], ["back", "qinfang_ting"],
 ["east", "yihong_yuan"], ["pond", "aojing_guan"],
 ["back", "yihong_yuan"], ["back", "qinfang_ting"],
 ["bamboo", "xiaoxiang_guan"], ["back", "qinfang_ting"],
 ["back", "rockery_gate"], ["back", "terminal_room"]
]
var route
var output = ""
var diagnose_floor = false
var floor_failures: Array[String] = []
var arrivals: Array[String] = []
var visited = {"terminal_room": true}
var report = {"status": "running", "legs": [], "scope": "Continuous command-driven actual physics through fourteen rooms and all thirteen connections both ways, without resetting the visitor. Headless state/floor/collision checks; not rendered UI, performance, live services or final scene art acceptance."}

func _initialize() -> void:
 call_deferred("run")

func finish(error = "") -> void:
 report.status = "passed" if error.is_empty() else "failed"
 report.error = error
 report.visited_rooms = visited.keys()
 report.arrival_signals = arrivals
 report.floor_failures = floor_failures
 if not output.is_empty():
  FileAccess.open(output, FileAccess.WRITE).store_string(JSON.stringify(report, " ") + "\n")
 if is_instance_valid(route):route.queue_free()
 await create_timer(.3).timeout
 if error.is_empty():print("FULL_GARDEN_TRAVERSAL_PASS rooms=", visited.size(), " legs=", report.legs.size())
 else:push_error("FULL_GARDEN_TRAVERSAL_FAILED: " + error)
 quit(0 if error.is_empty() else 1)

func run() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output = arg.trim_prefix("--output=")
  if arg == "--diagnose-floor":diagnose_floor = true
 if output.is_empty():
  await finish("Provide --output for traversal provenance")
  return
 report.source_glb_sha256 = FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 report.route_sha256 = FileAccess.get_sha256("res://runtime/entry_route.gd")
 report.test_sha256 = FileAccess.get_sha256("res://tests/test_full_garden_traversal.gd")
 report.physics_ticks_per_second = Engine.physics_ticks_per_second
 report.time_scale = Engine.time_scale
 route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.transition_finished.connect(func(id):arrivals.append(id))
 for i in range(5):await physics_frame
 if route.room_id != "terminal_room" or route.travelling:
  await finish("Actual initial cell state is wrong")
  return
 report.start_position = [route.player.position.x, route.player.position.y, route.player.position.z]
 for leg in TOUR:
  var origin: String = route.room_id
  var target: String = leg[1]
  var signals_before = arrivals.size()
  route.execute_command("unsupported-traversal-command")
  if route.travelling or route.room_id != origin:
   await finish("Unsupported command changed room state at " + origin)
   return
  route.execute_command(leg[0])
  if not route.travelling or route.destination != target:
   await finish("Command failed to begin " + origin + " -> " + target)
   return
  route.execute_command("back")
  if not route.travelling or route.destination != target:
   await finish("Command during travel replaced the route to " + target)
   return
  var trace = HashingContext.new()
  trace.start(HashingContext.HASH_SHA256)
  var frames = 0
  var air_frames = 0
  var longest_air = 0
  var min_y = route.player.position.y
  var max_y = min_y
  var distance = 0.0
  var previous: Vector3 = route.player.position
  var floor_samples = 0
  var supported_samples = 0
  var centre_ray_misses = []
  while route.travelling and frames < 3600:
   await physics_frame
   frames += 1
   var position: Vector3 = route.player.position
   trace.update(var_to_bytes(position))
   distance += previous.distance_to(position)
   previous = position
   min_y = minf(min_y, position.y)
   max_y = maxf(max_y, position.y)
   air_frames = 0 if route.player.is_on_floor() else air_frames + 1
   longest_air = maxi(longest_air, air_frames)
   if position.y < -.95 or longest_air > 24:
    await finish("Lost floor support toward " + target + " at " + str(position))
    return
   if route.player.is_on_floor():
    floor_samples += 1
    var query = PhysicsRayQueryParameters3D.create(position + Vector3(0,.15,0), position - Vector3(0,.45,0))
    query.exclude = [route.player.get_rid()]
    var hit = route.get_world_3d().direct_space_state.intersect_ray(query)
    if not hit.is_empty():supported_samples += 1
    else:
     var contacts = []
     for i in range(route.player.get_slide_collision_count()):
      var collision = route.player.get_slide_collision(i)
      contacts.append({"position": str(collision.get_position()), "normal": str(collision.get_normal()), "body": str(collision.get_collider().name)})
     centre_ray_misses.append({"position": str(position), "contacts": contacts})
  var end: Vector3 = route.player.position
  report.legs.append({"from": origin, "command": leg[0], "to": target,
   "physics_frames": frames, "walking_distance_m": distance, "min_y": min_y,
   "max_y": max_y, "longest_air_frames": longest_air, "grounded_ray_samples": floor_samples,
   "supported_ray_samples": supported_samples, "centre_ray_misses": centre_ray_misses, "trace_sha256": trace.finish().hex_encode(),
   "end_position": [end.x, end.y, end.z]})
  if route.travelling or route.room_id != target or arrivals.size() != signals_before + 1 or arrivals.back() != target:
   await finish("Wrong room, timeout or arrival signal at " + target)
   return
  var expected_height = 4.0 if target == "tubi_tang" else -.65 if target == "aojing_guan" else 0.0
  if absf(end.y - expected_height) > .2:
   await finish("Arrival height failed at " + target)
   return
  if floor_samples == 0 or supported_samples != floor_samples:
   var failure = "Grounded centre-ray support failed " + origin + " -> " + target
   floor_failures.append(failure)
   if not diagnose_floor:
    await finish(failure)
    return
  visited[target] = true
  for i in range(3):await process_frame
  if not route.input.editable or route.actions.get_child_count() != route.ROOMS[target].actions.size():
   await finish("Arrival did not restore room controls at " + target)
   return
  for button in route.actions.get_children():
   if button.disabled:
    await finish("Arrival left an action disabled at " + target)
    return
  print("CONTINUOUS_LEG_RECORDED ", origin, " -> ", target, " frames=", frames, " grounded_ray_misses=", floor_samples - supported_samples)
 if visited.size() != 14 or report.legs.size() != 26 or route.room_id != "terminal_room":
  await finish("Tour did not cover fourteen rooms and return to the actual cell")
  return
 await finish("Floor support failed in " + str(floor_failures.size()) + " legs; diagnostic tour is not acceptance" if not floor_failures.is_empty() else "")
