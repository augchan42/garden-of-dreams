extends SceneTree
var directory:String
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
 var record=JSON.parse_string(FileAccess.get_file_as_string("res://tests/tile-ridge-lightmap.json"))
 assert(record.source_glb_sha256==FileAccess.get_sha256("res://tests/tile-ridge-candidate.glb"))
 var report={"status":"running","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"candidate_glb_sha256":record.source_glb_sha256,"candidate_lightmap_sha256":FileAccess.get_sha256("res://tests/tile-ridge-lightmap.png"),"candidate_lightmap_record":record,"test_script_sha256":FileAccess.get_sha256("res://tests/diagnose_tile_ridge_candidate.gd"),"scope":"Only the Qinfang atlas mesh and its actual fresh candidate bake are swapped in the isolated current scene. Other geometry/maps/lights/materials/UI remain the baseline. No old map relabelling, whole-candidate lighting, production adoption, traversal, final art or performance claim.","views":{}}
 for view in ["portrait","desktop","roof-close"]:
  root.size=Vector2i(540,960) if view=="portrait" else Vector2i(1410,600)
  root.content_scale_size=Vector2i.ZERO
  var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
  route.player.position=Vector3(0,.04,1.8);route._arrive("qinfang_ting",true)
  await create_timer(1.6).timeout
  route.get_node("PracticalLights").update_lights();freeze_clocks(route)
  if view=="roof-close":
   route.camera.position=Vector3(4.5,5.3,8);route.camera.look_at(Vector3(0,4.1,0));route.camera.fov=50
  var mesh=route.find_child("SITE_qinfang-ting_MAT_pavilion_atlas",true,false) as MeshInstance3D
  var original_mesh=mesh.mesh;var original=mesh.get_active_material(0) as ShaderMaterial
  var candidate=load("res://tests/tile-ridge-candidate.glb").instantiate();root.add_child(candidate);candidate.hide()
  var new_mesh=candidate.find_child("SITE_qinfang-ting_MAT_pavilion_atlas",true,false) as MeshInstance3D
  assert(mesh.global_transform.is_equal_approx(new_mesh.global_transform))
  var old_path=directory.get_base_dir()+"/source-control-roof.png"
  assert(FileAccess.get_sha256(old_path)==FileAccess.get_sha256("res://lightmaps/SITE_qinfang-ting_MAT_pavilion_atlas.png"))
  var old_image=Image.load_from_file(old_path);old_image.resize(256,256,Image.INTERPOLATE_LANCZOS)
  var native_path=directory.get_base_dir()+"/export/lightmaps/SITE_qinfang-ting_MAT_pavilion_atlas.png"
  assert(FileAccess.get_sha256(native_path)==FileAccess.get_sha256("res://tests/tile-ridge-lightmap.png"))
  var native=Image.load_from_file(native_path)
  var imported=load("res://tests/tile-ridge-lightmap.png") as Texture2D
  assert(imported.get_width()==256)
  report.views[view]={"viewport":[root.size.x,root.size.y],"camera_transform":str(route.camera.global_transform),"cases":{}}
  for label in ["baseline","baseline-lossless256","candidate-import256","candidate-lossless-native","baseline-again"]:
   mesh.mesh=new_mesh.mesh if label.begins_with("candidate") else original_mesh
   var current=original.duplicate() as ShaderMaterial
   if label=="baseline-lossless256":current.set_shader_parameter("lightmap",ImageTexture.create_from_image(old_image))
   if label.begins_with("candidate"):
    current.set_shader_parameter("lightmap",ImageTexture.create_from_image(native) if label=="candidate-lossless-native" else imported)
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
 print("TILE_RIDGE_NATIVE_COMPARISON_PASS: three views, fresh candidate roof bake")
 quit()
