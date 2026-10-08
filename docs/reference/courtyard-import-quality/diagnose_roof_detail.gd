extends SceneTree
var directory:String
var maps:String

func _initialize():call_deferred("run")

func freeze_clocks(route:Node):
 for node in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(surface)
   if material is ShaderMaterial:
    for uniform in material.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":material.set_shader_parameter("timeline_time",3.0)
 for node in route.find_children("*","Node",true,false):
  node.set_process(false)
  node.set_physics_process(false)
 route.set_process(false)
 route.set_physics_process(false)

func run():
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):directory=arg.trim_prefix("--output=")
  if arg.begins_with("--maps="):maps=arg.trim_prefix("--maps=")
 assert(not directory.is_empty() and not maps.is_empty() and DisplayServer.get_name()!="headless")
 assert(DirAccess.make_dir_recursive_absolute(directory)==OK)
 root.size=Vector2i(540,960);root.content_scale_size=Vector2i.ZERO
 var report={"status":"running","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"shader_sha256":FileAccess.get_sha256("res://shaders/baked_diffuse.gdshader"),"diagnostic_script_sha256":FileAccess.get_sha256("res://tests/diagnose_roof_detail.gd"),"viewport":[540,960],"scope":"Isolated current-source native material/filter counterfactuals at four arrival views; no production edits, traversal, final art or target-device performance claim. Source PNG readbacks used by lossless trials are Godot-decoded images; their format is recorded.","rooms":{}}
 var rooms={"qinfang_ting":["SITE_qinfang-ting_MAT_pavilion_atlas",Vector3(0,.04,1.8),true],"xiaoxiang_guan":["SITE_xiaoxiang-guan_MAT_rooftile",Vector3(-6.6,.04,13),false],"daoxiang_cun":["SITE_daoxiang-cun_MAT_thatch",Vector3(-32,.04,-19.3),false],"daguan_lou":["SITE_daguan-lou_MAT_rooftile",Vector3(0,.04,-20.5),false]}
 var component_shader=Shader.new()
 component_shader.code="""shader_type spatial;
render_mode unshaded,cull_disabled;
uniform sampler2D paint:source_color,filter_linear_mipmap;
uniform sampler2D irradiance:repeat_disable,filter_linear;
uniform vec4 base_color:source_color=vec4(1.0);
uniform float irradiance_scale=1.0;
uniform bool atlas_roof=false;
uniform int mode=0;
void fragment(){
 bool roof=!atlas_roof || (UV.x>0.515625 && UV.x<0.984375 && UV.y>0.015625 && UV.y<0.484375);
 vec3 color=vec3(0.02);
 if(roof){
  if(mode==0)color=base_color.rgb*texture(paint,UV).rgb;
  if(mode==1)color=texture(irradiance,UV2).rgb*irradiance_scale*3.14159265;
  if(mode==2)color=vec3(1.0);
 }
 ALBEDO=color;
}"""
 var black_shader=Shader.new();black_shader.code="shader_type spatial; render_mode unshaded,cull_disabled; void fragment(){ALBEDO=vec3(0.0);}";
 var black=ShaderMaterial.new();black.shader=black_shader
 for room in rooms:
  var spec=rooms[room]
  var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
  route.player.position=spec[1];route._arrive(room,true)
  await create_timer(1.6).timeout
  route.get_node("PracticalLights").update_lights()
  freeze_clocks(route)
  var mesh=route.find_child(spec[0],true,false) as MeshInstance3D;assert(mesh!=null)
  var original=mesh.get_active_material(0) as ShaderMaterial;assert(original!=null and original.get_shader_parameter("use_lightmap"))
  var lightmap=original.get_shader_parameter("lightmap") as Texture2D
  var source_path=maps+"/"+spec[0]+".png";assert(FileAccess.get_sha256(source_path)==FileAccess.get_sha256(lightmap.resource_path))
  var native=Image.load_from_file(source_path);assert(native!=null and not native.is_empty())
  var record={"mesh":spec[0],"lightmap_sha256":FileAccess.get_sha256(source_path),"production_lightmap_size":[lightmap.get_width(),lightmap.get_height()],"source_image_size":[native.get_width(),native.get_height()],"decoded_image_format":native.get_format(),"normal_enabled":original.get_shader_parameter("use_normal_texture"),"normal_scale":original.get_shader_parameter("normal_scale"),"orm_enabled":original.get_shader_parameter("use_orm_texture"),"base_color":str(original.get_shader_parameter("base_color")),"cases":{}}
  var component=ShaderMaterial.new();component.shader=component_shader
  component.set_shader_parameter("paint",original.get_shader_parameter("albedo_texture"));component.set_shader_parameter("irradiance",lightmap);component.set_shader_parameter("irradiance_scale",original.get_shader_parameter("lightmap_scale"));component.set_shader_parameter("base_color",original.get_shader_parameter("base_color"));component.set_shader_parameter("atlas_roof",spec[2])
  for label in ["baseline","no-normal","no-specular","paint-only","irradiance-only","lossless-256","lossless-512","lossless-native","baseline-again","roof-mask"]:
   var current=original.duplicate() as ShaderMaterial
   if label=="no-normal":current.set_shader_parameter("use_normal_texture",false)
   if label=="no-specular":current.set_shader_parameter("material_specular",0.0)
   if label in ["paint-only","irradiance-only"]:
    current=component.duplicate() as ShaderMaterial;current.set_shader_parameter("mode",0 if label=="paint-only" else 1)
   if label.begins_with("lossless-"):
    var image=native.duplicate() as Image
    var cap=256 if label=="lossless-256" else (512 if label=="lossless-512" else native.get_width())
    if cap<image.get_width():image.resize(cap,cap,Image.INTERPOLATE_LANCZOS)
    current.set_shader_parameter("lightmap",ImageTexture.create_from_image(image))
   if label=="roof-mask":
    for node in route.find_children("*","CanvasLayer",true,false):node.hide()
    current=component.duplicate() as ShaderMaterial;current.set_shader_parameter("mode",2)
   print("ROOF_CASE_BEGIN ",room," ",label)
   mesh.set_surface_override_material(0,current)
   for frame in range(5):await process_frame
   await RenderingServer.frame_post_draw
   var image=root.get_texture().get_image();var path=directory+"/"+room+"-"+label+".png";assert(image.save_png(path)==OK)
   record.cases[label]={"sha256":FileAccess.get_sha256(path),"file":room+"-"+label+".png"}
  report.rooms[room]=record
  route.queue_free();await process_frame
 report.status="captured"
 FileAccess.open(directory+"/report.json",FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 print("ROOF_DETAIL_DIAGNOSIS_PASS rooms=",report.rooms.size()," source=",report.source_glb_sha256)
 quit(0)
