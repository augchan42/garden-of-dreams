extends SceneTree

func _initialize() -> void:call_deferred("run")

func flat_material(color:String) -> ShaderMaterial:
 var material=ShaderMaterial.new()
 var shader=Shader.new()
 shader.code="shader_type spatial; render_mode unshaded, fog_disabled; void fragment(){ALBEDO=vec3("+color+");}"
 material.shader=shader
 return material

func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(26,-.61,13.1)
 route._arrive("aojing_guan",true)
 route._begin_pond_view(true)
 var roof=route.find_child("SITE_aojing-guan_MAT_rooftile*",true,false) as MeshInstance3D
 assert(roof!=null)
 var report={"scope":"Flat-color visible-water raster coverage, including occlusion; all roof vertices inside the viewport. Not lighting or reference acceptance.","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"views":{}}
 # Black occluders keep depth testing. Alpha cards become solid for a
 # conservative lower bound; grade and UI are hidden only in this measurement.
 route.status.hide()
 route.pond_return_button.hide()
 route.find_child("ColorGrade",true,false).get_child(0).hide()
 var black=flat_material("0.0")
 var white=flat_material("1.0")
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   node.set_surface_override_material(i,white if "MAT_aojing_water" in str(node.name) else black)
 for size in [Vector2i(1410,600),Vector2i(390,844)]:
  root.size=size
  for i in range(3):await process_frame
  route._begin_pond_view(true)
  route.pond_return_button.hide()
  var minimum=Vector2(INF,INF)
  var maximum=Vector2(-INF,-INF)
  for surface in range(roof.mesh.get_surface_count()):
   for vertex in roof.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
    var point=route.camera.unproject_position(roof.global_transform*vertex)
    minimum=minimum.min(point)
    maximum=maximum.max(point)
  assert(minimum.x>=0 and minimum.y>=0 and maximum.x<size.x and maximum.y<size.y,
   "The roof must remain wholly visible at "+str(size))
  await create_timer(.2).timeout
  await RenderingServer.frame_post_draw
  var image=root.get_texture().get_image()
  var count=0
  var min_y=size.y
  var max_y=0
  for y in range(size.y):
   for x in range(size.x):
    var color=image.get_pixel(x,y)
    if minf(color.r,minf(color.g,color.b))>.99:
     count+=1
     min_y=mini(min_y,y)
     max_y=maxi(max_y,y)
  var fraction=float(count)/(size.x*size.y)
  assert(fraction>=.5,"Visible water must occupy at least half the frame")
  report.views["portrait" if size.x<size.y else "desktop"]={"viewport":[size.x,size.y],"water_pixels":count,"water_fraction":fraction,"water_rows":[min_y,max_y],"roof_bounds":[minimum.x,minimum.y,maximum.x,maximum.y]}
 FileAccess.open("res://pond-composition.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("POND_COMPOSITION_PASS ",report)
 quit()
