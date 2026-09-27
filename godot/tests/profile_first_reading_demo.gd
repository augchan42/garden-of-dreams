extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 root.size = Vector2i(1410, 600)
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 Engine.max_fps = 0
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 var report = {"device": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(), "viewport": [1410, 600], "scope": "Stationary demo arrival views on this Mac", "views": {}}
 var positions = {"terminal_room": Vector3(-1.3, .03, 37.4), "rockery_gate": Vector3(0, .03, 32.5), "qinfang_ting": Vector3(0, .03, 1.8)}
 for room in positions:
  route.player.position = positions[room]
  route._arrive(room, true)
  route.get_node("PracticalLights").update_lights()
  for i in range(40):await process_frame
  var times: Array[float] = []
  var draws: Array[int] = []
  var primitives: Array[int] = []
  var previous = Time.get_ticks_usec()
  for i in range(60):
   RenderingServer.force_draw()
   var now = Time.get_ticks_usec()
   times.append(float(now - previous) / 1000.0)
   previous = now
   draws.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(), RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE, RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME))
   primitives.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(), RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE, RenderingServer.VIEWPORT_RENDER_INFO_PRIMITIVES_IN_FRAME))
  times.sort()
  draws.sort()
  primitives.sort()
  report.views[room] = {"forced_draw_interval_median_ms": times[30], "forced_draw_interval_p95_ms": times[56], "visible_draw_calls_max": draws.back(), "visible_primitives_max": primitives.back(), "active_practicals": route.get_node("PracticalLights").lights.filter(func(light):return light.visible).size()}
  print(room, " ", report.views[room])
 report.texture_memory_bytes = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
 report.buffer_memory_bytes = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_BUFFER_MEM_USED)
 var file = FileAccess.open("res://demo-profile-desktop.json", FileAccess.WRITE)
 file.store_string(JSON.stringify(report, "  "))
 print("DEMO_PROFILE_PASS")
 quit(0)
