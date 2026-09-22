extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1)
 route._arrive("aojing_guan",true)
 route.execute_command("reflection")
 await create_timer(1.6).timeout
 var mirror=route.get_node("PondReflection")
 var report={"device":RenderingServer.get_video_adapter_name(),"scope":"Stationary desktop pond view; dynamic shadows still enabled. Not target-phone performance.","variants":{}}
 for active in [true,false]:
  mirror.set_process(active)
  mirror.viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS if active else SubViewport.UPDATE_DISABLED
  for i in range(30):await process_frame
  var times:Array[float]=[]
  var previous=Time.get_ticks_usec()
  for i in range(120):
   await RenderingServer.frame_post_draw
   var now=Time.get_ticks_usec()
   times.append(float(now-previous)/1000.0)
   previous=now
  times.sort()
  var visible=RenderingServer.viewport_get_render_info(mirror.viewport.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME) if active else 0
  var shadows=RenderingServer.viewport_get_render_info(mirror.viewport.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_SHADOW,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME) if active else 0
  report.variants["capture_active" if active else "capture_frozen"]={"median_frame_interval_ms":times[60],"capture_visible_draws":visible,"capture_shadow_draws":shadows,"texture_memory_bytes":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED),"capture_size":[mirror.viewport.size.x,mirror.viewport.size.y]}
 FileAccess.open("res://profile-reflection.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("REFLECTION_PROFILE ",report)
 quit(0)
