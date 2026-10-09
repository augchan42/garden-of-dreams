extends SceneTree
var directory=""
var captures:Array=[]
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):directory=arg.trim_prefix("--output=")
 if DisplayServer.get_name()!="headless":root.show()
 create_timer(90).timeout.connect(func():push_error("Reflection capture deadline exceeded");quit(1))
 call_deferred("run")
func capture(label:String) -> void:
 for i in range(6):await process_frame
 await RenderingServer.frame_post_draw
 var path=(directory+"/pond-check-" if directory!="" else "res://../docs/reference/pond-check-")+label+".png"
 var image=root.get_texture().get_image()
 assert(image.save_png(path)==OK)
 captures.append({"phase":label,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()]})
func run() -> void:
 if DisplayServer.get_name()=="headless":push_error("Reflection validation requires native graphics");quit(1);return
 if directory!="":DirAccess.make_dir_recursive_absolute(directory)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1)
 route._arrive("aojing_guan",true)
 route.execute_command("reflection")
 await create_timer(1.6).timeout
 if route.camera_tween and route.camera_tween.is_running():await route.camera_tween.finished
 var mirror=route.get_node("PondReflection")
 mirror.material.set_shader_parameter("timeline_time",0.0)
 var fogs:Array[ShaderMaterial]=[]
 for mesh in route.find_children("*","MeshInstance3D",true,false):
  for i in range(mesh.mesh.get_surface_count()):
   var active=mesh.get_active_material(i)
   if active is ShaderMaterial and active.shader.resource_path=="res://shaders/water.gdshader":active.set_shader_parameter("timeline_time",0.0)
   if active is ShaderMaterial and active.shader.resource_path=="res://shaders/floor_fog.gdshader" and not fogs.has(active):
    active.set_shader_parameter("timeline_time",0.0);fogs.append(active)
 assert(fogs.size()>0,"No attached fog frozen")
 await capture("baseline")
 # Record the projected pond so comparisons remain valid when the shot changes.
 var polygon:Array = []
 var corners:Array[Vector3]=[Vector3(20.5,-1.1,14),Vector3(32,-1.1,14),Vector3(32,-1.1,21),Vector3(20.5,-1.1,21)]
 var clipped:Array[Vector3]=[]
 var view=route.camera.get_camera_transform().affine_inverse()
 var previous=corners[-1]
 var previous_z=(view*previous).z
 for corner in corners:
  var z=(view*corner).z
  if (z<=-route.camera.near)!=(previous_z<=-route.camera.near):
   clipped.append(previous.lerp(corner,(-route.camera.near-previous_z)/(z-previous_z)))
  if z<=-route.camera.near:clipped.append(corner)
  previous=corner
  previous_z=z
 for corner in clipped:
  var point:Vector2 = route.camera.unproject_position(corner)
  polygon.append([point.x,point.y])
 var metadata = FileAccess.open(directory+"/reflection-capture-region.json" if directory!="" else "res://../godot/reflection-capture-region.json",FileAccess.WRITE)
 var button_rect=route.pond_return_button.get_global_rect()
 metadata.store_string(JSON.stringify({"pond_polygon":polygon,"controls_visible":route.command_panel.visible,"controls_top":route.command_panel.global_position.y,"buttons_top":route.actions.global_position.y,"return_button_rect":[button_rect.position.x,button_rect.position.y,button_rect.size.x,button_rect.size.y],"viewport":[root.size.x,root.size.y]},"  "))
 metadata.close()
 mirror.material.set_shader_parameter("reflection_strength",0.0)
 await capture("disabled")
 mirror.material.set_shader_parameter("reflection_strength",.78)
 var nodes:Array[Node]=[route]
 var window:MeshInstance3D
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D and str(node.name).begins_with("SITE_aojing") and "crt_amber" in str(node.name):window=node
 assert(window!=null)
 window.layers &= ~mirror.REFLECTION_LAYER
 await capture("window-excluded")
 window.layers |= mirror.REFLECTION_LAYER
 mirror.material.set_shader_parameter("timeline_time",100.0)
 await capture("ripples")
 if directory!="":
  var report=FileAccess.open(directory+"/report.json",FileAccess.WRITE)
  report.store_string(JSON.stringify({"status":"reflection_captures_saved_pixel_check_required","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"script_sha256":FileAccess.get_sha256("res://tests/render_reflection_validation.gd"),"rows":captures,"frozen_actual_fog_materials":fogs.size(),"scope":"Actual reflection action, complete tween, baseline/strength-zero/window-excluded/reflection-ripple controls with water and attached fog clocks fixed. Requires pixel checks; not final art, phone or sustained acceptance."}," ")+"\n");report.close()
 print("REFLECTION_CAPTURE_VALIDATION: source window excluded only from capture, fixed-time strength and ripple comparisons")
 quit(0)
