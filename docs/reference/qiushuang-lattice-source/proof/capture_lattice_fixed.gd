extends SceneTree

const SOURCE = "72ad817f07e1fb13b565197f0a39984a2d97bc1c7c3dff6c1bccf3ae1125cab1"

func _initialize():
 create_timer(150).timeout.connect(func():push_error("QIUSHUANG_LATTICE_LIT_DEADLINE");quit(1))
 call_deferred("run")

func run():
 var directory=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):directory=arg.trim_prefix("--output=")
 assert(not directory.is_empty() and DisplayServer.get_name()!="headless")
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 assert(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE)
 for filename in ["full-index.json","backdrop-wash-index.json","terminal-spill-index.json"]:
  var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/"+filename))
  assert(records is Dictionary and preload("res://runtime/baked_materials.gd").source_matches(records))
 var report={"status":"running","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"scope":"Native current-source lit Qiushuang bank and overview views using complete matching lighting. No live bulletin content, traversal, phone, final all-site art or performance acceptance.","fixed_clock":3.0,"captures":[]}
 for shape in ["desktop","portrait"]:
  root.size=Vector2i(1410,600) if shape=="desktop" else Vector2i(540,960)
  root.content_scale_size=Vector2i.ZERO
  for action in ["overview","left","centre","right"]:
   var route=load("res://runtime/entry_route.tscn").instantiate()
   assert(route.site_bakes_enabled and not route.demo_mode)
   root.add_child(route)
   # Freeze every animated scene shader equally in both comparison projects.
   for node in route.find_children("*","MeshInstance3D",true,false):
    for surface in range(node.mesh.get_surface_count()):
     var material=node.get_active_material(surface)
     if material is ShaderMaterial:
      for uniform in material.shader.get_shader_uniform_list():
       if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.)
   route.get_node("PondReflection").material.set_shader_parameter("timeline_time",3.)
   route.player.position=Vector3(22,.04,-13.5)
   route._arrive("qiushuang_zhai",true)
   await create_timer(1.6).timeout
   if action!="overview":
    route.execute_command(action)
    await create_timer(1.6).timeout
   for node in route.find_children("*","Node",true,false):
    node.set_process(false)
    node.set_physics_process(false)
   route.set_process(false)
   route.set_physics_process(false)
   for frame in range(6):await process_frame
   # A static viewport may not schedule another automatic draw after the
   # settling frames. Submit the native frame synchronously before readback.
   RenderingServer.force_draw(false)
   var image=root.get_texture().get_image()
   var path=directory+"/"+shape+"-"+action+".png"
   assert(image.save_png(path)==OK)
   var tech=route.find_child("SITE_qiushuang-zhai_MAT_tech_atlas",true,false) as MeshInstance3D
   assert(tech!=null and tech.mesh.get_surface_count()==1)
   var tech_triangles=tech.mesh.surface_get_arrays(0)[Mesh.ARRAY_INDEX].size()/3
   assert(tech_triangles==10272)
   report.captures.append({"shape":shape,"action":action,"path":path,"sha256":FileAccess.get_sha256(path),"size":[image.get_width(),image.get_height()],"camera_transform":str(route.camera.global_transform),"camera_fov":route.camera.fov,"camera_aspect":route.camera.keep_aspect,"tech_batch_triangles":tech_triangles,"site_bakes_enabled":route.site_bakes_enabled})
   route.queue_free()
   for frame in range(6):await process_frame
 report.status="passed"
 var file=FileAccess.open(directory+"/report.json",FileAccess.WRITE)
 assert(file!=null)
 file.store_string(JSON.stringify(report,"  ")+"\n")
 file.close()
 print("QIUSHUANG_LATTICE_LIT_PASS: eight current-source lit views, batched tech retained")
 quit()
