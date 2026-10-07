extends SceneTree
func _initialize():call_deferred("run")

func sample() -> Color:
 for frame in range(3):
  await process_frame
  RenderingServer.force_draw()
 return root.get_texture().get_image().get_pixel(128,128)

func run():
 root.size=Vector2i(256,256)
 root.content_scale_size=Vector2i.ZERO
 var world=Node3D.new()
 root.add_child(world)
 var env=WorldEnvironment.new()
 env.environment=Environment.new()
 env.environment.background_mode=Environment.BG_COLOR
 env.environment.background_color=Color.BLACK
 env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_DISABLED
 world.add_child(env)
 var mesh=MeshInstance3D.new()
 mesh.mesh=PlaneMesh.new()
 world.add_child(mesh)
 var black=Image.create(2,2,false,Image.FORMAT_RGB8)
 black.fill(Color.BLACK)
 var material=ShaderMaterial.new()
 material.shader=load("res://shaders/baked_diffuse.gdshader")
 if "--without-terminal-spill" in OS.get_cmdline_user_args():
  var disabled=material.shader.duplicate() as Shader
  var term=" if(use_terminal_spill)baked += texture(terminal_spill,UV2).rgb * terminal_spill_scale;"
  assert(disabled.code.contains(term))
  disabled.code=disabled.code.replace(term,"")
  material.shader=disabled
 material.set_shader_parameter("base_color",Color(.5,.5,.5))
 material.set_shader_parameter("use_lightmap",false)
 material.set_shader_parameter("use_backdrop_wash",true)
 material.set_shader_parameter("backdrop_wash_double_sided",true)
 material.set_shader_parameter("backdrop_wash",load("res://tests/fixtures/cycles-unit-sun.png"))
 material.set_shader_parameter("backdrop_wash_back",ImageTexture.create_from_image(black))
 mesh.material_override=material
 var camera=Camera3D.new()
 camera.projection=Camera3D.PROJECTION_ORTHOGONAL
 camera.size=2
 camera.current=true
 world.add_child(camera)
 camera.position=Vector3(0,3,0)
 camera.rotation.x=-PI/2
 var front=await sample()
 camera.position=Vector3(0,-3,0)
 camera.rotation.x=PI/2
 var back=await sample()
 if absf(front.r-.5)>.02 or back.r>.01:
  push_error("Native wash map selected the wrong face: front="+str(front)+" back="+str(back))
  quit(1)
  return
 # Independent bake terms must add once in linear space.
 camera.position=Vector3(0,3,0)
 camera.rotation.x=-PI/2
 material.set_shader_parameter("use_lightmap",true)
 material.set_shader_parameter("lightmap",load("res://tests/fixtures/cycles-unit-sun.png"))
 material.set_shader_parameter("lightmap_scale",.5)
 material.set_shader_parameter("backdrop_wash_scale",.5)
 var combined=await sample()
 if absf(combined.r-front.r)>.01:
  push_error("Ordinary and wash bakes do not add correctly: "+str(combined))
  quit(1)
  return
 # Terminal indirect light uses a separate term; its normalized texture
 # must be decoded at the original faint scale rather than gaining energy.
 material.set_shader_parameter("use_backdrop_wash",false)
 material.set_shader_parameter("use_terminal_spill",true)
 var normalized=Image.create(2,2,false,Image.FORMAT_RGBF)
 normalized.fill(Color.WHITE)
 material.set_shader_parameter("terminal_spill",ImageTexture.create_from_image(normalized))
 material.set_shader_parameter("terminal_spill_scale",.318303*.25)
 material.set_shader_parameter("lightmap_scale",.75)
 var indirect_combined=await sample()
 if absf(indirect_combined.r-front.r)>.01 or absf(indirect_combined.g-front.g)>.01 or absf(indirect_combined.b-front.b)>.01:
  push_error("Normalized terminal spill changed diffuse energy: "+str(indirect_combined))
  quit(1)
  return
 print("TERMINAL_SPILL_TRANSFER_PASS normalized-scale combined=",indirect_combined)
 # The production sky is an unshaded painted material. Its unlit base must
 # survive conversion even without material emission or a wash contribution.
 var unshaded=StandardMaterial3D.new()
 unshaded.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
 unshaded.albedo_color=Color(.3,.4,.5)
 mesh.material_override=unshaded
 var original=await sample()
 var converted=preload("res://runtime/baked_materials.gd").material_from_source(unshaded)
 converted.set_shader_parameter("use_lightmap",false)
 mesh.material_override=converted
 var preserved=await sample()
 if absf(original.r-preserved.r)>.01 or absf(original.g-preserved.g)>.01 or absf(original.b-preserved.b)>.01:
  push_error("Unshaded painted base was lost during conversion: "+str(original)+" versus "+str(preserved))
  quit(1)
  return
 print("BACKDROP_WASH_SIDES_PASS front=",front," back=",back," combined=",combined)
 print("UNSHADED_SKY_TRANSFER_PASS original=",original," converted=",preserved)
 world.free()
 quit()
