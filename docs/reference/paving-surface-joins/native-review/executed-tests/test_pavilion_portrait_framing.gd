extends SceneTree

func _initialize() -> void:call_deferred("run")
func fail(message:String) -> void:
 push_error(message)
 quit(1)

func run() -> void:
 if DisplayServer.get_name()=="headless":fail("Pavilion framing requires an actual native viewport");return
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.set_process(false)
 route.set_physics_process(false)
 for i in range(3):await process_frame
 route._arrive("qinfang_ting",true)
 await process_frame
 var moon=route.find_child("SITE_stage_MAT_painted_moon",true,false) as MeshInstance3D
 if moon==null:fail("Missing physical moon");return
 var clear_scene=Rect2(Vector2(12,70),Vector2(root.size.x-24,route.command_panel.position.y-82))
 for i in range(8):
  var point=moon.global_transform*moon.get_aabb().get_endpoint(i)
  if route.camera.is_position_behind(point) or not clear_scene.has_point(route.camera.unproject_position(point)):
   fail("Portrait pavilion clips the physical moon or places it under controls");return
 # Camera resize changes overview composition without resetting room text/actions.
 route.output_label.text="Preserved room content"
 root.size=Vector2i(1410,600)
 for i in range(4):await process_frame
 if route.camera.position.distance_to(Vector3(10,5.5,12))>.02 or abs(route.camera.fov-55)>.001 or route.output_label.text!="Preserved room content":
  fail("Landscape resize must restore its overview without resetting room content");return
 root.size=Vector2i(390,844)
 for i in range(4):await process_frame
 route.execute_command("table")
 await create_timer(1.6).timeout
 if abs(route.camera.fov-55)>.001 or route.camera.keep_aspect!=Camera3D.KEEP_WIDTH:
  fail("Portrait table detail must retain its original 55 degree horizontal view");return
 var detail=route.camera.transform
 root.size=Vector2i(400,850)
 for i in range(4):await process_frame
 if not route.camera.transform.is_equal_approx(detail):fail("Resize must not replace a table detail with the overview");return
 route._arrive("qinfang_ting",true)
 route._travel([Vector3(0,0,15),Vector3(0,0,12)],"qinfang_ting")
 route._begin_gate_reveal()
 var portrait_arrival=route._pavilion_camera_view()
 await create_timer(4.2).timeout
 if route.gate_reveal_active or route.camera.position.distance_to(portrait_arrival[0])>.02 or abs(route.camera.fov-portrait_arrival[2])>.001:
  fail("Portrait reveal must end at the same pose/projection as arrival");return
 route.queue_free()
 await create_timer(.3).timeout
 print("PAVILION_PORTRAIT_FRAMING_PASS: whole moon, resize, unchanged table detail and reveal endpoint")
 quit(0)
