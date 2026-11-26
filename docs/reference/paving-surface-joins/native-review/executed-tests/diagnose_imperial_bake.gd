extends SceneTree
func _initialize():call_deferred("run")
func run():
 root.size=Vector2i(1410,600)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(0,.04,-20.5)
 route._arrive("daguan_lou",true)
 route.get_node("PracticalLights").update_lights()
 var keys=route.find_children("*","Light3D",true,false).filter(func(l):return l is SpotLight3D or l is DirectionalLight3D)
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/priority2-index.json"))
 var directory="res://../docs/reference/lighting-diagnostics/"
 DirAccess.make_dir_recursive_absolute(directory)
 var report={"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"scope":"Temporary imperial receiver-mask and texture-resolution comparisons; no production changes or visual acceptance.","baked_shader_sha256":FileAccess.get_sha256("res://shaders/baked_diffuse.gdshader"),"variants":{},"native_maps":[]}
 for variant in ["static_keys_overlap","static_keys_isolated","static_keys_isolated_native"]:
  if variant=="static_keys_overlap":
   for light in keys:
    if (light.light_cull_mask&1)!=0:light.light_cull_mask|=2
  if variant=="static_keys_isolated":
   for light in keys:light.light_cull_mask&=~2
  if variant=="static_keys_isolated_native":
   for mesh in route.find_children("*","MeshInstance3D",true,false):
    if not records.has(str(mesh.name)):continue
    var record=records[str(mesh.name)]
    var image=Image.load_from_file(ProjectSettings.globalize_path("res://../export/lightmaps/"+record.texture))
    assert(not image.is_empty())
    var texture=ImageTexture.create_from_image(image)
    var prior=mesh.get_active_material(0).get_shader_parameter("lightmap") as Texture2D
    report.native_maps.append({"mesh":str(mesh.name),"compressed_size":[prior.get_width(),prior.get_height()],"native_size":[texture.get_width(),texture.get_height()]})
    for surface in range(mesh.mesh.get_surface_count()):mesh.get_active_material(surface).set_shader_parameter("lightmap",texture)
  await create_timer(1.8).timeout
  await RenderingServer.frame_post_draw
  var frame=root.get_texture().get_image()
  assert(frame.save_png(directory+"imperial-"+variant+".png")==OK)
  var regions={"roof":Rect2i(450,100,570,120),"doors":Rect2i(500,285,410,100)}
  var samples={}
  for label in regions:
   var region=regions[label]
   var total=Vector3.ZERO
   for y in range(region.position.y,region.end.y):
    for x in range(region.position.x,region.end.x):
     var pixel=frame.get_pixel(x,y)
     total+=Vector3(pixel.r,pixel.g,pixel.b)
   var mean=total/float(region.get_area())
   samples[label]={"mean_display_rgb":[mean.x,mean.y,mean.z],"sample_rect":[region.position.x,region.position.y,region.size.x,region.size.y]}
  report.variants[variant]=samples
 FileAccess.open("res://imperial-bake-diagnosis.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("IMPERIAL_BAKE_DIAGNOSIS_COMPLETE ",JSON.stringify(report.variants))
 quit()
