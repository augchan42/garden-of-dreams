extends SceneTree
var output:=""
var variant:=""
var expected:=""
var route
var forced_lod:=false
var rows:Array=[]
func _initialize()->void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg.begins_with("--variant="):variant=arg.trim_prefix("--variant=")
  if arg.begins_with("--source="):expected=arg.trim_prefix("--source=")
  if arg=="--force-lod":forced_lod=true
 if DisplayServer.get_name()!="headless":root.show()
 create_timer(100).timeout.connect(func():push_error("Stream geometry comparison deadline");quit(1))
 call_deferred("run")
func settle()->void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
 RenderingServer.force_draw();await RenderingServer.frame_post_draw
func run()->void:
 assert(DisplayServer.get_name()!="headless" and output!="" and variant!="")
 assert(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==expected)
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();route.site_bakes_enabled=false;root.add_child(route);await settle()
 if forced_lod:
  route.get_node("FloraLOD").set_process(false)
  for plant in route.get_node("FloraLOD").plants:
   if str(plant.node.name).begins_with("HERO_flora_ziling"):plant.node.mesh=plant.lower
 var waters:Array=[];var fogs:Array=[]
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   var active=node.get_active_material(i)
   if active is ShaderMaterial and active.shader.resource_path=="res://shaders/water.gdshader" and not waters.has(active):waters.append(active);active.set_shader_parameter("timeline_time",10.0)
   if active is ShaderMaterial and active.shader.resource_path=="res://shaders/floor_fog.gdshader" and not fogs.has(active):fogs.append(active);active.set_shader_parameter("timeline_time",10.0)
 assert(waters.size()>0 and fogs.size()>0)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",10.0)
 for room in ["qinfang_ting","ouxiang_xie","ziling_zhou"]:
  var positions={"qinfang_ting":route.GATE_PATH[-1],"ouxiang_xie":route.WEST_PATH[-1],"ziling_zhou":route.ISLAND_PATH[-1]}
  route.player.position=positions[room]+Vector3(0,.03,0)
  for size in [Vector2i(1410,600),Vector2i(390,844),Vector2i(360,800)]:
   root.size=size;route._configure_ui_scale(false,160);await settle();route._arrive(room,true);await settle()
   assert(not route.site_bakes_enabled)
   var image:=root.get_texture().get_image();var path:=output+"/%s-%dx%d.png"%[room,image.get_width(),image.get_height()];assert(image.save_png(path)==OK)
   rows.append({"room":room,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"camera_fov":route.camera.fov,"site_bakes_enabled":route.site_bakes_enabled,"camera_transition_running":false})
 assert(rows.size()==9)
 var stream=route.find_child("SITE_qinfang-ting_MAT_water",true,false) as MeshInstance3D
 var low:=INF;var high:=-INF
 for surface in range(stream.mesh.get_surface_count()):
  for p in stream.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
   var world:Vector3=stream.global_transform*p;low=minf(low,world.y);high=maxf(high,world.y)
 var file=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"unbaked_waterline_geometry_captured_visual_review_pending","variant":variant,"source_glb_sha256":expected,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256("res://tests/render_reed_candidate.gd"),"forced_reed_lod1":forced_lod,"actual_stream_bounds_y_up":[low,high],"actual_stream_color":str(waters[0].get_shader_parameter("water_color")),"actual_live_fog_material":fogs[0].resource_path,"rows":rows,"scope":"Isolated baseline and candidate BOTH use original current engine palette/runtime and no ordinary/wash/spill bakes; attached water/fog/pond clocks fixed10. Actual imported water bounds recorded. Completed current arrival cameras. Full or explicitly forced reed LOD1 geometry comparison only, not fresh lighting, final art, route physics, phone or production adoption."}," ")+"\n");file.close()
 print("REED_NATIVE_RESULT ",variant," ",rows.size()," originals");quit(0)
