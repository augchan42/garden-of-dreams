extends SceneTree

func _initialize():call_deferred("run")

func run():
 var directory="/tmp/garden-backdrop-seam-20261010/views"
 assert(DisplayServer.get_name()!="headless")
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.set_process(false)
 route.set_physics_process(false)
 route.player.position=Vector3(0,.04,1.8)
 route._arrive("qinfang_ting",true)
 if route.camera_tween and route.camera_tween.is_valid() and route.camera_tween.is_running():await route.camera_tween.finished
 var cyclorama=route.find_child("SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas",true,false) as MeshInstance3D
 var moon=route.find_child("SITE_stage_MAT_painted_moon",true,false) as MeshInstance3D
 assert(cyclorama!=null and moon!=null)
 var original=cyclorama.get_active_material(0) as ShaderMaterial
 assert(original!=null)
 var environment=route.find_child("GardenEnvironment",true,false) as WorldEnvironment
 var fog_enabled=environment.environment.fog_enabled
 var record={"scope":"Isolated production clone; settled arrival, one backdrop variable per case. No production edits.","source_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"cases":{},"mesh_surfaces":cyclorama.mesh.get_surface_count(),"camera_position":str(route.camera.global_position),"parameters":{}}
 for name in ["base_color","material_emission","emission_energy","use_albedo_texture","use_emission_texture","use_lightmap","use_backdrop_wash"]:record.parameters[name]=str(original.get_shader_parameter(name))
 for object in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(object.mesh.get_surface_count()):
   var material=object.get_active_material(surface) as ShaderMaterial
   if material and material.shader.code.contains("timeline_time"):material.set_shader_parameter("timeline_time",0.0)
 for label in ["baseline","no-moon","cyclorama-no-ordinary","cyclorama-no-wash","cyclorama-no-paint","baseline-repeat"]:
  var current=original.duplicate() as ShaderMaterial
  moon.visible=label!="no-moon"
  # Fog held unchanged throughout this comparison.
  if label=="cyclorama-no-ordinary":current.set_shader_parameter("use_lightmap",false)
  if label=="cyclorama-no-wash":current.set_shader_parameter("use_backdrop_wash",false)
  if label=="cyclorama-no-paint":
   current.set_shader_parameter("use_albedo_texture",false)
   current.set_shader_parameter("use_emission_texture",false)
  cyclorama.set_surface_override_material(0,current)
  for i in range(8):await process_frame
  await RenderingServer.frame_post_draw
  var pixels=root.get_texture().get_image()
  var path=directory+"/"+label+".png"
  assert(pixels.save_png(path)==OK)
  record.cases[label]={"image_sha256":FileAccess.get_sha256(path),"dimensions":[pixels.get_width(),pixels.get_height()]}
 FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(record," ")+"\n")
 print("BACKDROP_SEAM_COUNTERFACTUALS_RECORDED ",record.cases.size())
 quit(0)
