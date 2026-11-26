extends SceneTree

# Counterfactual native camera captures. Does not change production camera/source.
func _initialize() -> void:call_deferred("run")

func run() -> void:
 var directory=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-directory="):directory=arg.trim_prefix("--output-directory=")
 if directory.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Pavilion framing probe needs a native window and output directory")
  quit(1)
  return
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.set_process(false)
 route.set_physics_process(false)
 route.player.position=Vector3(0,.04,1.8)
 for mesh in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(mesh.mesh.get_surface_count()):
   var material=mesh.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.0)
 var variants={
  "baseline":[Vector3(14,6.98,16.8),Vector3(0,1.8,0),55.0],
  "south-six":[Vector3(6,6.98,20),Vector3(0,1.8,0),55.0],
  "south-eight":[Vector3(8,6.98,20),Vector3(0,1.8,0),55.0],
  "south-six-low":[Vector3(6,5.5,20),Vector3(0,1.8,0),55.0],
  "south-six-close":[Vector3(6,6.4,18),Vector3(0,1.8,0),55.0],
  "south-eight-aim":[Vector3(8,6.98,20),Vector3(0,1.8,-2),55.0],
  "south-six-narrow":[Vector3(6,6.98,20),Vector3(0,1.8,0),50.0]}
 var moon=route.find_child("SITE_stage_MAT_painted_moon",true,false) as MeshInstance3D
 assert(moon!=null)
 var report={"scope":"Native portrait Qinfang camera counterfactuals; scene/source/production cameras unchanged. Projection and captures do not prove other rooms or continuous transitions.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"views":{}}
 for label in variants:
  route._arrive("qinfang_ting",true)
  var view=variants[label]
  route.camera.keep_aspect=Camera3D.KEEP_HEIGHT
  route.camera.fov=view[2]
  route._camera_to(view[0],view[1],true)
  await create_timer(.5).timeout
  await process_frame
  RenderingServer.force_draw()
  var image=root.get_texture().get_image()
  var path=directory+"/"+label+".png"
  assert(image.save_png(path)==OK)
  var moon_bounds=[]
  var inside=0
  for i in range(8):
   var point=moon.global_transform*moon.get_aabb().get_endpoint(i)
   var projected=route.camera.unproject_position(point)
   moon_bounds.append([projected.x,projected.y])
   if not route.camera.is_position_behind(point) and Rect2(Vector2(0,60),Vector2(root.size.x,route.command_panel.position.y-60)).has_point(projected):inside+=1
  report.views[label]={"position":[view[0].x,view[0].y,view[0].z],"target":[view[1].x,view[1].y,view[1].z],"vertical_fov":view[2],"moon_bounds_screen":moon_bounds,"moon_bounds_inside_clear_scene":inside,"command_panel_top":route.command_panel.position.y,"image_sha256":FileAccess.get_sha256(path)}
 FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 route.queue_free()
 await create_timer(.3).timeout
 print("PAVILION_FRAMING_PROBE_PASS views=",variants.size())
 quit(0)
