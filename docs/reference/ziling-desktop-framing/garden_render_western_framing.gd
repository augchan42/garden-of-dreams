extends SceneTree
var route
var output := ""
var rows: Array=[]
func _initialize() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 if DisplayServer.get_name()=="headless" or output=="":push_error("Native display and output required");quit(1);return
 root.show()
 create_timer(180).timeout.connect(func():push_error("Western framing deadline");quit(1))
 call_deferred("run")
func run() -> void:
 DirAccess.make_dir_recursive_absolute(output)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 await process_frame
 route.player.position=Vector3(0,.04,1.8);route._arrive("qinfang_ting",true)
 for step in [["west","ouxiang_xie"],["island","ziling_zhou"],["back","ouxiang_xie"],["back","qinfang_ting"]]:
  route.execute_command(step[0])
  for i in range(1800):
   await physics_frame
   if not route.travelling:break
  if route.travelling or route.room_id!=step[1] or route.player.position.y<-.3:
   push_error("Western collision travel rejected "+str(step));quit(1);return
  for i in range(16):await process_frame
  while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running():await process_frame
  var completed: Array[bool]=[false]
  RenderingServer.frame_post_draw.connect(func():completed[0]=true,CONNECT_ONE_SHOT)
  RenderingServer.force_draw()
  if not completed[0]:await RenderingServer.frame_post_draw
  var im=root.get_texture().get_image();var path=output+"/"+str(rows.size())+"-"+step[1]+".png"
  if im.save_png(path)!=OK:push_error("Cannot save western original");quit(1);return
  rows.append({"command":step[0],"room":route.room_id,"player_position":[route.player.position.x,route.player.position.y,route.player.position.z],"capture":path,"sha256":FileAccess.get_sha256(path),"camera_transition_running":false,"pixels":[im.get_width(),im.get_height()]})
 var f=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"status":"western_rendered_roundtrip_passed","rows":rows,"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"script_sha256":FileAccess.get_sha256(get_script().resource_path),"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"scope":"Actual typed public commands, four supported arrivals and settled native camera originals. Native screenshots require direct review. This is not a full moving tour or device performance acceptance."}," ")+"\n");f.close()
 print("WESTERN_RENDERED_ROUNDTRIP_PASS: 4 arrivals")
 quit(0)
