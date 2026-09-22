extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var mobile="--portrait" in OS.get_cmdline_user_args()
 root.size=Vector2i(390,844) if mobile else Vector2i(1410,600)
 root.content_scale_size=Vector2i.ZERO
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 Engine.max_fps=0
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var variant="no-shadows" if "--no-shadows" in OS.get_cmdline_user_args() else ("no-lights" if "--no-lights" in OS.get_cmdline_user_args() else "baseline")
 if "--baked" in OS.get_cmdline_user_args():
  variant="baked"
  var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/index.json"))
  var applied=load("res://runtime/baked_materials.gd").apply_to_scene(route,records)
  if applied != records.size() or applied <= 0:
   push_error("Incomplete bake coverage in benchmark")
   quit(1)
   return
 var lights={"directional":0,"spot":0,"omni_enabled":0}
 var nodes:Array[Node]=[route]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is Light3D:
   if variant in ["no-shadows","baked"]: node.shadow_enabled=false
   elif variant == "no-lights":node.visible=false
  if node is DirectionalLight3D:lights.directional+=1
  elif node is SpotLight3D:lights.spot+=1
  elif node is OmniLight3D and node.light_energy>0:lights.omni_enabled+=1
 var report={"device":RenderingServer.get_video_adapter_name(),"renderer":RenderingServer.get_current_rendering_method(),"viewport":[root.size.x,root.size.y],"samples_per_view":120,"vsync":"disabled","diagnostic_variant":variant,"scope":"Stationary arrival views on this Mac; not a mobile GPU result or a traversal benchmark.","lights":lights,"views":{}}
 for room in route.ROOMS:
  route.player.position = {"terminal_room":Vector3(-1.3,0,37.4),"rockery_gate":Vector3(0,0,32.5),"qinfang_ting":Vector3(0,0,1.8),"ouxiang_xie":Vector3(-23,0,0),"ziling_zhou":Vector3(-35.4,0,0),"qiushuang_zhai":Vector3(22,0,-13.5),"tubi_tang":Vector3(7,4,-31),"hengwu_yuan":Vector3(-18,0,-14.7),"daoxiang_cun":Vector3(-32,0,-19.3),"aojing_guan":Vector3(26,-.65,13.1),"longcui_an":Vector3(-25,0,10.6),"xiaoxiang_guan":Vector3(-6.6,0,13),"yihong_yuan":Vector3(22.6,0,1),"daguan_lou":Vector3(0,0,-20.5)}[room]+Vector3(0,.04,0)
  route._arrive(room,true)
  route.get_node("PracticalLights").update_lights()
  route.get_node("PracticalLights").set_process(false)
  if variant == "no-lights":
   var pending:Array[Node]=[route]
   while not pending.is_empty():
    var node=pending.pop_back()
    pending.append_array(node.get_children())
    if node is Light3D:node.visible=false
  for i in range(30):await process_frame
  var times:Array[float]=[]
  var draws:Array[int]=[]
  var shadow_draws:Array[int]=[]
  var primitives:Array[int]=[]
  var capture_draws:Array[int]=[]
  var previous=Time.get_ticks_usec()
  for i in range(120):
   await RenderingServer.frame_post_draw
   var now=Time.get_ticks_usec()
   var mirror=route.get_node("PondReflection")
   var extra=0
   if mirror.viewport.render_target_update_mode!=SubViewport.UPDATE_DISABLED:
    extra=RenderingServer.viewport_get_render_info(mirror.viewport.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME)+RenderingServer.viewport_get_render_info(mirror.viewport.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_SHADOW,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME)
   capture_draws.append(extra)
   times.append(float(now-previous)/1000.0)
   previous=now
   draws.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME))
   shadow_draws.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_SHADOW,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME))
   primitives.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_PRIMITIVES_IN_FRAME))
  times.sort();draws.sort();shadow_draws.sort();primitives.sort();capture_draws.sort()
  report.views[room]={"frame_interval_median_ms":times[60],"frame_interval_p95_ms":times[114],"visible_draw_calls_max":draws.back(),"shadow_draw_calls_max":shadow_draws.back(),"visible_primitives_max":primitives.back(),"reflection_capture_draw_calls_max":capture_draws.back(),"combined_draw_call_upper_bound":draws.back()+shadow_draws.back()+capture_draws.back(),"active_practicals":route.get_node("PracticalLights").lights.filter(func(light):return light.visible).size()}
  print(room," ",report.views[room])
 report.texture_memory_bytes=RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
 report.buffer_memory_bytes=RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_BUFFER_MEM_USED)
 var suffix="portrait" if mobile else "desktop"
 if variant != "baseline":suffix+="-"+variant
 var file=FileAccess.open("res://profile-"+suffix+".json",FileAccess.WRITE)
 file.store_string(JSON.stringify(report,"  "))
 print("PROFILE_SAVED ",suffix)
 quit(0)
