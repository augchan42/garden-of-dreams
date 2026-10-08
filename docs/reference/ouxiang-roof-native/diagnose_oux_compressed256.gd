extends SceneTree
var directory:String
func bytes_sha256(data:PackedByteArray)->String:
 var context=HashingContext.new();assert(context.start(HashingContext.HASH_SHA256)==OK);assert(context.update(data)==OK);return context.finish().hex_encode()
func _initialize():call_deferred("run")
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
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):directory=arg.trim_prefix("--output=")
 assert(not directory.is_empty() and DisplayServer.get_name()!="headless")
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 var record=JSON.parse_string(FileAccess.get_file_as_string("res://tests/oux-chart-lightmap.json"))
 assert(record.source_glb_sha256==FileAccess.get_sha256("res://tests/oux-chart-candidate.glb"))
 var report={"status":"running","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"candidate_glb_sha256":record.source_glb_sha256,"candidate_lightmap_sha256":FileAccess.get_sha256("res://tests/oux-chart-lightmap.png"),"candidate_lightmap_record":record,"test_script_sha256":FileAccess.get_sha256("res://tests/diagnose_oux_compressed256.gd"),"scope":"Only the Ouxiang roof mesh and its actual fresh candidate bake are swapped in the isolated current scene. Other geometry/maps/lights/materials/UI remain the baseline. No old map relabelling, whole-candidate lighting, production adoption, traversal, final art or performance claim.","views":{}}
 for view in ["portrait","desktop","roof-close","portrait-water"]:
  root.size=Vector2i(390,844) if view.begins_with("portrait") else Vector2i(1410,600)
  root.content_scale_size=Vector2i.ZERO
  var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
  route.player.position=Vector3(-19.5,.04,0);route._arrive("ouxiang_xie",true)
  await create_timer(1.6).timeout
  route.get_node("PracticalLights").update_lights();freeze_clocks(route)
  if view=="roof-close":
   route.camera.position=Vector3(-17,7.5,7);route.camera.look_at(Vector3(-23,3.5,0));route.camera.fov=45
  if view=="portrait-water":
   var target=Vector3(-23,0.5,0)
   route.camera.position=target+(Vector3(-15,5,10)-target)*2.0
   route.camera.look_at(target);route.camera.fov=55
  var mesh=route.find_child("SITE_ouxiang-xie_MAT_rooftile",true,false) as MeshInstance3D
  var original_mesh=mesh.mesh;var original=mesh.get_active_material(0) as ShaderMaterial
  var candidate=load("res://tests/oux-chart-candidate.glb").instantiate();root.add_child(candidate);candidate.hide()
  var new_mesh=candidate.find_child("SITE_ouxiang-xie_MAT_rooftile",true,false) as MeshInstance3D
  assert(mesh.global_transform.is_equal_approx(new_mesh.global_transform))
  var old_path=directory.get_base_dir()+"/source-control-roof.png"
  assert(FileAccess.get_sha256(old_path)==FileAccess.get_sha256("res://lightmaps/SITE_ouxiang-xie_MAT_rooftile.png"))
  var old_native=Image.load_from_file(old_path)
  var old_image=old_native.duplicate();old_image.resize(256,256,Image.INTERPOLATE_LANCZOS)
  var native_path=directory.get_base_dir()+"/export/lightmaps/SITE_ouxiang-xie_MAT_rooftile.png"
  assert(FileAccess.get_sha256(native_path)==FileAccess.get_sha256("res://tests/oux-chart-lightmap.png"))
  var native=Image.load_from_file(native_path)
  var lossless256=native.duplicate();lossless256.resize(256,256,Image.INTERPOLATE_LANCZOS)
  var lossless512=native.duplicate();lossless512.resize(512,512,Image.INTERPOLATE_LANCZOS)
  var imported=load("res://tests/oux-chart-lightmap.png") as Texture2D
  assert(imported.get_width()==256)
  report["candidate_import"]={"width":imported.get_width(),"height":imported.get_height(),"format":imported.get_image().get_format(),"data_bytes":imported.get_image().get_data().size(),"image_sha256":bytes_sha256(imported.get_image().get_data()),"import_params_sha256":FileAccess.get_sha256("res://tests/oux-chart-lightmap.png.import")}
  report.views[view]={"viewport":[root.size.x,root.size.y],"camera_transform":str(route.camera.global_transform),"cases":{}}
  for label in ["baseline","baseline-lossless256","baseline-lossless-native","candidate-import256","candidate-lossless256","candidate-lossless512","candidate-lossless-native","baseline-again"]:
   mesh.mesh=new_mesh.mesh if label.begins_with("candidate") else original_mesh
   var current=original.duplicate() as ShaderMaterial
   if label=="baseline-lossless256":current.set_shader_parameter("lightmap",ImageTexture.create_from_image(old_image))
   if label=="baseline-lossless-native":current.set_shader_parameter("lightmap",ImageTexture.create_from_image(old_native))
   if label.begins_with("candidate"):
    var chosen:Texture2D=imported
    if label=="candidate-lossless256":chosen=ImageTexture.create_from_image(lossless256)
    if label=="candidate-lossless512":chosen=ImageTexture.create_from_image(lossless512)
    if label=="candidate-lossless-native":chosen=ImageTexture.create_from_image(native)
    current.set_shader_parameter("lightmap",chosen)
    current.set_shader_parameter("lightmap_scale",record.scale)
   mesh.set_surface_override_material(0,current)
   for frame in range(5):await process_frame
   await RenderingServer.frame_post_draw
   var image=root.get_texture().get_image();var path=directory+"/"+view+"-"+label+".png";assert(image.save_png(path)==OK)
   report.views[view].cases[label]={"path":path,"sha256":FileAccess.get_sha256(path)}
  candidate.queue_free();route.queue_free()
  for frame in range(5):await process_frame
 report.status="passed"
 var file=FileAccess.open(directory+"/report.json",FileAccess.WRITE);assert(file!=null);file.store_string(JSON.stringify(report,"  ")+"\n");file.close()
 print("OUX_CHART_NATIVE_COMPARISON_PASS: four views, fresh candidate Ouxiang roof bake")
 quit()
