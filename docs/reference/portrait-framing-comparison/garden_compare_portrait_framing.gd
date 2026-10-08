extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var output := "/tmp/garden-portrait-framing-native"
 DirAccess.make_dir_recursive_absolute(output)
 var plan = JSON.parse_string(FileAccess.get_file_as_string("/tmp/garden-portrait-framing-proposals.json"))
 if DisplayServer.get_name() == "headless" or plan.source_glb_sha256 != FileAccess.get_sha256("res://assets/garden-of-dreams.glb"):
  push_error("Portrait comparison requires native renderer and matching source")
  quit(1)
  return
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 for frame in range(12): await process_frame
 var rows := []
 for size in [Vector2i(390,844),Vector2i(360,800)]:
  root.size = size
  route._configure_ui_scale(false,160)
  for frame in range(12): await process_frame
  for room in plan.rooms:
   var record: Dictionary = plan.rooms[room]
   for variant in ["baseline","candidate"]:
    route._arrive(room,true)
    if variant == "candidate":
     var p: Array = record.candidate_position
     var t: Array = record.candidate_target
     route.camera.keep_aspect = Camera3D.KEEP_WIDTH
     route.camera.fov = record.candidate_fov
     route._camera_to(Vector3(p[0],p[1],p[2]),Vector3(t[0],t[1],t[2]),true)
    for frame in range(12): await process_frame
    var low := Vector2(INF,INF)
    var high := Vector2(-INF,-INF)
    var behind := 0
    for name in record.meshes:
     var mesh = route.find_child(name,true,false) as MeshInstance3D
     if mesh == null:
      push_error("Missing comparison mesh: "+name)
      quit(1)
      return
     for surface in range(mesh.mesh.get_surface_count()):
      for local in mesh.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
       var world: Vector3 = mesh.global_transform * local
       if route.camera.is_position_behind(world): behind += 1
       var pixel: Vector2 = route.camera.unproject_position(world)
       low = low.min(pixel)
       high = high.max(pixel)
    await RenderingServer.frame_post_draw
    var path: String = output+"/%s-%s-%dx%d.png"%[room,variant,size.x,size.y]
    var saved: Error = root.get_texture().get_image().save_png(path)
    if saved != OK:
     push_error("Cannot save native comparison")
     quit(1)
     return
    var panel: Rect2 = route.command_panel.get_global_rect()
    var header: Rect2 = route.status.get_global_rect()
    var visible: Vector2 = root.get_visible_rect().size
    rows.append({"room":room,"variant":variant,"requested_size":[size.x,size.y],
     "viewport":[visible.x,visible.y],"hero_bounds":[[low.x,low.y],[high.x,high.y]],
     "behind_camera":behind,"panel_top":panel.position.y,"header_bottom":header.end.y,
     "fits_between_interface":behind==0 and low.x>=8 and high.x<=visible.x-8 and low.y>=header.end.y+8 and high.y<=panel.position.y-8,
     "capture":path,"sha256":FileAccess.get_sha256(path),
     "camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"fov":route.camera.fov})
 var file := FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"native_comparisons_recorded_visual_decision_pending",
  "source_glb_sha256":plan.source_glb_sha256,"rows":rows,
  "scope":"Diagnostic camera-only comparisons on current source. Arrival state is selected directly; this does not prove travel, action persistence, resizing, authored camera synchronization or final art acceptance."}," ")+"\n")
 file.close()
 print("PORTRAIT_NATIVE_COMPARISONS_RECORDED ",rows.size())
 quit(0)
