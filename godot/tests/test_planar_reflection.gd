extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1)
 route._arrive("aojing_guan",true)
 var mirror=route.get_node_or_null("PondReflection")
 if mirror==null:
  push_error("Pond reflection is missing")
  quit(1)
  return
 await process_frame
 mirror.update_reflection()
 assert(mirror.reflected_meshes>0)
 assert(mirror.pond_meshes==1)
 assert(abs(mirror.reflection_camera.global_position.y - (-2.2-route.camera.global_position.y)) < .001)
 assert(mirror.reflection_camera.cull_mask == mirror.REFLECTION_LAYER)
 assert(mirror.viewport.render_target_update_mode==SubViewport.UPDATE_ALWAYS)
 assert(mirror.material.get_shader_parameter("reflection_texture")!=null)
 route.player.position=Vector3(-23,0,0)
 mirror.update_reflection()
 assert(mirror.viewport.render_target_update_mode==SubViewport.UPDATE_DISABLED)
 print("PLANAR_REFLECTION_PASS: dedicated pond, mirrored camera, capture layer and distance gating")
 quit(0)
