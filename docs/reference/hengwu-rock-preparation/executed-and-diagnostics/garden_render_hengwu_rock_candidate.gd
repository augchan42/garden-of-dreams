extends SceneTree
var variant := "baseline"
var output := ""
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--variant="):variant=arg.trim_prefix("--variant=")
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 call_deferred("run")
func settle(frames: int=12) -> void:
 for f in range(frames):await process_frame
 RenderingServer.force_draw();await RenderingServer.frame_post_draw
func run() -> void:
 DirAccess.make_dir_recursive_absolute(output)
 if DisplayServer.get_name()=="headless":quit(1);return
 var route=load("res://runtime/entry_route.tscn").instantiate()
 route.site_bakes_enabled=false
 root.add_child(route);await settle()
 route.player.position=Vector3(-18,.03,-11)
 var rows: Array=[]
 for size in [Vector2i(1410,600),Vector2i(390,844),Vector2i(360,800)]:
  root.size=size;route._configure_ui_scale(false,160);await settle();route._arrive("hengwu_yuan",true);await settle()
  for action in ["arrival","rocks","read"]:
   if action!="arrival":route.execute_command(action);await settle(110)
   var pixels:=root.get_texture().get_image();var path: String=output+"/"+variant+"-"+action+"-%dx%d.png"%[size.x,size.y]
   assert(pixels.save_png(path)==OK)
   rows.append({"variant":variant,"action":action,"capture":path,"sha256":FileAccess.get_sha256(path),"actual_pixels":[pixels.get_width(),pixels.get_height()],"logical_viewport":[root.size.x,root.size.y],"camera_position":[route.camera.position.x,route.camera.position.y,route.camera.position.z],"site_bakes_enabled":route.site_bakes_enabled})
 var file:=FileAccess.open(output+"/"+variant+"-report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"unbaked_geometry_comparison_recorded","variant":variant,"rows":rows,"script_sha256":FileAccess.get_sha256("/tmp/garden_render_hengwu_rock_candidate.gd"),"scope":"Both scenes rendered without any site bakes; unchanged normal grade and static/practical lighting. Candidate needs source-matched fresh lighting before visual acceptance/adoption. Direct arrival/action setup does not establish route physics."}," ")+"\n");file.close();print("HENGWU_ROCK_UNBAKED_COMPARISON ",variant," ",rows.size());quit(0)
