extends SceneTree
var route
var output:=""
var rows:Array=[]
var subjects:Dictionary={}
func _initialize()->void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 root.show();create_timer(120).timeout.connect(func():push_error("Desktop comparison deadline");quit(1));call_deferred("run")
func settle()->void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
 RenderingServer.force_draw();await RenderingServer.frame_post_draw
func vertices(node:MeshInstance3D,geometry:Mesh=null)->Array:
 assert(node!=null)
 if geometry==null:geometry=node.mesh
 var points:Array=[]
 for i in range(geometry.get_surface_count()):
  for p in geometry.surface_get_arrays(i)[Mesh.ARRAY_VERTEX]:points.append(node.global_transform*p)
 return points
func bounds(points:Array)->Dictionary:
 var lo:=Vector2(INF,INF);var hi:=Vector2(-INF,-INF);var behind:=0
 for p in points:
  if route.camera.is_position_behind(p):behind+=1
  var pixel:Vector2=route.camera.unproject_position(p);lo=lo.min(pixel);hi=hi.max(pixel)
 var size:Vector2=root.get_visible_rect().size;var header:Rect2=route.status.get_global_rect();var panel:Rect2=route.command_panel.get_global_rect()
 return {"low":[lo.x,lo.y],"high":[hi.x,hi.y],"width_fraction":(hi.x-lo.x)/size.x,"header_bottom":header.end.y,"panel_top":panel.position.y,"behind":behind,"fits":behind==0 and lo.x>=12 and hi.x<=size.x-12 and lo.y>=header.end.y+12 and hi.y<=panel.position.y-14}
func run()->void:
 assert(DisplayServer.get_name()!="headless" and output!="")
 assert(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")=="1380ceca14ee8bd79723c351a6084438eed4384416aee76a78222802550ca485")
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route);await settle();assert(route.site_bakes_enabled)
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(i)
   if material is ShaderMaterial and material.shader.resource_path in ["res://shaders/water.gdshader","res://shaders/floor_fog.gdshader"]:material.set_shader_parameter("timeline_time",10.0)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",10.0)
 for pair in [["island","SITE_ziling-zhou_MAT_plaster_rock"],["bridge","SITE_ziling-zhou_MAT_pavilion_atlas"],["pavilion_roof","SITE_ouxiang-xie_MAT_rooftile"]]:subjects[pair[0]]=vertices(route.find_child(pair[1],true,false))
 subjects.reeds=[]
 for plant in route.get_node("FloraLOD").plants:
  if str(plant.node.name).begins_with("HERO_flora_ziling"):
   subjects.reeds.append_array(vertices(plant.node,plant.base));subjects.reeds.append_array(vertices(plant.node,plant.lower))
 assert(subjects.island.size()==2112 and subjects.bridge.size()==1296 and subjects.pavilion_roof.size()==8116 and subjects.reeds.size()==48320)
 var cases=[["baseline",Vector3(-40,3,6),Vector3(-34,.6,0)],["nearer-left",Vector3(-41,2.6,9),Vector3(-33,-1,0)],["lower-back",Vector3(-40,2.6,10),Vector3(-33,-1,0)],["higher-back",Vector3(-40,3,10),Vector3(-33,-1,0)]]
 for c in cases:
  for size in [Vector2i(1410,600),Vector2i(1280,720)]:
   root.size=size;route._configure_ui_scale(false,160);await settle();route.player.position=route.ISLAND_PATH[-1]+Vector3(0,.03,0);route._arrive("ziling_zhou",true);await settle()
   route.camera.keep_aspect=Camera3D.KEEP_HEIGHT;route.camera.fov=55;route._camera_to(c[1],c[2],true);await settle()
   var m:Dictionary={};for name in subjects:m[name]=bounds(subjects[name])
   var image:=root.get_texture().get_image();var path:=output+"/%s-%dx%d.png"%[c[0],image.get_width(),image.get_height()];assert(image.save_png(path)==OK)
   rows.append({"case":c[0],"capture":path,"sha256":FileAccess.get_sha256(path),"actual_pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"fov":route.camera.fov,"site_bakes_enabled":route.site_bakes_enabled,"camera_transition_running":false,"measurements":m})
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE);assert(file!=null)
 file.store_string(JSON.stringify({"status":"desktop_comparisons_rendered_visual_review_pending","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("res://tests/render_ziling_desktop.gd"),"rows":rows,"scope":"Original current freshly lit scene and unchanged game runtime. Camera-only baseline/three proposals, actual native subject bounds, water/fog/reflection clocks fixed10. No implementation, public resize/action acceptance, final art or phone claim."}," ")+"\n");file.close();print("ZILING_DESKTOP_COMPARISON_RESULT ",rows.size()," originals");quit(0)
