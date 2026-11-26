extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 var directory="res://../docs/reference"
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--output-directory="):directory=argument.trim_prefix("--output-directory=")
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 var report={"scope":"Actual native outbound reveal images and poses; not sustained FPS or target-phone acceptance.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"captures":{}}
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route._arrive("rockery_gate",true);route.player.position=Vector3(-1.273,.04,20.5)
 route._camera_to(Vector3(-1.273,1.6,21.6),Vector3(0,1.2,19),true)
 await create_timer(.5).timeout
 route._travel(route.GATE_PATH.slice(8),"qinfang_ting")
 for i in range(600):
  await physics_frame
  if route.gate_reveal_active:break
 if not route.gate_reveal_active:
  push_error("Walking route did not reach reveal");quit(1);return
 print("REVEAL_START_CAMERA ",route.camera.position)
 if "--fixed-clock" in OS.get_cmdline_user_args():
  for mesh in route.find_children("*","MeshInstance3D",true,false):
   for surface in range(mesh.mesh.get_surface_count()):
    var material=mesh.get_active_material(surface)
    if material is ShaderMaterial:
     for uniform in material.shader.get_shader_uniform_list():
      if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.0)
 var previous=0.0
 for t in [.1,.4,.8,1.2,1.6,2.4,3.4,4.1]:
  await create_timer(t-previous).timeout;previous=t
  await process_frame
  RenderingServer.force_draw()
  var label=("mobile-" if mobile else "")+"gate-reveal-"+str(t)
  var file=directory+"/"+label+".png"
  assert(root.get_texture().get_image().save_png(file)==OK)
  report.captures[label]={"image_sha256":FileAccess.get_sha256(file),"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"fov":route.camera.fov,"keep_aspect":route.camera.keep_aspect,"command_panel_visible":route.command_panel.visible}
  print("GATE_REVEAL_RENDER_SAVED ",label)
 FileAccess.open(directory+"/reveal-report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 route.queue_free()
 await create_timer(.3).timeout
 print("GATE_REVEAL_RENDER_PASS captures=",report.captures.size())
 quit(0)
