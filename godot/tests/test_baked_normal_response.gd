extends SceneTree
func _initialize():call_deferred("run")
func run():
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(256,256)
 var scene=Node3D.new();root.add_child(scene)
 var environment=WorldEnvironment.new();environment.environment=Environment.new()
 environment.environment.background_mode=Environment.BG_COLOR
 environment.environment.background_color=Color.BLACK
 environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_DISABLED
 scene.add_child(environment)
 var source=StandardMaterial3D.new()
 source.albedo_color=Color(.5,.5,.5)
 source.roughness=1
 source.normal_enabled=true
 var image=Image.create(2,2,false,Image.FORMAT_RGB8)
 image.fill(Color(.9,.5,.8))
 source.normal_texture=ImageTexture.create_from_image(image)
 var mesh=MeshInstance3D.new();mesh.name="NormalProbe";mesh.mesh=PlaneMesh.new();mesh.mesh.material=source;scene.add_child(mesh)
 var camera=Camera3D.new();camera.position=Vector3(0,3,0);camera.rotation.x=-PI/2;camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=2;camera.current=true;scene.add_child(camera)
 var practical=OmniLight3D.new();practical.position=Vector3(2,1,0);practical.omni_range=4;practical.light_energy=2;scene.add_child(practical)
 var catalog=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/demo-index.json"))
 assert(preload("res://runtime/baked_materials.gd").apply_to_scene(scene,{"NormalProbe":catalog.values()[0]})==1)
 var material=mesh.get_active_material(0)
 material.set_shader_parameter("lightmap_scale",0)
 var values={}
 for mode in ["mapped","flat","zero_depth"]:
  material.set_shader_parameter("use_normal_texture",mode!="flat")
  material.set_shader_parameter("normal_scale",0.0 if mode=="zero_depth" else 1.0)
  for i in range(5):await process_frame
  await RenderingServer.frame_post_draw
  var frame=root.get_texture().get_image()
  values[mode]=frame.get_pixel(frame.get_width()/2,frame.get_height()/2).r
 if absf(values.mapped-values.flat)<.03 or absf(values.zero_depth-values.flat)>.01:
  push_error("Baked normal texture/depth did not affect actual practical-light shading: "+JSON.stringify(values))
  quit(1)
  return
 print("BAKED_NORMAL_RESPONSE_PASS ",JSON.stringify(values))
 quit()
