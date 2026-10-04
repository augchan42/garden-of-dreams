extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 var full_baked="--full-baked" in OS.get_cmdline_user_args()
 if full_baked:route.site_bakes_enabled=false
 root.add_child(route)
 if full_baked:
  var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
  assert(preload("res://runtime/baked_materials.gd").apply_to_scene(route,records)==records.size())
  for light in route.find_children("*","Light3D",true,false):
   if light is SpotLight3D or light is DirectionalLight3D:light.shadow_enabled=false
 route.player.position=Vector3(26,-.61,13.1)
 route._arrive("aojing_guan",true)
 route.execute_command("reflection")
 await create_timer(1.6).timeout
 var mirror=route.get_node("PondReflection")
 var report={"device":RenderingServer.get_video_adapter_name(),"viewport":[root.size.x,root.size.y],"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"scope":"Stationary desktop pond view; all 124 static bakes enabled, static shadows disabled. Main and reflection capture recorded separately. Not target-phone or full-traversal performance.","variants":{}}
 if full_baked:report.scope="Experimental complete-garden bakes, static shadows disabled, linked backdrop wash retained. Stationary desktop pond view; not production or phone/traversal acceptance."
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
  var main_visible=RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME)
  var main_shadows=RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_SHADOW,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME)
  var main_primitives=RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_PRIMITIVES_IN_FRAME)
  var capture_primitives=RenderingServer.viewport_get_render_info(mirror.viewport.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_PRIMITIVES_IN_FRAME) if active else 0
  report.variants["capture_active" if active else "capture_frozen"]={"median_frame_interval_ms":times[60],"main_visible_draws":main_visible,"main_shadow_draws":main_shadows,"capture_visible_draws":visible,"capture_shadow_draws":shadows,"visible_draws_combined":main_visible+visible,"visible_primitives_combined":main_primitives+capture_primitives,"texture_memory_bytes":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED),"capture_size":[mirror.viewport.size.x,mirror.viewport.size.y]}
 FileAccess.open("res://profile-reflection-full-baked.json" if full_baked else "res://profile-reflection.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("REFLECTION_PROFILE ",report)
 quit(0)
