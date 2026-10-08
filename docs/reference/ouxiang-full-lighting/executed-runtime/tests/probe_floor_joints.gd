extends SceneTree

func _initialize() -> void:call_deferred("run")

func run() -> void:
 var directory=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-directory="):directory=arg.trim_prefix("--output-directory=")
 assert(not directory.is_empty() and DisplayServer.get_name()!="headless")
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(960,640)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 route.site_bakes_enabled=false
 root.add_child(route)
 route.set_process(false)
 route.set_physics_process(false)
 var inspection_light=OmniLight3D.new()
 inspection_light.light_energy=2.0
 inspection_light.omni_range=4.0
 route.add_child(inspection_light)
 var seams=JSON.parse_string(FileAccess.get_file_as_string("res://tests/floor-seam-candidate.json")).seams
 var views={}
 for seam in seams:
  var point=Vector3(seam.position_godot[0],0,seam.position_godot[2])
  var room="terminal_room" if seam.group=="cell" else "qinfang_ting"
  route.player.position=point+Vector3(0,.04,.4)
  route._arrive(room,true)
  route.camera.keep_aspect=Camera3D.KEEP_HEIGHT
  route.camera.fov=48
  var camera_position=point+Vector3(.1,1.4,.15)
  route._camera_to(camera_position,point,true)
  inspection_light.position=point+Vector3(0,1.5,.3)
  for variant in ["route-light","inspection-light"]:
   inspection_light.visible=variant=="inspection-light"
   await create_timer(.3).timeout
   await RenderingServer.frame_post_draw
   var name=seam.name+"-"+variant
   var path=directory+"/"+name+".png"
   assert(root.get_texture().get_image().save_png(path)==OK)
   var query=PhysicsRayQueryParameters3D.create(camera_position,point-Vector3(0,.01,0),1,[route.player.get_rid()])
   var hit=route.get_world_3d().direct_space_state.intersect_ray(query)
   views[name]={"point":[point.x,point.y,point.z],"camera_position":[camera_position.x,camera_position.y,camera_position.z],"diagnostic_light":inspection_light.visible,"image_sha256":FileAccess.get_sha256(path),"centre_collision":str(hit.collider.name) if not hit.is_empty() else "none"}
 var report={"scope":"Actual separately authored floor export, eight close inspection cameras with native route light and an explicit additional white inspection lamp, old bakes disabled. No collision inserts or geometry overlays. Ray excludes invisible visitor capsule. Not adopted, fresh lighting, production camera or new continuous-walk acceptance.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"probe_sha256":FileAccess.get_sha256("res://tests/probe_floor_joints.gd"),"views":views}
 FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 route.queue_free()
 await create_timer(.3).timeout
 print("FLOOR_JOINT_CAPTURE_PASS ",views.size())
 quit(0)
