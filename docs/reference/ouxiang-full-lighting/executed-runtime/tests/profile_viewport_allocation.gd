extends SceneTree

# Native allocation diagnostic: fresh process per size/density. No FPS or route
# acceptance claim; stationary cameras isolate viewport-dependent allocations.
func _initialize() -> void:
 call_deferred("run")

func snapshot(route: Node, label: String) -> Dictionary:
 var window_texture = root.get_texture()
 var before = RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
 var native_image = RenderingServer.texture_2d_get(RenderingServer.viewport_get_texture(root.get_viewport_rid()))
 assert(native_image != null)
 var inventory = preload("res://tests/texture_binding_inventory.gd").new().collect(route)
 return {"state": label, "texture_memory_before_readback_bytes": before,
  "texture_memory_after_readback_bytes": RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED),
  "native_image_size": [native_image.get_width(),native_image.get_height()],
  "native_image_format": native_image.get_format(), "native_image_data_bytes": native_image.get_data_size(),
  "window_texture_metadata_size": [window_texture.get_width(),window_texture.get_height()],
  "logical_viewport_size": [root.get_visible_rect().size.x,root.get_visible_rect().size.y],
  "ui_content_scale_factor": root.content_scale_factor, "viewport_oversampling": root.get_oversampling(),
  "viewport_oversampling_override": root.get_oversampling_override(),
  "viewport_use_oversampling": root.is_using_oversampling(), "texture_inventory": inventory}

func settle() -> void:
 for frame in range(60):await process_frame
 await RenderingServer.frame_post_draw

func run() -> void:
 var width = 1410
 var height = 600
 var dpi = 0
 var output = ""
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--width="):width=argument.trim_prefix("--width=").to_int()
  if argument.begins_with("--height="):height=argument.trim_prefix("--height=").to_int()
  if argument.begins_with("--ui-dpi="):dpi=argument.trim_prefix("--ui-dpi=").to_int()
  if argument.begins_with("--output="):output=argument.trim_prefix("--output=")
 assert(width>0 and height>0 and not output.is_empty())
 root.size = Vector2i(width,height)
 Engine.max_fps = 60
 var route = load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 route._configure_ui_scale(dpi>0,dpi)
 await settle()
 var report = {"scope": "Fresh native Mac process at a declared window size and UI density. Actual renderer totals/readbacks and bound texture inventory; no gameplay timing, actual Android, full traversal or final art acceptance.",
  "device": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method(),
  "source_glb_sha256": FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),
  "script_sha256": FileAccess.get_sha256("res://tests/profile_viewport_allocation.gd"),
  "inventory_script_sha256": FileAccess.get_sha256("res://tests/texture_binding_inventory.gd"),
  "requested_window_size": [width,height], "requested_ui_dpi": dpi, "samples": []}
 var positions = {"terminal_room": Vector3(-1.3,.03,37.4), "rockery_gate": Vector3(0,.03,32.5), "qinfang_ting": Vector3(0,.03,1.8)}
 for room in positions:
  route.player.position = positions[room]
  route._arrive(room,true)
  route.get_node("PracticalLights").update_lights()
  await settle()
  report.samples.append(snapshot(route,room))
 route.execute_command("table")
 route.cast_rng.seed=2817
 route.execute_command("cast")
 await settle()
 report.samples.append(snapshot(route,"reading"))
 route.get_node("ReadingResult").find_child("CloseReading",true,false).pressed.emit()
 await settle()
 route.execute_command("finish")
 await settle()
 report.samples.append(snapshot(route,"finale"))
 var file=FileAccess.open(output,FileAccess.WRITE)
 assert(file!=null)
 file.store_string(JSON.stringify(report,"  "))
 file.close()
 for player in route.demo_audio.players.values():player.stop()
 route.queue_free()
 await create_timer(.2).timeout
 print("VIEWPORT_ALLOCATION_DIAGNOSTIC_PASS ",width,"x",height," dpi=",dpi)
 quit(0)
