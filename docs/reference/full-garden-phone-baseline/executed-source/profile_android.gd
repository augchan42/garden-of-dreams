extends "res://tests/demo_profile_base.gd"

const TOUR = preload("res://tests/test_full_garden_traversal.gd").TOUR
var arrivals: Array[String] = []
var visited = {"terminal_room": true}
var phase = ""
var intervals: Array[float] = []
var previous_usec = 0
var draws_max = 0
var primitives_max = 0
var practicals_max = 0
var memory_max = 0
var timed_usec = 0
var floor_leg: Dictionary = {}
var air_frames = 0
var failure = ""
var trace: HashingContext
var previous_position: Vector3

func reject(reason: String) -> void:
 phase = ""
 failure = reason
 report.status = "failed"
 report.error = reason
 save_report()
 push_error("FULL_PHONE_PROFILE_REJECTED " + reason)

func _process(_delta: float) -> void:
 if phase.is_empty() or not is_instance_valid(route):return
 var now = Time.get_ticks_usec()
 intervals.append(float(now - previous_usec) / 1000.0)
 timed_usec += now - previous_usec
 previous_usec = now
 var rid = root.get_viewport_rid()
 draws_max = maxi(draws_max, RenderingServer.viewport_get_render_info(rid, RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE, RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME))
 primitives_max = maxi(primitives_max, RenderingServer.viewport_get_render_info(rid, RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE, RenderingServer.VIEWPORT_RENDER_INFO_PRIMITIVES_IN_FRAME))
 practicals_max = maxi(practicals_max, route.get_node("PracticalLights").lights.filter(func(light):return light.visible).size())
 memory_max = maxi(memory_max, RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED))
 if Engine.time_scale != 1.0 or Engine.physics_ticks_per_second != 60:
  reject("Simulation timing changed during the actual phone tour")

func _physics_process(_delta: float) -> void:
 if not failure.is_empty() or floor_leg.is_empty() or not is_instance_valid(route):return
 var position: Vector3 = route.player.position
 floor_leg.physics_frames += 1
 floor_leg.walking_distance_m += previous_position.distance_to(position)
 previous_position = position
 trace.update(var_to_bytes(position))
 floor_leg.min_y = minf(floor_leg.min_y, position.y)
 floor_leg.max_y = maxf(floor_leg.max_y, position.y)
 air_frames = 0 if route.player.is_on_floor() else air_frames + 1
 floor_leg.longest_air_frames = maxi(floor_leg.longest_air_frames, air_frames)
 if position.y < -.95 or air_frames > 24:
  reject("Lost floor support toward " + floor_leg.to + " at " + str(position))
 if route.player.is_on_floor():
  floor_leg.grounded_ray_samples += 1
  var query = PhysicsRayQueryParameters3D.create(position + Vector3(0,.15,0), position - Vector3(0,.45,0))
  query.exclude = [route.player.get_rid()]
  var hit = route.get_world_3d().direct_space_state.intersect_ray(query)
  if not hit.is_empty():floor_leg.supported_ray_samples += 1

func begin_sample(label: String) -> void:
 intervals.clear()
 draws_max = 0
 primitives_max = 0
 practicals_max = 0
 memory_max = 0
 previous_usec = Time.get_ticks_usec()
 phase = label

func end_sample() -> void:
 var label = phase
 phase = ""
 intervals.sort()
 if intervals.is_empty():
  reject("No rendered frames measured for " + label)
  return
 report.samples[label] = {"frames": intervals.size(), "frame_interval_median_ms": intervals[intervals.size()/2], "frame_interval_p95_ms": intervals[int(intervals.size()*.95)], "visible_draw_calls_max": draws_max, "visible_primitives_max": primitives_max, "active_practicals_max": practicals_max, "texture_memory_bytes": memory_max}
 report.timed_seconds = float(timed_usec)/1000000.0
 report.budget_results[label] = {"texture": memory_max<=64*1024*1024, "draw_calls": draws_max<=150, "primitives": primitives_max<=300000, "practicals": practicals_max<=4, "p95_60fps": intervals[int(intervals.size()*.95)]<=1000.0/60.0}
 save_report()

func stationary(label: String) -> void:
 if route.camera_tween and route.camera_tween.is_running():await route.camera_tween.finished
 await get_tree().create_timer(2.0).timeout
 if route.travelling or route.demo_mode or not route.site_bakes_enabled:
  reject("Arrival failed to settle with full lighting at " + label)
  return
 begin_sample(label)
 var deadline = Time.get_ticks_msec() + 3000
 while Time.get_ticks_msec() < deadline and failure.is_empty():await get_tree().process_frame
 if not failure.is_empty():return
 end_sample()
 if not failure.is_empty():return
 # Readback only after the timed phase has stopped; no clocks/lights are changed.
 await RenderingServer.frame_post_draw
 var image = root.get_texture().get_image()
 var filename = "garden-full-" + label + ".png"
 if image.is_empty() or image.save_png("user://"+filename)!=OK:
  reject("Could not capture actual phone arrival " + label)
  return
 report.captures[label] = {"file":filename, "image_size":[image.get_width(),image.get_height()], "sha256":FileAccess.get_sha256("user://"+filename), "room":route.room_id, "camera_settled":not (route.camera_tween and route.camera_tween.is_running()), "viewport_texture_size":[root.get_texture().get_width(),root.get_texture().get_height()], "window_size":[root.size.x,root.size.y], "logical_viewport_size":[root.get_visible_rect().size.x,root.get_visible_rect().size.y]}
 save_report()

func run() -> void:
 report = {"status":"starting", "error":"", "scope":"Actual Android normal fourteen-room public-command traversal and at least 600 timed seconds across whole tours, at normal physics/time. Image readback excluded from timed phases. Dedicated debug app; not 2020 Adreno, release, final art or live services acceptance.", "samples":{}, "legs":[], "captures":{}, "budget_results":{}, "touch_events":[], "timed_seconds":0.0, "completed_tours":0, "minimum_timed_seconds":600}
 if not OS.has_feature("android") or not OS.has_feature("garden_profile"):
  reject("Requires an actual Android dedicated profiling export")
  return
 if Engine.time_scale!=1.0 or Engine.physics_ticks_per_second!=60:
  reject("Requires normal time and 60Hz physics")
  return
 Engine.max_fps=60
 DisplayServer.screen_set_orientation(DisplayServer.SCREEN_PORTRAIT)
 report.build=JSON.parse_string(FileAccess.get_file_as_string("res://phone-profile-build.json"))
 var source=JSON.parse_string(FileAccess.get_file_as_string("res://assets/garden-source.json"))
 report.source_glb_sha256=source.source_glb_sha256
 if report.source_glb_sha256!=report.build.source_glb_sha256:
  reject("Installed scene differs from the pinned build")
  return
 report.device_model=OS.get_model_name()
 report.renderer_device=RenderingServer.get_video_adapter_name()
 report.renderer=RenderingServer.get_current_rendering_method()
 report.physics_ticks_per_second=Engine.physics_ticks_per_second
 report.time_scale=Engine.time_scale
 report.fps_cap=Engine.max_fps
 report.targets={"frames_per_second":60,"texture_memory_bytes":64*1024*1024,"draw_calls":150,"primitives":300000,"practicals":4}
 var catalogs={}
 for name in ["full-index.json","backdrop-wash-index.json","terminal-spill-index.json"]:
  var catalog=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/"+name))
  if not catalog is Dictionary or not preload("res://runtime/baked_materials.gd").source_matches(catalog):
   reject("Source-matched full lighting required: "+name)
   return
  catalogs[name]={"receivers":catalog.size(),"sha256":FileAccess.get_sha256("res://lightmaps/"+name)}
 if catalogs["full-index.json"].receivers!=124 or catalogs["backdrop-wash-index.json"].receivers!=6 or catalogs["terminal-spill-index.json"].receivers!=7:
  reject("Incomplete 124/6/7 receiver catalogs")
  return
 report.catalogs=catalogs
 route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.transition_finished.connect(func(id):arrivals.append(id))
 for frame in range(90):await get_tree().process_frame
 report.native_window_size=[root.size.x,root.size.y]
 report.ui_content_scale_factor=root.content_scale_factor
 if route.room_id!="terminal_room" or route.travelling:
  reject("Actual starting cell state is wrong")
  return
 report.status="running"
 save_report()
 var started=Time.get_ticks_msec()
 await stationary("start-terminal_room")
 var tour=0
 while failure.is_empty() and (tour==0 or timed_usec<600000000):
  for index in range(TOUR.size()):
   if not failure.is_empty():return
   var leg=TOUR[index]
   var origin: String=route.room_id
   var target: String=leg[1]
   var signals_before=arrivals.size()
   route.execute_command("unsupported-traversal-command")
   if route.travelling or route.room_id!=origin:
    reject("Unsupported command changed room state")
    return
   route.execute_command(leg[0])
   if not route.travelling or route.destination!=target:
    reject("Command did not start "+origin+" -> "+target)
    return
   route.execute_command("back")
   if route.destination!=target:
    reject("Command during travel replaced the destination")
    return
   floor_leg={"tour":tour,"from":origin,"to":target,"command":leg[0],"physics_frames":0,"walking_distance_m":0.0,"min_y":route.player.position.y,"max_y":route.player.position.y,"longest_air_frames":0,"grounded_ray_samples":0,"supported_ray_samples":0}
   air_frames=0
   trace=HashingContext.new()
   trace.start(HashingContext.HASH_SHA256)
   previous_position=route.player.position
   var label="%02d-%02d-%s-to-%s"%[tour,index,origin,target]
   begin_sample(label)
   var deadline=Time.get_ticks_msec()+90000
   while route.travelling and Time.get_ticks_msec()<deadline and failure.is_empty():await get_tree().process_frame
   var completed_leg=floor_leg.duplicate()
   floor_leg={}
   completed_leg.trace_sha256=trace.finish().hex_encode()
   completed_leg.end_position=[route.player.position.x,route.player.position.y,route.player.position.z]
   if not failure.is_empty():return
   end_sample()
   if not failure.is_empty():return
   report.legs.append(completed_leg)
   if route.travelling or route.room_id!=target or arrivals.size()!=signals_before+1 or arrivals.back()!=target:
    reject("Wrong room, timeout or arrival signal at "+target)
    return
   var expected_height=4.0 if target=="tubi_tang" else -.65 if target=="aojing_guan" else 0.0
   if absf(route.player.position.y-expected_height)>.2 or completed_leg.grounded_ray_samples==0 or completed_leg.supported_ray_samples!=completed_leg.grounded_ray_samples:
    reject("Arrival height or grounded centre-ray support failed at "+target)
    return
   visited[target]=true
   for frame in range(3):await get_tree().process_frame
   if not route.input.editable or route.actions.get_child_count()!=route.ROOMS[target].actions.size():
    reject("Arrival did not restore context controls at "+target)
    return
   for button in route.actions.get_children():
    if button.disabled:
     reject("Arrival left an action disabled")
     return
   report.visited_rooms=visited.keys()
   report.arrival_signals=arrivals
   await stationary("%02d-%02d-%s"%[tour,index,target])
   print("FULL_PHONE_LEG_RECORDED ",label," timed_seconds=",float(timed_usec)/1000000.0)
  tour+=1
  report.completed_tours=tour
 if not failure.is_empty():return
 if visited.size()!=14 or report.legs.size()!=tour*26 or route.room_id!="terminal_room":
  reject("Incomplete tour coverage or final cell return")
  return
 report.wall_seconds=float(Time.get_ticks_msec()-started)/1000.0
 report.status="complete"
 save_report()
 print("FULL_PHONE_PROFILE_COMPLETE tours=",tour," rooms=",visited.size()," timed_seconds=",report.timed_seconds)
