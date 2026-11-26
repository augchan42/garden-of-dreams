extends SceneTree

var mesh:MeshInstance3D
var directory=""
func _initialize() -> void:call_deferred("run")
func render(material:Material) -> Image:
 mesh.material_override=material
 for i in range(4):await process_frame
 RenderingServer.force_draw()
 return root.get_texture().get_image()
func difference(a:Image,b:Image) -> Dictionary:
 var squared=0.0
 var maximum=0.0
 for y in range(a.get_height()):
  for x in range(a.get_width()):
   var ca=a.get_pixel(x,y);var cb=b.get_pixel(x,y)
   for channel in range(3):
    var d=absf(ca[channel]-cb[channel]);squared+=d*d;maximum=maxf(maximum,d)
 return {"rmse":sqrt(squared/(a.get_width()*a.get_height()*3)),"maximum":maximum}
func run() -> void:
 var source_path=""
 var atlas_path="res://moon-atlas.json"
 var moon_pixels=223.0
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--moon-pixels="):moon_pixels=float(arg.trim_prefix("--moon-pixels="))
  if arg.begins_with("--source="):source_path=arg.trim_prefix("--source=")
  if arg.begins_with("--atlas="):atlas_path=arg.trim_prefix("--atlas=")
  if arg.begins_with("--output-directory="):directory=arg.trim_prefix("--output-directory=")
 if source_path.is_empty() or directory.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Moon transfer requires native graphics, source and output directory");quit(1);return
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 root.content_scale_size=Vector2i.ZERO;root.size=Vector2i(256,256)
 var imported=load(source_path).instantiate();root.add_child(imported)
 mesh=imported.find_child("SITE_stage_MAT_painted_moon",true,false) as MeshInstance3D
 assert(mesh!=null)
 var source=mesh.get_active_material(0) as StandardMaterial3D
 assert(source!=null and source.albedo_texture!=null and source.albedo_texture==source.emission_texture,"Moon must share one native texture resource")
 var expected=JSON.parse_string(FileAccess.get_file_as_string(atlas_path))
 var base=source.albedo_color.srgb_to_linear();var emission=source.emission.srgb_to_linear()
 assert(abs(base.r-expected.base_factor)<.00001 and abs(base.g-base.r)<.00001 and abs(base.b-base.r)<.00001,"Imported moon base factor differs")
 assert(abs(emission.r*source.emission_energy_multiplier-expected.emission_factor*.8)<.00001 and abs(emission.g-emission.r)<.00001 and abs(emission.b-emission.r)<.00001,"Imported moon emission factor differs")
 var world=Node3D.new();root.add_child(world);mesh.reparent(world,true);mesh.position=Vector3.ZERO;imported.free()
 var environment=WorldEnvironment.new();environment.environment=Environment.new();environment.environment.background_mode=Environment.BG_COLOR;environment.environment.background_color=Color(.03,.05,.065);environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_DISABLED;world.add_child(environment)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=5.4*256.0/moon_pixels;camera.position=Vector3(0,0,8);camera.current=true;world.add_child(camera)
 var light=DirectionalLight3D.new();light.light_energy=.6;world.add_child(light)
 var grade=load("res://runtime/color_grade.tscn").instantiate();root.add_child(grade)
 var report={"scope":"Actual imported moon native versus existing baked-material adapter with ordinary bake disabled, in emissive/key/graded views; positive missing-paint control. Not final baked garden lighting or site art acceptance.","source_glb_sha256":FileAccess.get_sha256(source_path),"adapter_sha256":FileAccess.get_sha256("res://runtime/baked_materials.gd"),"shader_sha256":FileAccess.get_sha256("res://shaders/baked_diffuse.gdshader"),"base_linear":[base.r,base.g,base.b],"emission_linear":[emission.r,emission.g,emission.b],"emission_energy":source.emission_energy_multiplier,"texture_size":[source.albedo_texture.get_width(),source.albedo_texture.get_height()],"moon_diameter_pixels":moon_pixels,"texture_readback_format":source.albedo_texture.get_image().get_format(),"texture_readback_bytes":source.albedo_texture.get_image().get_data_size(),"renderer_texture_memory_bytes":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED),"cases":{}}
 var passed=true
 for name in ["emission","key","graded"]:
  light.visible=name!="emission";grade.visible=name=="graded"
  var native=await render(source);var adapted=preload("res://runtime/baked_materials.gd").material_from_source(source);adapted.set_shader_parameter("use_lightmap",false)
  var frame=await render(adapted);var without=source.duplicate();without.albedo_texture=null;without.emission_texture=null
  var control=await render(without);var result=difference(native,frame);result.missing_paint_rmse=difference(native,control).rmse
  result.passed=result.rmse<=1.0/255 and result.maximum<=3.0/255 and result.missing_paint_rmse>.005;passed=passed and result.passed
  for pair in [["native",native],["adapted",frame],["missing-paint",control]]:
   var path=directory+"/"+name+"-"+pair[0]+".png";assert(pair[1].save_png(path)==OK);result[pair[0]+"_sha256"]=FileAccess.get_sha256(path)
  report.cases[name]=result
 report.status="passed" if passed else "failed"
 FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 grade.queue_free();world.queue_free();await create_timer(.3).timeout
 if not passed:push_error("Moon native/adapter transfer mismatch "+JSON.stringify(report))
 else:print("MOON_PAINT_TRANSFER_PASS cases=",report.cases.size())
 quit(0 if passed else 1)
