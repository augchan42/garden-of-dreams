extends SceneTree

# Read-only projection diagnosis. Cylinder crossings flag potential backdrop
# exposure; foreground occlusion and final composition still need rendered checks.
func _initialize() -> void:call_deferred("run")

func crossing(camera:Camera3D,point:Vector2) -> float:
 var origin=camera.project_ray_origin(point)
 var direction=camera.project_ray_normal(point)
 var a=direction.x*direction.x+direction.z*direction.z
 var b=2*(origin.x*direction.x+origin.z*direction.z)
 var c=origin.x*origin.x+origin.z*origin.z-48*48
 var discriminant=b*b-4*a*c
 if a<=.000001 or discriminant<0:return NAN
 var distance=(-b+sqrt(discriminant))/(2*a)
 return origin.y+direction.y*distance

func run() -> void:
 var output=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 if output.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Framing diagnosis requires a native window and --output")
  quit(1)
  return
 root.content_scale_size=Vector2i.ZERO
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.set_process(false)
 route.set_physics_process(false)
 var moon=route.find_child("SITE_stage_MAT_painted_moon",true,false) as MeshInstance3D
 if moon==null:
  push_error("Painted moon missing")
  quit(1)
  return
 var positions={"terminal_room":Vector3(-1.3,0,37.4),"rockery_gate":Vector3(0,0,32.5),"qinfang_ting":Vector3(0,0,1.8),"ouxiang_xie":Vector3(-23,0,0),"ziling_zhou":Vector3(-35.4,0,0),"qiushuang_zhai":Vector3(22,0,-13.5),"tubi_tang":Vector3(7,4,-31),"hengwu_yuan":Vector3(-18,0,-14.7),"daoxiang_cun":Vector3(-32,0,-19.3),"aojing_guan":Vector3(26,-.65,13.1),"longcui_an":Vector3(-25,0,10.6),"xiaoxiang_guan":Vector3(-6.6,0,13),"yihong_yuan":Vector3(22.6,0,1),"daguan_lou":Vector3(0,0,-20.5)}
 var report={"scope":"Native current-runtime projection math at all fourteen arrival cameras in two shapes. Approximate 48m cylinder/top20m checks are potential exposure, not rendered visibility or final camera acceptance.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_script_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"views":{}}
 for shape in ["desktop","portrait"]:
  root.size=Vector2i(1410,600) if shape=="desktop" else Vector2i(390,844)
  for frame in range(3):await process_frame
  var size=Vector2(root.size)
  for room in positions:
   route.player.position=positions[room]+Vector3(0,.04,0)
   route._arrive(room,true)
   await process_frame
   var camera=route.camera
   var left=camera.project_ray_normal(Vector2(0,size.y/2))
   var right=camera.project_ray_normal(Vector2(size.x,size.y/2))
   var top=camera.project_ray_normal(Vector2(size.x/2,0))
   var bottom=camera.project_ray_normal(Vector2(size.x/2,size.y))
   var heights=[]
   var over=0
   for i in range(17):
    var height=crossing(camera,Vector2(size.x*i/16,0))
    heights.append(height)
    if is_finite(height) and height>20:over+=1
   var projected=[]
   var behind=0
   var inside=0
   var bounds=moon.get_aabb()
   for i in range(8):
    var point=moon.global_transform*bounds.get_endpoint(i)
    if camera.is_position_behind(point):behind+=1
    var screen=camera.unproject_position(point)
    projected.append([screen.x,screen.y])
    if not camera.is_position_behind(point) and Rect2(Vector2.ZERO,size).has_point(screen):inside+=1
   report.views[shape+"-"+room]={"window_size":[root.size.x,root.size.y],"keep_aspect":camera.keep_aspect,"configured_fov":camera.fov,"horizontal_fov_degrees":rad_to_deg(left.angle_to(right)),"vertical_fov_degrees":rad_to_deg(top.angle_to(bottom)),"camera_position":[camera.position.x,camera.position.y,camera.position.z],"top_edge_cylinder_y":heights,"top_samples_above_enclosure":over,"moon_bounds_screen":projected,"moon_bounds_corners_behind":behind,"moon_bounds_corners_inside":inside}
 FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 route.queue_free()
 await create_timer(.2).timeout
 print("STAGE_FRAMING_INSPECTION_PASS views=",report.views.size())
 quit(0)
