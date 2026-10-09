extends SceneTree
var directory="res://../docs/reference"
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):directory=arg.trim_prefix("--output=")
 if DisplayServer.get_name()!="headless":root.show()
 create_timer(60).timeout.connect(func():push_error("Surface capture deadline exceeded");quit(1))
 call_deferred("run")
func run() -> void:
 if DisplayServer.get_name()=="headless":push_error("Surface motion capture requires native graphics");quit(1);return
 DirAccess.make_dir_recursive_absolute(directory)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=route.GATE_PATH[-1]+Vector3(0,.03,0)
 route._arrive("qinfang_ting",true)
 route.camera.fov=55
 route._camera_to(Vector3(12,3.1,7),Vector3(9,-.6,0),true)
 var waters:Array[ShaderMaterial]=[]
 var fogs:Array[ShaderMaterial]=[]
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   var active=node.get_active_material(i)
   if active is ShaderMaterial and active.shader.resource_path=="res://shaders/water.gdshader" and not waters.has(active):waters.append(active)
   if active is ShaderMaterial and active.shader.resource_path=="res://shaders/floor_fog.gdshader" and not fogs.has(active):fogs.append(active)
 assert(not fogs.is_empty() and not waters.is_empty(),"No attached animated material checked")
 for water in waters:water.set_shader_parameter("timeline_time",0.0)
 for fog in fogs:fog.set_shader_parameter("timeline_time",0.0)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",0.0)
 var rows:Array=[]
 for phase in [["baseline",0.0,0.0],["water",100.0,0.0],["fog",0.0,100.0]]:
  for water in waters:water.set_shader_parameter("phase_offset",phase[1])
  for fog in fogs:fog.set_shader_parameter("phase_offset",phase[2])
  await create_timer(1).timeout
  RenderingServer.force_draw()
  await RenderingServer.frame_post_draw
  var image=root.get_texture().get_image()
  var path=directory+"/surfaces-%s.png" % phase[0]
  var result=image.save_png(path)
  if result != OK:
   push_error("Surface render failed")
   quit(1)
   return
  rows.append({"phase":phase[0],"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"water_phase":phase[1],"fog_phase":phase[2]})
 for water in waters:
  water.set_shader_parameter("phase_offset",0.0)
  water.set_shader_parameter("timeline_time",-1.0)
 var bindings:Array=[]
 for fog in fogs:
  fog.set_shader_parameter("phase_offset",0.0)
  fog.set_shader_parameter("timeline_time",-1.0)
  bindings.append({"resource_path":fog.resource_path,"resource_name":fog.resource_name,"color":str(fog.get_shader_parameter("fog_color"))})
 var report=FileAccess.open(directory+"/report.json",FileAccess.WRITE)
 report.store_string(JSON.stringify({"status":"surface_captures_saved_pixel_check_required","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"script_sha256":FileAccess.get_sha256("res://tests/render_surfaces.gd"),"actual_fog_bindings":bindings,"rows":rows,"scope":"Normal full-baked route at a fixed test camera, separately shifted water and attached live-fog clocks. Requires actual pixel differences; not phone or final art acceptance."}," ")+"\n");report.close()
 print("SURFACE_RENDERS_SAVED")
 quit(0)
