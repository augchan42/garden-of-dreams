extends SceneTree

func _initialize() -> void:call_deferred("run")

func run() -> void:
 var output=""
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--output="):output=argument.trim_prefix("--output=")
 if output.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Portrait draw measurement requires native graphics and --output")
  quit(1)
  return
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(390,844)
 var report={"scope":"Stationary native 390x844 pavilion overview draw/primitive/allocation counters; not phone or sustained frame rate acceptance.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"views":{}}
 for mode in ["normal","demo"]:
  var route=load("res://runtime/entry_route.tscn" if mode=="normal" else "res://runtime/first_reading_demo.tscn").instantiate()
  root.add_child(route)
  route.player.position=Vector3(0,.03,1.8)
  route._arrive("qinfang_ting",true)
  route.get_node("PracticalLights").update_lights()
  for i in range(20):await process_frame
  var draws=[]
  var primitives=[]
  for i in range(12):
   RenderingServer.force_draw()
   draws.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_DRAW_CALLS_IN_FRAME))
   primitives.append(RenderingServer.viewport_get_render_info(root.get_viewport_rid(),RenderingServer.VIEWPORT_RENDER_INFO_TYPE_VISIBLE,RenderingServer.VIEWPORT_RENDER_INFO_PRIMITIVES_IN_FRAME))
  var memory=RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
  var lights=route.get_node("PracticalLights").lights.filter(func(light):return light.visible).size()
  report.views[mode]={"draw_calls_max":draws.max(),"primitives_max":primitives.max(),"texture_memory_bytes":memory,"active_practicals":lights}
  if draws.max()>150 or primitives.max()>300000 or memory>64*1024*1024 or lights>4:
   push_error("Portrait overview exceeds a rendering budget")
   FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
   quit(1)
   return
  if mode=="demo":
   for player in route.demo_audio.players.values():player.stop()
  route.queue_free()
  await create_timer(.3).timeout
 FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 print("PAVILION_PORTRAIT_BUDGET_PASS ",report.views)
 quit(0)
