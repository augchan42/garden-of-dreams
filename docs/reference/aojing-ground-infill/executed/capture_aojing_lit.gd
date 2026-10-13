extends SceneTree
func _initialize():
 create_timer(180).timeout.connect(func():push_error("AOJING_LIT_DEADLINE");quit(1))
 call_deferred("run")
func run():
 var directory=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):directory=arg.trim_prefix("--output=")
 assert(not directory.is_empty() and DisplayServer.get_name()!="headless")
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 for filename in ["full-index.json","backdrop-wash-index.json","terminal-spill-index.json"]:
  var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/"+filename))
  assert(records is Dictionary and preload("res://runtime/baked_materials.gd").source_matches(records))
 var source=FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 assert(source=="09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290")
 var report={"status":"running","source_glb_sha256":source,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"fixed_clock":3.0,"captures":[],"scope":"Actual full-lit native Aojing arrival, public doors/reflection actions and one separate west-strip inspection pose. No traversal, device/performance or final art acceptance."}
 var poses={"west_strip":[Vector3(16.5,3.8,18.5),Vector3(20,-.2,17.5)]}
 for shape in ["desktop","portrait"]:
  root.size=Vector2i(1410,600) if shape=="desktop" else Vector2i(390,844)
  root.content_scale_size=Vector2i.ZERO
  for action in ["arrival","doors","reflection","west_strip"]:
   var route=load("res://runtime/entry_route.tscn").instantiate()
   root.add_child(route)
   assert(route.site_bakes_enabled and not route.demo_mode)
   route.player.position=Vector3(26,-.61,13.1)
   route._arrive("aojing_guan",true)
   await create_timer(1.8).timeout
   if action in ["doors","reflection"]:
    route.execute_command(action)
    await create_timer(1.8).timeout
   if poses.has(action):
    route.camera.global_position=poses[action][0]
    route.camera.look_at(poses[action][1],Vector3.UP)
    route.camera.fov=48
   assert(not route.camera_tween or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
   for node in route.find_children("*","MeshInstance3D",true,false):
    for surface in range(node.mesh.get_surface_count()):
     var material=node.get_active_material(surface)
     if material is ShaderMaterial:
      for uniform in material.shader.get_shader_uniform_list():
       if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.0)
   route.get_node("PondReflection").material.set_shader_parameter("timeline_time",3.0)
   for node in route.find_children("*","Node",true,false):
    node.set_process(false)
    node.set_physics_process(false)
   route.set_process(false)
   route.set_physics_process(false)
   for frame in range(8):await process_frame
   RenderingServer.force_draw(false)
   var image=root.get_texture().get_image()
   var path=directory+"/"+shape+"-"+action+".png"
   assert(image.get_size()==root.size and image.save_png(path)==OK)
   var receiver=route.find_child("SITE_stage_MAT_stage_canvas",true,false) as MeshInstance3D
   var material=receiver.get_active_material(0) as ShaderMaterial
   var texture=material.get_shader_parameter("lightmap") as Texture2D
   assert(texture!=null and texture.get_width()>0 and texture.get_height()>0)
   report.captures.append({"shape":shape,"action":action,"path":path,"sha256":FileAccess.get_sha256(path),"size":[image.get_width(),image.get_height()],"room_id":route.room_id,"camera_transform":str(route.camera.global_transform),"camera_fov":route.camera.fov,"camera_aspect":route.camera.keep_aspect,"diagnostic_camera":poses.has(action),"site_bakes_enabled":route.site_bakes_enabled,"source_map_sha256":FileAccess.get_sha256(texture.resource_path),"native_map_size":[texture.get_width(),texture.get_height()]})
   print("AOJING_LIT_CAPTURE ",shape," ",action)
   route.queue_free()
   for frame in range(8):await process_frame
 report.status="passed"
 var file=FileAccess.open(directory+"/report.json",FileAccess.WRITE)
 assert(file!=null)
 file.store_string(JSON.stringify(report,"  ")+"\n")
 file.close()
 print("AOJING_LIT_PASS 8 full-lit native Aojing public/ground views")
 quit()
