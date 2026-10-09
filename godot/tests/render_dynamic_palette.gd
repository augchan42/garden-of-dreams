extends SceneTree
const SOURCE:="c9d4fb308730733af2175c424449f8a63b731674d2527df2168a260cc0f5013e"
var route
var output:=""
var rows:Array=[]
var fogs:Array[ShaderMaterial]=[]
var waters:Array[ShaderMaterial]=[]
func _initialize()->void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 if DisplayServer.get_name()!="headless":root.show()
 create_timer(120).timeout.connect(func():push_error("Dynamic palette capture deadline exceeded");quit(1))
 call_deferred("run")
func settle()->void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running(),"Incomplete camera pose")
 RenderingServer.force_draw();await RenderingServer.frame_post_draw
func capture(room:String,aspect:String)->void:
 for fog in fogs:assert(is_equal_approx(fog.get_shader_parameter("timeline_time"),10.0))
 for water in waters:assert(is_equal_approx(water.get_shader_parameter("timeline_time"),10.0))
 assert(is_equal_approx(route.get_node("PondReflection").material.get_shader_parameter("timeline_time"),10.0))
 var image:=root.get_texture().get_image();var path:=output+"/%s-%s.png"%[room,aspect];assert(image.save_png(path)==OK)
 var position:Vector3=route.camera.position
 rows.append({"room":room,"aspect":aspect,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"camera_position":[position.x,position.y,position.z],"camera_fov":route.camera.fov,"camera_transition_running":false,"actual_fog_timelines":fogs.map(func(fog):return fog.get_shader_parameter("timeline_time")),"water_timeline":10.0,"reflection_timeline":10.0,"panel_top":route.command_panel.get_global_rect().position.y,"text":route.output_label.text})
func run()->void:
 if DisplayServer.get_name()=="headless" or output=="":push_error("Native renderer and output required");quit(1);return
 assert(FileAccess.get_sha256("res://assets/garden-of-dreams.glb")==SOURCE)
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route);await settle()
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(i)
   if material is ShaderMaterial and material.shader.resource_path=="res://shaders/water.gdshader" and not waters.has(material):
    material.set_shader_parameter("timeline_time",10.0);waters.append(material)
   if material is ShaderMaterial and material.shader.resource_path=="res://shaders/floor_fog.gdshader" and not fogs.has(material):
    material.set_shader_parameter("timeline_time",10.0);fogs.append(material)
 assert(fogs.size()>0 and waters.size()>0 and route.site_bakes_enabled)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",10.0)
 var positions={"terminal_room":route.CELL_PATH[0],"rockery_gate":route.CELL_PATH[-1],"qinfang_ting":route.GATE_PATH[-1],"ouxiang_xie":route.WEST_PATH[-1],"ziling_zhou":route.ISLAND_PATH[-1],"hengwu_yuan":route.COURTYARD_PATH[-1],"daoxiang_cun":route.FARM_PATH[-1],"aojing_guan":route.REFLECTION_PATH[-1],"longcui_an":route.NUNNERY_PATH[-1],"xiaoxiang_guan":route.BAMBOO_PATH[-1],"yihong_yuan":route.RED_COURT_PATH[-1],"daguan_lou":route.NORTH_PATH[-1],"qiushuang_zhai":route.STUDY_PATH[-1],"tubi_tang":route.HILL_PATH[-1]}
 for room in route.ROOMS:
  route.player.position=positions[room]+Vector3(0,.03,0)
  for aspect in ["desktop","portrait"]:
   root.size=Vector2i(1410,600) if aspect=="desktop" else Vector2i(390,844);route._configure_ui_scale(false,160);await settle();route._arrive(room,true);await settle();capture(room,aspect)
 if rows.size()!=28:push_error("Missing room originals");quit(1);return
 var bindings:Array=[]
 for fog in fogs:bindings.append({"resource_path":fog.resource_path,"color":str(fog.get_shader_parameter("fog_color"))})
 var water_bindings:Array=[]
 for water in waters:water_bindings.append({"resource_path":water.resource_path,"color":str(water.get_shader_parameter("water_color")),"timeline_time":water.get_shader_parameter("timeline_time")})
 var files:Dictionary={}
 for path in ["res://garden_preview.tscn","res://materials/water.tres","res://shaders/pond_reflection.gdshader","res://runtime/entry_route.gd","res://tests/render_dynamic_palette.gd","res://lightmaps/full-index.json","res://lightmaps/backdrop-wash-index.json","res://lightmaps/terminal-spill-index.json"]:files[path]=FileAccess.get_sha256(path)
 var report=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 report.store_string(JSON.stringify({"status":"all_fourteen_room_arrivals_captured_visual_review_required","source_glb_sha256":SOURCE,"files":files,"actual_fog_bindings":bindings,"actual_water_bindings":water_bindings,"rows":rows,"scope":"Installed normal full-baked route: original current desktop/portrait arrival poses for fourteen rooms; actual attached water/fog/reflection clocks fixed10 and checked per capture. No source/camera/layout changes, full moving tour, final scene-art or physical-device acceptance claimed."}," ")+"\n");report.close()
 print("DYNAMIC_PALETTE_CAPTURE_RESULT ",rows.size()," originals");quit(0)
