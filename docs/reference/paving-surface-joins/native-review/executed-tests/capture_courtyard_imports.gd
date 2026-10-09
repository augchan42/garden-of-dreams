extends SceneTree

# Capture the actual imported maps at four normal arrival views.
# Frozen clocks allow pixel comparison; this does not exercise traversal.
func _initialize():
 call_deferred("run")

func freeze_clocks(route:Node):
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.0)
 for node in route.find_children("*","Node",true,false):
  node.set_process(false)
  node.set_physics_process(false)
 route.set_process(false)
 route.set_physics_process(false)

func run():
 var directory=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):directory=arg.trim_prefix("--output=")
 assert(not directory.is_empty() and DisplayServer.get_name()!="headless")
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 root.size=Vector2i(540,960)
 root.content_scale_size=Vector2i.ZERO
 var report={"status":"running","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"shader_sha256":FileAccess.get_sha256("res://shaders/baked_diffuse.gdshader"),"test_script_sha256":FileAccess.get_sha256("res://tests/capture_courtyard_imports.gd"),"viewport":[540,960],"scope":"Actual normal-route imports at four frozen arrival views. No material counterfactuals, traversal, final-site art or target-device performance acceptance.","rooms":{},"facade_maps":{}}
 var rooms={"qinfang_ting":Vector3(0,.04,1.8),"xiaoxiang_guan":Vector3(-6.6,.04,13),"daoxiang_cun":Vector3(-32,.04,-19.3),"daguan_lou":Vector3(0,.04,-20.5)}
 for room in rooms:
  var route=load("res://runtime/entry_route.tscn").instantiate()
  root.add_child(route)
  route.player.position=rooms[room]
  route._arrive(room,true)
  await create_timer(1.6).timeout
  route.get_node("PracticalLights").update_lights()
  freeze_clocks(route)
  if room=="xiaoxiang_guan":
   for name in ["SITE_xiaoxiang-guan_MAT_whitewash","SITE_xiaoxiang-guan_MAT_lattice_wood"]:
    var mesh=route.find_child(name,true,false) as MeshInstance3D
    assert(mesh!=null)
    var material=mesh.get_active_material(0) as ShaderMaterial
    var texture=material.get_shader_parameter("lightmap") as Texture2D
    var image=texture.get_image()
    var settings=ConfigFile.new()
    assert(settings.load(texture.resource_path+".import")==OK)
    assert(settings.get_value("params","compress/mode")==0)
    assert(settings.get_value("params","process/size_limit")==512)
    assert(image.get_format()==Image.FORMAT_RGB8)
    assert(texture.get_width()==(512 if name.ends_with("whitewash") else 256))
    report.facade_maps[name]={"source_sha256":FileAccess.get_sha256(texture.resource_path),"import_sha256":FileAccess.get_sha256(texture.resource_path+".import"),"size":[texture.get_width(),texture.get_height()],"format":image.get_format(),"image_bytes":image.get_data_size()}
  for frame in range(5):await process_frame
  await RenderingServer.frame_post_draw
  var image=root.get_texture().get_image()
  var path=directory+"/"+room+".png"
  assert(image.save_png(path)==OK)
  report.rooms[room]={"path":path,"sha256":FileAccess.get_sha256(path),"camera_transform":str(route.camera.global_transform),"visitor_position":str(route.player.position)}
  route.queue_free()
  for frame in range(5):await process_frame
 report.status="passed"
 var file=FileAccess.open(directory+"/report.json",FileAccess.WRITE)
 assert(file!=null)
 file.store_string(JSON.stringify(report,"  ")+"\n")
 file.close()
 print("COURTYARD_IMPORT_CAPTURE_PASS: four actual views, two lossless maps")
 quit()
