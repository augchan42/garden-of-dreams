extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func capture(label:String) -> void:
 for i in range(6):await process_frame
 await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png("res://../docs/reference/pond-check-"+label+".png")==OK)
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1)
 route._arrive("aojing_guan",true)
 route.execute_command("reflection")
 await create_timer(1.6).timeout
 var mirror=route.get_node("PondReflection")
 mirror.material.set_shader_parameter("timeline_time",0.0)
 load("res://materials/water.tres").set_shader_parameter("timeline_time",0.0)
 load("res://materials/floor_fog.tres").set_shader_parameter("timeline_time",0.0)
 await capture("baseline")
 # Record the projected pond so comparisons remain valid when the shot changes.
 var polygon:Array = []
 for corner in [Vector3(20.5,-1.1,14),Vector3(32,-1.1,14),Vector3(32,-1.1,21),Vector3(20.5,-1.1,21)]:
  var point:Vector2 = route.camera.unproject_position(corner)
  polygon.append([point.x,point.y])
 var metadata = FileAccess.open("res://../godot/reflection-capture-region.json",FileAccess.WRITE)
 metadata.store_string(JSON.stringify({"pond_polygon":polygon,"controls_top":route.command_panel.global_position.y,"buttons_top":route.actions.global_position.y,"viewport":[root.size.x,root.size.y]},"  "))
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
 print("REFLECTION_CAPTURE_VALIDATION: source window excluded only from capture, fixed-time strength and ripple comparisons")
 quit(0)
