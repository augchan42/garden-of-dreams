extends SceneTree
func _initialize():call_deferred("run")
func run():
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 assert(records.size()==124)
 var facade_maps=["SITE_xiaoxiang-guan_MAT_whitewash","SITE_xiaoxiang-guan_MAT_lattice_wood"]
 var reviewed_roofs={}
 if "--imperial-lossless512" in OS.get_cmdline_user_args():
  reviewed_roofs["SITE_daguan-lou_MAT_rooftile"]="001c6e9d40bd62cabdb887995a624e9ae5c7edcfddc0351f4016e59fc06f3989"
 if "--ouxiang-lossless512" in OS.get_cmdline_user_args():
  reviewed_roofs["SITE_ouxiang-xie_MAT_rooftile"]="e68faad7e479997944aef30ab9248732bc34ab3f10e65c7f569e9b59baea1dd5"
 for name in records:
  var mesh=route.find_child(name,true,false) as MeshInstance3D
  if mesh==null or not mesh.get_active_material(0) is ShaderMaterial or (mesh.layers&2)==0 or (mesh.layers&1)!=0:
   push_error("Normal exploration lacks a required baked receiver: "+name)
   quit(1)
   return
  var texture=mesh.get_active_material(0).get_shader_parameter("lightmap") as Texture2D
  var roof_exception=reviewed_roofs.has(name)
  var cap=512 if name in facade_maps or roof_exception else 256
  if texture==null or texture.get_width()>cap or texture.get_height()>cap:
   push_error("Full bake texture missing or runtime size exceeds the configured budget: "+name)
   quit(1)
   return
  if name in facade_maps:
   var settings=ConfigFile.new()
   assert(settings.load(texture.resource_path+".import")==OK)
   assert(settings.get_value("params","compress/mode")==0,"Courtyard compression would restore pink checks")
   assert(settings.get_value("params","process/size_limit")==512)
  if roof_exception:
   assert(records[name].uv_sha256==reviewed_roofs[name],"Roof exception requires the verified tile charts")
   var settings=ConfigFile.new()
   assert(settings.load(texture.resource_path+".import")==OK)
   assert(settings.get_value("params","compress/mode")==0)
   assert(settings.get_value("params","process/size_limit")==512)
   assert(settings.get_value("params","mipmaps/generate")==false)
   var image=texture.get_image()
   assert(image.get_size()==Vector2i(512,512) and image.get_format()==Image.FORMAT_RGB8)
   assert(image.get_data_size()==786432,"Roof decoded allocation differs from the inspected import")
 for light in route.find_children("*","Light3D",true,false):
  if light is SpotLight3D or light is DirectionalLight3D:
   var expected_mask=1
   if light.shadow_enabled or light.light_cull_mask!=expected_mask:
    push_error("Complete static bakes still use static receiver lighting or shadow maps")
    quit(1)
    return
 assert((route.find_child("SITE_stage_MAT_painted_moon",true,false).layers&6)==6)
 assert((route.find_child("SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas",true,false).layers&7)==6)
 assert(route.find_child("BackdropWash",true,false)==null)
 print("FULL_SCENE_LIGHTING_PASS: 124 baked receivers, per-map runtime caps, lossless courtyard maps, static shadow maps disabled, linked backdrop retained")
 quit()
