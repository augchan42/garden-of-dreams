extends SceneTree

var destination=""
var mesh:MeshInstance3D

func _initialize() -> void:call_deferred("run")

func render(material:Material) -> Image:
 mesh.material_override=material
 for i in range(5):await process_frame
 await RenderingServer.frame_post_draw
 return root.get_texture().get_image()

func difference(a:Image,b:Image) -> Dictionary:
 var squared=0.0
 var maximum=0.0
 for y in range(a.get_height()):
  for x in range(a.get_width()):
   var ca=a.get_pixel(x,y)
   var cb=b.get_pixel(x,y)
   for channel in range(3):
    var delta=absf(ca[channel]-cb[channel])
    squared+=delta*delta
    maximum=maxf(maximum,delta)
 return {"rmse":sqrt(squared/(a.get_width()*a.get_height()*3)),"maximum":maximum}

func run() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output-dir="):destination=arg.trim_prefix("--output-dir=")
 if destination.is_empty() or DisplayServer.get_name()=="headless":
  push_error("PBR pixel proof requires a native display and --output-dir")
  quit(1)
  return
 DirAccess.make_dir_recursive_absolute(destination)
 root.content_scale_size=Vector2i.ZERO
 root.size=Vector2i(256,256)
 var world=Node3D.new()
 root.add_child(world)
 var env=WorldEnvironment.new()
 env.environment=Environment.new()
 env.environment.background_mode=Environment.BG_COLOR
 env.environment.background_color=Color(.015,.015,.015)
 env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_DISABLED
 world.add_child(env)
 mesh=MeshInstance3D.new()
 mesh.mesh=SphereMesh.new()
 world.add_child(mesh)
 var camera=Camera3D.new()
 camera.position=Vector3(0,0,3)
 camera.projection=Camera3D.PROJECTION_ORTHOGONAL
 camera.size=2.4
 camera.current=true
 world.add_child(camera)
 var light=DirectionalLight3D.new()
 light.rotation_degrees=Vector3(-25,-20,0)
 world.add_child(light)
 var image=Image.create(32,32,false,Image.FORMAT_RGBA8)
 for y in range(32):
  for x in range(32):
   image.set_pixel(x,y,Color(.15,.4,.85,.65) if (x/8+y/8)%2==0 else Color(.75,.8,.2,.3))
 image.generate_mipmaps()
 var texture=ImageTexture.create_from_image(image)
 var cases={}
 for channel in range(5):
  var rough=StandardMaterial3D.new()
  rough.roughness=.8
  rough.metallic=.25
  rough.metallic_specular=.35
  rough.roughness_texture=texture
  rough.roughness_texture_channel=channel
  cases["roughness-"+str(channel)]=rough
  var metal=StandardMaterial3D.new()
  metal.roughness=.35
  metal.metallic=.8
  metal.metallic_specular=.65
  metal.metallic_texture=texture
  metal.metallic_texture_channel=channel
  cases["metallic-"+str(channel)]=metal
 var packed=StandardMaterial3D.new()
 packed.roughness=.7
 packed.metallic=.6
 packed.roughness_texture=texture
 packed.roughness_texture_channel=BaseMaterial3D.TEXTURE_CHANNEL_GREEN
 packed.metallic_texture=texture
 packed.metallic_texture_channel=BaseMaterial3D.TEXTURE_CHANNEL_BLUE
 cases["packed-standard"]=packed
 var orm=ORMMaterial3D.new()
 orm.orm_texture=texture
 orm.roughness=.2
 orm.metallic=.3
 orm.metallic_specular=.12
 cases["orm-hidden-factors"]=orm
 var report={"scope":"Native Compatibility pixel comparison against actual Godot Standard/ORM materials under the same dynamic light; bake disabled, AO not doubled.","cases":{},"status":"running"}
 var matches=true
 for name in cases:
  var source=cases[name]
  source.albedo_color=Color(.4,.3,.2)
  source.disable_ambient_light=true
  var native=await render(source)
  native.save_png(destination+"/"+name+"-native.png")
  var adapted=preload("res://runtime/baked_materials.gd").material_from_source(source)
  adapted.set_shader_parameter("use_lightmap",false)
  var frame=await render(adapted)
  frame.save_png(destination+"/"+name+"-adapted.png")
  var result=difference(native,frame)
  # Negative control: removing texture bindings must visibly change the result.
  for flag in ["use_orm_texture","use_roughness_texture","use_metallic_texture"]:adapted.set_shader_parameter(flag,false)
  var without=await render(adapted)
  without.save_png(destination+"/"+name+"-missing-map.png")
  result["missing_map_rmse"]=difference(native,without).rmse
  result["native_sha256"]=FileAccess.get_sha256(destination+"/"+name+"-native.png")
  result["adapted_sha256"]=FileAccess.get_sha256(destination+"/"+name+"-adapted.png")
  result["missing_map_sha256"]=FileAccess.get_sha256(destination+"/"+name+"-missing-map.png")
  result["passed"]=result.rmse<=1.0/255.0 and result.maximum<=3.0/255.0 and result.missing_map_rmse>.005
  report.cases[name]=result
  matches=matches and result.passed
 report.status="passed" if matches else "failed"
 report["adapter_sha256"]=FileAccess.get_sha256("res://runtime/baked_materials.gd")
 report["shader_sha256"]=FileAccess.get_sha256("res://shaders/baked_diffuse.gdshader")
 report["fixture_sha256"]=FileAccess.get_sha256("res://tests/test_baked_pbr_render.gd")
 FileAccess.open(destination+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 world.queue_free()
 await create_timer(.2).timeout
 if not matches:push_error("Native PBR transfer mismatch: "+JSON.stringify(report))
 else:print("BAKED_PBR_RENDER_PASS cases=",cases.size())
 quit(0 if matches else 1)
