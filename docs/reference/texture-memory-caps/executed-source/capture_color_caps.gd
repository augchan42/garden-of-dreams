extends SceneTree

# Actual placed atlas materials at both arrivals and closer inspection views.
# This capture-only diagnostic records no frame timing or mobile acceptance.
func _initialize() -> void:
 call_deferred("run")

func settle() -> void:
 for frame in range(12):
  await process_frame
  RenderingServer.force_draw()

func pixel_rmse(a:Image,b:Image) -> float:
 var squared=0.0
 for y in range(a.get_height()):
  for x in range(a.get_width()):
   var ca=a.get_pixel(x,y)
   var cb=b.get_pixel(x,y)
   for channel in range(3):squared+=pow(ca[channel]-cb[channel],2)
 return sqrt(squared/(a.get_width()*a.get_height()*3))

func run() -> void:
 var folder = ""
 var expected_size = 2048
 var expected_orm_size = 2048
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--output-directory="):
   folder = argument.trim_prefix("--output-directory=")
  if argument.begins_with("--expected-size="):
   expected_size = int(argument.trim_prefix("--expected-size="))
  if argument.begins_with("--expected-orm-size="):
   expected_orm_size = int(argument.trim_prefix("--expected-orm-size="))
 assert(not folder.is_empty() and expected_size in [1024,2048] and expected_orm_size in [1024,2048])
 assert(DisplayServer.get_name() != "headless")
 assert(DirAccess.make_dir_recursive_absolute(folder) == OK)
 root.content_scale_size = Vector2i.ZERO
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var probe=DirectionalLight3D.new()
 probe.name="AtlasInspectionLight"
 probe.light_cull_mask=2
 probe.light_energy=.75
 probe.visible=false
 route.add_child(probe)
 route.set_process(false)
 route.set_physics_process(false)
 var report = {"scope": "Actual native Mac graphical fixed-clock basecolor-cap controls of placed Qinfang pavilion and Hengwu wall atlas materials, at arrival and closer views in desktop and portrait windows. No actual phone, final art or timing acceptance.", "source_glb_sha256": FileAccess.get_sha256("res://assets/garden-of-dreams.glb"), "renderer_device": RenderingServer.get_video_adapter_name(), "expected_size": expected_size, "expected_orm_size": expected_orm_size, "textures": {}, "captures": {}}
 report["renderer_files_sha256"]={"runtime/baked_materials.gd":FileAccess.get_sha256("res://runtime/baked_materials.gd"),"shaders/baked_diffuse.gdshader":FileAccess.get_sha256("res://shaders/baked_diffuse.gdshader")}
 for name in ["pavilion","wall"]:
  var path = "res://assets/garden-of-dreams_" + name + "_basecolor.png"
  var texture = load(path) as Texture2D
  assert(texture.get_size() == Vector2(expected_size,expected_size), "Basecolor candidate was not imported")
  assert(texture.get_image().has_mipmaps())
  report.textures[name] = {"size": [texture.get_width(),texture.get_height()], "source_png_sha256": FileAccess.get_sha256(path), "import_sha256": FileAccess.get_sha256(path + ".import")}
  var orm_path = "res://assets/garden-of-dreams_" + name + "_orm.png"
  var orm = load(orm_path) as Texture2D
  assert(orm.get_size() == Vector2(expected_orm_size,expected_orm_size),"ORM candidate was not imported")
  report.textures[name+"_orm"] = {"size": [orm.get_width(),orm.get_height()], "source_png_sha256": FileAccess.get_sha256(orm_path), "import_sha256": FileAccess.get_sha256(orm_path + ".import")}
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material = node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name == "timeline_time":material.set_shader_parameter("timeline_time",3.0)
 for shape in ["desktop","portrait"]:
  root.size = Vector2i(1410,600) if shape == "desktop" else Vector2i(390,844)
  await settle()
  for room in ["qinfang_ting","hengwu_yuan"]:
   route.player.position = (route.GATE_PATH[-1] if room == "qinfang_ting" else route.COURTYARD_PATH[-1]) + Vector3(0,.03,0)
   route.get_node("PracticalLights").update_lights()
   route._arrive(room,true)
   route.command_panel.hide()
   var mesh_name = "SITE_qinfang-ting_MAT_pavilion_atlas" if room == "qinfang_ting" else "SITE_hengwu-yuan_MAT_wall_atlas"
   var mesh = route.find_child(mesh_name,true,false) as MeshInstance3D
   assert(mesh != null)
   var material = mesh.get_active_material(0)
   assert(material is ShaderMaterial and material.get_shader_parameter("use_normal_texture"))
   assert(material.get_shader_parameter("albedo_texture").get_size() == Vector2(expected_size,expected_size))
   assert(material.get_shader_parameter("normal_texture").get_size() == Vector2(1024,1024))
   assert(material.get_shader_parameter("use_orm_texture") and material.get_shader_parameter("orm_texture").get_size() == Vector2(expected_orm_size,expected_orm_size))
   for view in ["arrival","close","pbr-probe"]:
    if view == "close":
     route._camera_to(Vector3(4,2.3,4) if room == "qinfang_ting" else Vector3(-17.6,1.65,-12),Vector3(0,1.3,0) if room == "qinfang_ting" else Vector3(-18,1.1,-15.2),true)
    if view=="pbr-probe" and room=="hengwu_yuan":
     # The portrait facade crops out the selected wall; inspect its west face.
     route._camera_to(Vector3(-19.5,1.8,-13),Vector3(-22.5,1.4,-14),true)
    probe.visible=view=="pbr-probe"
    probe.rotation=route.camera.rotation
    await settle()
    var label = shape + "-" + room + "-" + view
    var path = folder + "/" + label + ".png"
    var image = root.get_texture().get_image()
    assert(image.save_png(path) == OK)
    var transform = route.camera.global_transform
    report.captures[label] = {"sha256": FileAccess.get_sha256(path), "clock": 3.0, "image_size": [image.get_width(),image.get_height()], "camera_transform": [transform.basis.x,transform.basis.y,transform.basis.z,transform.origin], "normal_material_owner": str(mesh.name), "normal_scale": material.get_shader_parameter("normal_scale")}
    if view=="pbr-probe":
     var controls={}
     for flag in ["use_albedo_texture","use_normal_texture","use_orm_texture"]:
      material.set_shader_parameter(flag,false)
      await settle()
      var without=root.get_texture().get_image()
      controls[flag]=pixel_rmse(image,without)
      material.set_shader_parameter(flag,true)
      if controls[flag]<=.0001:
       push_error("Placed texture has no measured inspection-light effect: "+label+" "+flag)
       route.queue_free()
       await create_timer(.2).timeout
       quit(1)
       return
     report.captures[label]["missing_map_rmse"]=controls
   probe.visible=false
 var file = FileAccess.open(folder + "/report.json",FileAccess.WRITE)
 assert(file != null)
 file.store_string(JSON.stringify(report,"  "))
 file.close()
 print("NORMAL_ATLAS_CANDIDATE_CAPTURE_PASS size=",expected_size," views=",report.captures.size())
 route.queue_free()
 await create_timer(.2).timeout
 quit()
