extends SceneTree
func _initialize():call_deferred("run")
func run():
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 assert(records.size()==124)
 for name in records:
  var mesh=route.find_child(name,true,false) as MeshInstance3D
  if mesh==null or not mesh.get_active_material(0) is ShaderMaterial or (mesh.layers&2)==0 or (mesh.layers&1)!=0:
   push_error("Normal exploration lacks a required baked receiver: "+name)
   quit(1)
   return
  var texture=mesh.get_active_material(0).get_shader_parameter("lightmap") as Texture2D
  if texture==null or texture.get_width()>256:
   push_error("Full bake texture missing or runtime size exceeds the configured budget: "+name)
   quit(1)
   return
 for light in route.find_children("*","Light3D",true,false):
  if light is SpotLight3D or light is DirectionalLight3D:
   var expected_mask=4 if str(light.name)=="BackdropWash" else 1
   if light.shadow_enabled or light.light_cull_mask!=expected_mask:
    push_error("Complete static bakes still use static receiver lighting or shadow maps")
    quit(1)
    return
 assert((route.find_child("SITE_stage_MAT_painted_moon",true,false).layers&6)==6)
 assert((route.find_child("SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas",true,false).layers&5)==5)
 assert(route.find_child("BackdropWash",true,false).light_cull_mask==4)
 print("FULL_SCENE_LIGHTING_PASS: 124 baked receivers, compressed maps, static shadow maps disabled, linked backdrop retained")
 quit()
