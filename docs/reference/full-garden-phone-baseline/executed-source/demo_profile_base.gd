extends Node

# Run only in a dedicated Android profiling export, never as a game autoload.
var report: Dictionary = {}
var route: Node3D
var finished = false
var root: Window:
 get: return get_tree().root

class TouchRecorder extends Node:
 var profile_host
 func _input(event: InputEvent) -> void:
  if profile_host.finished and event is InputEventScreenTouch:
   profile_host.report.touch_events.append({"pressed": event.pressed, "position": [event.position.x, event.position.y]})
   profile_host.call_deferred("save_after_touch")

func _ready() -> void:
 print("PHONE_PROFILE_STARTED")
 call_deferred("run")

func save_report() -> void:
 var error = preload("res://tests/profile_report_store.gd").publish("user://garden-phone-profile.json", report)
 assert(error == OK, "Phone report publication failed: " + error_string(error))

func buttons() -> Dictionary:
 var result = {}
 var candidates = route.actions.get_children()
 for name in ["ReadingResult", "DemoFinale"]:
  if route.has_node(name):
   candidates.append_array(route.get_node(name).find_children("*", "Button", true, false))
 for button in candidates:
  var rectangle = button.get_global_rect()
  var center = root.get_screen_transform() * rectangle.get_center()
  var physical_size = root.get_screen_transform().basis_xform(rectangle.size)
  result[button.text] = {"screen_center": [center.x, center.y], "logical_size": [rectangle.size.x, rectangle.size.y], "screen_size": [physical_size.x, physical_size.y]}
 return result

func save_after_touch() -> void:
 await RenderingServer.frame_post_draw
 report.reading_open = route.has_node("ReadingResult")
 report.room_after_touch = route.room_id
 report.buttons = buttons()
 report.texture_memory_after_touch_bytes = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
 var result = root.get_texture().get_image().save_png("user://garden-phone-after-touch.png")
 assert(result == OK)
 save_report()

func capture_arrival(label: String) -> void:
 # Freeze shader clocks only for image comparison, after real frame sampling.
 var clocks: Dictionary = {}
 for node in route.find_children("*", "MeshInstance3D", true, false):
  for surface in range(node.mesh.get_surface_count()):
   var material = node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name == "timeline_time" and not clocks.has(material):
      clocks[material] = material.get_shader_parameter("timeline_time")
      material.set_shader_parameter("timeline_time", 3.0)
 for frame in range(2):
  await get_tree().process_frame
 await RenderingServer.frame_post_draw
 var image = root.get_texture().get_image()
 assert(image.save_png("user://garden-phone-" + label + ".png") == OK)
 var camera = route.camera.global_transform
 report.captures[label] = {"clock": 3.0, "animated_materials": clocks.size(), "image_size": [image.get_width(), image.get_height()], "camera_transform": [camera.basis.x, camera.basis.y, camera.basis.z, camera.origin]}
 for material in clocks:
  material.set_shader_parameter("timeline_time", clocks[material])
 # Settle resumed shaders before the next timed movement.
 for frame in range(60):
  await get_tree().process_frame
 save_report()

func sample(label: String, frames: int, moving = false) -> void:
 var intervals: Array[float] = []
 var draws: Array[int] = []
 var triangles: Array[int] = []
 var previous = Time.get_ticks_usec()
 var minimum_y = route.player.position.y
 var practicals_max = 0
 for frame in range(frames):
  await get_tree().process_frame
  var now = Time.get_ticks_usec()
  intervals.append(float(now - previous) / 1000.0)
  previous = now
  minimum_y = min(minimum_y, route.player.position.y)
  draws.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(), RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE, RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME))
  triangles.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(), RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE, RenderingServer.VIEWPORT_RENDER_INFO_PRIMITIVES_IN_FRAME))
  practicals_max = max(practicals_max, route.get_node("PracticalLights").lights.filter(func(light): return light.visible).size())
  if moving and not route.travelling:
   break
 intervals.sort()
 draws.sort()
 triangles.sort()
 assert(not intervals.is_empty())
 report.samples[label] = {"frames": intervals.size(), "frame_interval_median_ms": intervals[intervals.size() / 2], "frame_interval_p95_ms": intervals[int(intervals.size() * .95)], "visible_draw_calls_max": draws.back(), "visible_primitives_max": triangles.back(), "active_practicals_max": practicals_max, "minimum_player_y": minimum_y, "texture_memory_bytes": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)}
 save_report()

func run() -> void:
 assert(OS.has_feature("android"), "This profiler requires actual Android hardware")
 assert(OS.has_feature("garden_profile"), "Use a dedicated profiling export")
 Engine.max_fps = 60
 DisplayServer.screen_set_orientation(DisplayServer.SCREEN_PORTRAIT)
 for frame in range(30):
  await get_tree().process_frame
 var source = JSON.parse_string(FileAccess.get_file_as_string("res://assets/garden-source.json"))
 var build = JSON.parse_string(FileAccess.get_file_as_string("res://phone-profile-build.json"))
 report = {"status": "running", "scope": "Actual Android demo arrival views, cell/gate/pavilion travel and tap diagnostics at the declared staged source. Not corrected-source acceptance, all-garden traversal, release timing, older Adreno hardware or final art.", "source_glb_sha256": source.source_glb_sha256, "build": build, "device_model": OS.get_model_name(), "renderer_device": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(), "native_window_size": [root.size.x, root.size.y], "screen_dpi": DisplayServer.screen_get_dpi(), "refresh_rate": DisplayServer.screen_get_refresh_rate(), "fps_cap": Engine.max_fps, "targets": {"frames_per_second": 60, "texture_memory_bytes": 64 * 1024 * 1024, "draw_calls": 150, "primitives": 300000, "practicals": 4}, "samples": {}, "touch_events": []}
 assert(report.source_glb_sha256 == build.source_glb_sha256, "Staged source and installed bake record differ")
 report.captures = {}
 save_report()
 route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 var recorder = TouchRecorder.new()
 recorder.profile_host = self
 root.add_child(recorder)
 get_tree().create_timer(180).timeout.connect(func():
  if not finished:
   report.status = "timed_out"
   save_report()
   push_error("PHONE_PROFILE_TIMEOUT"))
 for frame in range(90):
  await get_tree().process_frame
 report.logical_viewport_size = [root.get_visible_rect().size.x, root.get_visible_rect().size.y]
 report.ui_content_scale_factor = root.content_scale_factor
 report.ui_content_scale_mode = root.content_scale_mode
 report.initial_buttons = buttons()
 await sample("cell", 180)
 await capture_arrival("cell")
 route.execute_command("exit")
 assert(route.travelling, "Cell exit did not start physics travel")
 await sample("cell_to_gate", 3600, true)
 assert(route.room_id == "rockery_gate" and not route.travelling, "Did not reach gate")
 for frame in range(60):
  await get_tree().process_frame
 await sample("gate", 180)
 await capture_arrival("gate")
 route.execute_command("enter")
 assert(route.travelling, "Gate entry did not start physics travel")
 await sample("gate_to_pavilion", 5400, true)
 assert(route.room_id == "qinfang_ting" and not route.travelling, "Did not reach pavilion")
 for frame in range(90):
  await get_tree().process_frame
 await sample("pavilion", 180)
 await capture_arrival("pavilion")
 report.budget_results = {}
 for label in report.samples:
  var data = report.samples[label]
  report.budget_results[label] = {"texture": data.texture_memory_bytes <= report.targets.texture_memory_bytes, "draw_calls": data.visible_draw_calls_max <= report.targets.draw_calls, "primitives": data.visible_primitives_max <= report.targets.primitives, "practicals": data.active_practicals_max <= report.targets.practicals, "no_fall_below_floor": data.minimum_player_y >= -.3}
 report.buttons = buttons()
 report.texture_inventory = preload("res://tests/texture_binding_inventory.gd").new().collect(route)
 report.status = "ready_for_taps"
 finished = true
 save_report()
 print("PHONE_PROFILE_READY_FOR_TAPS source=", report.source_glb_sha256, " user_dir=", OS.get_user_data_dir())
