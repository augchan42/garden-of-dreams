extends SceneTree
var route
var output := ""
var candidate := false
var errors: Array[String]=[]
var rows: Array=[]
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg=="--candidate":candidate=true
 if DisplayServer.get_name()=="headless" or output=="":push_error("Native display/output required");quit(1);return
 root.show();create_timer(120).timeout.connect(func():push_error("WATER_EDGE_COMPARISON_DEADLINE");quit(1))
 call_deferred("run")
func check(ok: bool,message: String) -> void:
 if not ok:errors.append(message);push_error("WATER_EDGE_REJECTED "+message)
func settle() -> void:
 for i in range(16):await process_frame
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running():await process_frame
 var done: Array[bool]=[false]
 RenderingServer.frame_post_draw.connect(func():done[0]=true,CONNECT_ONE_SHOT)
 RenderingServer.force_draw()
 if not done[0]:await RenderingServer.frame_post_draw
 check(done[0],"Draw not completed")
func run() -> void:
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();route.site_bakes_enabled=false;route.demo_mode=false;root.add_child(route);await settle()
 check(not route.site_bakes_enabled and not route.demo_mode,"Comparison uses stale lighting")
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   var active=node.get_active_material(i)
   if active is ShaderMaterial and active.shader.resource_path in ["res://shaders/water.gdshader","res://shaders/floor_fog.gdshader"]:active.set_shader_parameter("timeline_time",10.0)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",10.0)
 for size in [Vector2i(1410,600),Vector2i(390,844)]:
  root.size=size;route._configure_ui_scale(false,160);await settle()
  for id in ["qinfang_ting","ouxiang_xie","ziling_zhou"]:
   var visitor=route.WEST_PATH[0] if id=="qinfang_ting" else (route.WEST_PATH[-1] if id=="ouxiang_xie" else route.ISLAND_PATH[-1])
   route.player.position=visitor+Vector3(0,.03,0);route._arrive(id,true);await settle()
   var im=root.get_texture().get_image();var name=id+"-"+str(im.get_width())+"x"+str(im.get_height())+".png";var path=output+"/"+name
   check(im.save_png(path)==OK,"Capture failed")
   rows.append({"room":id,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[im.get_width(),im.get_height()],"fov":route.camera.fov,"site_bakes_enabled":false,"camera_transition_running":false})
 var bank_bodies: Array=[]
 for body in route.find_children("*","StaticBody3D",true,false):
  if str(body.name).begins_with("COL_water_bank_"):bank_bodies.append(body)
 check(bank_bodies.size()==(54 if candidate else 0),"Native new bank body count "+str(bank_bodies.size()))
 var bank_hits: Array=[]
 if candidate:
  for body in bank_bodies:body.collision_layer=1024
  await physics_frame
  for side in [-1,1]:
   for i in range(27):
    var point=Vector3(-40+(i+.5)*80/27,1,side*5.34)
    var hit=route.player.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(point,point-Vector3(0,2,0),1024))
    check(not hit.is_empty() and absf(hit.position.y)<=.005,"Bank ray missed or raised above walk level")
    bank_hits.append({"x":point.x,"z":point.z,"hit_y":hit.position.y if not hit.is_empty() else null})
 var f=FileAccess.open(output+"/report.json",FileAccess.WRITE);f.store_string(JSON.stringify({"status":"unbaked_native_water_edge_comparison_passed" if errors.is_empty() else "rejected","candidate":candidate,"errors":errors,"rows":rows,"new_bank_bodies":bank_bodies.size(),"bank_top_ray_hits":bank_hits,"source_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"runtime_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256(get_script().resource_path),"scope":"Both fixtures use retained current game camera/runtime with all source lightmaps disabled and surface clocks10. Six native originals per fixture plus isolated bank-only collision rays. Direct review required. Not final fresh lighting, public moving-route, phone, material/site-art or adoption acceptance."}," ")+"\n");f.close()
 print("WATER_EDGE_COMPARISON_RESULT ",rows.size()," originals; ",errors.size()," failures")
 quit(0 if errors.is_empty() else 1)
