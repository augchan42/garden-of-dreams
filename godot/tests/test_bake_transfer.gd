extends SceneTree
func _initialize():call_deferred("run")
func run():
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(256,256)
 var world=Node3D.new();root.add_child(world)
 var env=WorldEnvironment.new();env.environment=Environment.new();env.environment.background_mode=Environment.BG_COLOR;env.environment.background_color=Color.BLACK;env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_DISABLED;world.add_child(env)
 var mesh=MeshInstance3D.new();mesh.mesh=PlaneMesh.new();world.add_child(mesh)
 var camera=Camera3D.new();camera.position=Vector3(0,3,0);camera.rotation.x=-PI/2;camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=2;camera.current=true;world.add_child(camera)
 var light=DirectionalLight3D.new();light.rotation.x=-PI/2;light.light_energy=1;light.light_color=Color.WHITE;world.add_child(light)
 var standard=StandardMaterial3D.new();standard.albedo_color=Color(.5,.5,.5);standard.roughness=1;standard.specular_mode=BaseMaterial3D.SPECULAR_DISABLED
 var texture=load('res://tests/fixtures/cycles-unit-sun.png') as Texture2D
 assert(texture!=null)
 var report={}
 for mode in ["dynamic","baked"]:
  if mode=="dynamic":mesh.material_override=standard
  else:
   var m=ShaderMaterial.new();m.shader=load("res://shaders/baked_diffuse.gdshader");m.set_shader_parameter("base_color",Color(.5,.5,.5));m.set_shader_parameter("lightmap",texture);m.set_shader_parameter("lightmap_scale",1.0);m.set_shader_parameter("material_roughness",1.0);mesh.material_override=m;light.visible=false
  for i in range(5):await process_frame
  await RenderingServer.frame_post_draw
  var frame=root.get_texture().get_image();var display=frame.get_pixel(frame.get_width()/2,frame.get_height()/2)
  print("ENGINE_TRANSFER_FIXTURE ",mode," display ",display," linear ",display.srgb_to_linear())
  report[mode]={"display_rgb":[display.r,display.g,display.b],"linear_rgb":[display.srgb_to_linear().r,display.srgb_to_linear().g,display.srgb_to_linear().b]}
 var matches=true
 for channel in range(3):
  matches=matches and report.dynamic.display_rgb[channel]>.45 and report.dynamic.display_rgb[channel]<.55 and absf(report.dynamic.display_rgb[channel]-report.baked.display_rgb[channel])<=.01
 if not matches:
  push_error("Baked diffuse does not match Compatibility unit-light response: "+JSON.stringify(report))
  quit(1)
  return
 print("BAKE_TRANSFER_PASS: unit-sun Cycles diffuse matches Compatibility dynamic lighting within 0.01 display RGB")
 quit()
