extends SceneTree

# Compare the real portrait view with the same native maps decoded at the
# same runtime resolution. A smooth painted flat must not gain visible blocks.
const REGION = Rect2i(0,205,100,35)
const MAX_RMSE = 2.0 / 255.0

func _initialize():call_deferred("run")

func capture() -> Image:
 await process_frame
 RenderingServer.force_draw()
 return root.get_texture().get_image()

func run():
 root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await process_frame
 route.player.position=Vector3(0,.04,1.8)
 route._arrive("qinfang_ting",true)
 await create_timer(1).timeout
 var base=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 var wash=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/backdrop-wash-index.json"))
 var targets:Array[Dictionary]=[]
 var formats={}
 for index in range(3):
  var name="SITE_stage_MAT_painted_mountains_"+str(index)
  var node=route.find_child(name,true,false) as MeshInstance3D
  assert(node!=null and node.mesh.get_surface_count()==1)
  var material=node.get_active_material(0) as ShaderMaterial
  assert(material!=null)
  var fields={"lightmap":base[name].texture,"backdrop_wash":wash[name].texture,
              "backdrop_wash_back":wash[name].sides.back.texture}
  var textures={}
  for field in fields:
   var texture=material.get_shader_parameter(field) as Texture2D
   assert(texture!=null and texture.get_size()==Vector2(256,256))
   textures[field]=texture
   formats[fields[field]]={"format":texture.get_image().get_format(),"compressed":texture.get_image().is_compressed()}
  targets.append({"material":material,"fields":fields,"textures":textures})
 var actual=await capture()
 for target in targets:
  for field in target.fields:
   var path=ProjectSettings.globalize_path("res://lightmaps/"+target.fields[field])
   var image=Image.load_from_file(path)
   assert(image!=null)
   image.resize(256,256,Image.INTERPOLATE_LANCZOS)
   image.convert(Image.FORMAT_RGB8)
   target.material.set_shader_parameter(field,ImageTexture.create_from_image(image))
 var reference=await capture()
 for target in targets:
  for field in target.textures:target.material.set_shader_parameter(field,target.textures[field])
 var squared_error=0.0
 for y in range(REGION.position.y,REGION.end.y):
  for x in range(REGION.position.x,REGION.end.x):
   var a=actual.get_pixel(x,y)
   var b=reference.get_pixel(x,y)
   squared_error+=(a.r-b.r)*(a.r-b.r)+(a.g-b.g)*(a.g-b.g)+(a.b-b.b)*(a.b-b.b)
 var rmse=sqrt(squared_error/(REGION.size.x*REGION.size.y*3))
 var report={"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),
             "scope":"Portrait Qinfang mountain region versus uncompressed native maps at the same 256px runtime resolution; no source or saved material changes.",
             "viewport":[390,844],"region":[0,205,100,35],"rmse":rmse,
             "max_rmse":MAX_RMSE,"formats":formats,"passed":rmse<=MAX_RMSE}
 var output=ProjectSettings.globalize_path("res://../export/mountain-lightmap-filtering.json")
 var file=FileAccess.open(output,FileAccess.WRITE)
 file.store_string(JSON.stringify(report,"  ")+"\n")
 file.close()
 assert(actual.save_png(ProjectSettings.globalize_path("res://../docs/reference/mountain-filter-actual.png"))==OK)
 assert(reference.save_png(ProjectSettings.globalize_path("res://../docs/reference/mountain-filter-reference.png"))==OK)
 route.queue_free()
 await process_frame
 if rmse>MAX_RMSE:
  push_error("Mountain compression adds visible blocks: RMSE="+str(rmse)+", limit="+str(MAX_RMSE))
  quit(1)
  return
 print("MOUNTAIN_LIGHTMAP_FILTERING_PASS rmse=",rmse," limit=",MAX_RMSE," formats=",formats)
 quit()
