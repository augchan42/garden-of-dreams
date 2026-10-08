extends SceneTree

func _initialize() -> void:call_deferred("run")

func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1)
 for size in [Vector2i(1410,600),Vector2i(390,844)]:
  root.size=size
  await process_frame
  await process_frame
  route._arrive("aojing_guan",true)
  var portrait=size.x<size.y
  var source=route.find_child("CAM_aojing-guan_portrait*" if portrait else "CAM_aojing-guan_wide*",true,false) as Camera3D
  assert(source!=null)
  assert(source.global_position.distance_to(route.camera.global_position)<.001)
  assert(source.global_basis.is_equal_approx(route.camera.global_basis))
  # Compare actual projection of the window and water, not just FOV metadata.
  for point in [Vector3(26,.9,12.325),Vector3(20.5,-1.1,14),Vector3(32,-1.1,21)]:
   assert(source.unproject_position(point).distance_to(route.camera.unproject_position(point))<.05,
    "Authored and runtime projections differ at "+str(size))
  var mirror=route.get_node("PondReflection")
  mirror.update_reflection()
  assert(is_equal_approx(mirror.reflection_camera.fov,route.camera.fov))
  assert(mirror.reflection_camera.keep_aspect==route.camera.keep_aspect)
 route._arrive("yihong_yuan",true)
 assert(is_equal_approx(route.camera.fov,55.0),"A later site must restore its normal FOV")
 print("REFLECTION_CAMERA_ALIGNMENT_PASS: authored position, orientation and window/pond projection in both aspects; mirrored projection; next-site FOV reset")
 quit()
