extends SceneTree

func _initialize():call_deferred("run")

func run():
 var directory=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-directory="):directory=arg.trim_prefix("--output-directory=")
 if directory.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Moon contrast diagnosis requires native graphics and output directory")
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
 route._arrive("qinfang_ting",true)
 var moon=route.find_child("SITE_stage_MAT_painted_moon",true,false) as MeshInstance3D
 var material=moon.get_active_material(0) as ShaderMaterial
 assert(material!=null and material.get_shader_parameter("use_lightmap") and material.get_shader_parameter("use_backdrop_wash"))
 var original=material.duplicate() as ShaderMaterial
 var grade=route.find_child("ColorGrade",true,false)
 assert(grade!=null)
 var bounds=moon.mesh.get_aabb()
 var minimum=Vector2(INF,INF)
 var maximum=Vector2(-INF,-INF)
 for i in range(8):
  var point=route.camera.unproject_position(moon.global_transform*bounds.get_endpoint(i))
  minimum=minimum.min(point);maximum=maximum.max(point)
 var center=(minimum+maximum)*.5
 var radius=(maximum-minimum)*.5
 var report={"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"shader_sha256":FileAccess.get_sha256("res://shaders/baked_diffuse.gdshader"),"test_sha256":FileAccess.get_sha256("res://tests/diagnose_moon_scene_contrast.gd"),"scope":"Actual production-baked garden portrait arrival with isolated moon material counterfactuals. View/state placement only, no source edits or installed look changes. Interior projected-disc pixel statistics are display RGB, not linear radiometry or final art acceptance.","moon_bounds_pixels":[[minimum.x,minimum.y],[maximum.x,maximum.y]],"cases":{}}
 for label in ["baseline","no-emission","no-ordinary","no-wash","no-bakes","material-0.45","no-grade"]:
  var current=original.duplicate() as ShaderMaterial
  if label=="no-emission":current.set_shader_parameter("emission_energy",0.0)
  if label in ["no-ordinary","no-bakes"]:current.set_shader_parameter("use_lightmap",false)
  if label in ["no-wash","no-bakes"]:current.set_shader_parameter("use_backdrop_wash",false)
  if label=="material-0.45":
   var base=current.get_shader_parameter("base_color") as Color
   # Colors are source_color uniforms: scale physical values in linear space.
   var scaled=base.srgb_to_linear()*0.45
   scaled.a=base.a
   current.set_shader_parameter("base_color",scaled.linear_to_srgb())
   current.set_shader_parameter("emission_energy",original.get_shader_parameter("emission_energy")*0.45)
  moon.set_surface_override_material(0,current)
  grade.visible=label!="no-grade"
  for i in range(4):await process_frame
  await RenderingServer.frame_post_draw
  var image=root.get_texture().get_image()
  var path=directory+"/"+label+".png"
  assert(image.save_png(path)==OK)
  var samples=[]
  var clipped=0
  for y in range(maxi(0,int(minimum.y)),mini(image.get_height(),int(maximum.y)+1)):
   for x in range(maxi(0,int(minimum.x)),mini(image.get_width(),int(maximum.x)+1)):
    var normalized=(Vector2(x+.5,y+.5)-center)/radius
    if normalized.length_squared()>.64:continue
    var color=image.get_pixel(x,y)
    samples.append(color.r*.2126+color.g*.7152+color.b*.0722)
    if maxf(color.r,maxf(color.g,color.b))>=.99:clipped+=1
  assert(samples.size()>50)
  samples.sort()
  report.cases[label]={"image_sha256":FileAccess.get_sha256(path),"interior_samples":samples.size(),"display_luminance_min":samples[0],"display_luminance_max":samples[-1],"display_luminance_p05":samples[int(samples.size()*.05)],"display_luminance_p95":samples[int(samples.size()*.95)],"channel_clip_fraction":float(clipped)/samples.size()}
 moon.set_surface_override_material(0,original)
 grade.visible=true
 FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 route.queue_free()
 await create_timer(.3).timeout
 print("MOON_SCENE_CONTRAST_DIAGNOSIS_RECORDED ",report.cases.size()," cases")
 quit(0)
