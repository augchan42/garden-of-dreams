extends SceneTree

var output_directory = "res://../docs/reference"
var captures: Dictionary = {}

func save_capture_report() -> void:
 var shape = "portrait" if "--mobile" in OS.get_cmdline_user_args() else "desktop"
 var file = FileAccess.open(output_directory + "/route-" + shape + "-report.json",FileAccess.WRITE)
 assert(file != null)
 file.store_string(JSON.stringify({"source_glb_sha256": FileAccess.get_sha256("res://assets/garden-of-dreams.glb"), "scope": "Actual native arrival captures, not continuous traversal, frame timing or phone acceptance.", "fixed_clock": 3.0 if "--fixed-clock" in OS.get_cmdline_user_args() else -1.0, "captures": captures},"  "))
 file.close()

func _initialize() -> void:
 call_deferred("run")

func capture(route: Node, label: String) -> void:
 await create_timer(1.8).timeout
 await process_frame
 RenderingServer.force_draw()
 var image = root.get_texture().get_image()
 var suffix="-full-baked" if "--full-baked" in OS.get_cmdline_user_args() else ("-baked" if "--baked" in OS.get_cmdline_user_args() else "")
 var path = output_directory + "/route-" + label + suffix + ".png"
 var result = image.save_png(path)
 assert(result==OK)
 captures[label] = {"sha256": FileAccess.get_sha256(path), "room_id": route.room_id, "image_size": [image.get_width(),image.get_height()]}
 print("ROUTE_RENDER_SAVED ",label)

func run() -> void:
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--output-directory="):
   output_directory = argument.trim_prefix("--output-directory=")
 assert(DirAccess.make_dir_recursive_absolute(output_directory) == OK)
 if "--mobile" in OS.get_cmdline_user_args(): root.size = Vector2i(390,844)
 var route = load("res://runtime/entry_route.tscn").instantiate()
 var baked="--baked" in OS.get_cmdline_user_args() or "--full-baked" in OS.get_cmdline_user_args()
 if baked:route.site_bakes_enabled=false
 root.add_child(route)
 if "--fixed-clock" in OS.get_cmdline_user_args():
  for node in route.find_children("*","MeshInstance3D",true,false):
   for surface in range(node.mesh.get_surface_count()):
    var material = node.get_active_material(surface)
    if material is ShaderMaterial:
     for uniform in material.shader.get_shader_uniform_list():
      if uniform.name == "timeline_time":material.set_shader_parameter("timeline_time",3.0)
 if baked:
  var catalog="full-index.json"
  var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/"+catalog))
  if preload("res://runtime/baked_materials.gd").apply_to_scene(route,records)!=records.size():
   push_error("Incomplete route bake")
   quit(1)
   return
  assert(preload("res://runtime/backdrop_wash.gd").apply_baked(route.get_node("GardenOfDreams"))==preload("res://runtime/backdrop_wash.gd").receiver_names(route.get_node("GardenOfDreams")).size())
  assert(preload("res://runtime/terminal_spill.gd").apply_baked(route.get_node("GardenOfDreams"))==7)
  var nodes:Array[Node]=[route]
  while not nodes.is_empty():
   var node=nodes.pop_back()
   nodes.append_array(node.get_children())
   if node is Light3D:node.shadow_enabled=false
 if "--views-only" in OS.get_cmdline_user_args():
  for pair in [["terminal_room","cell"],["rockery_gate","gate"],["qinfang_ting","pavilion"],["ouxiang_xie","ouxiang"],["ziling_zhou","ziling"],["qiushuang_zhai","study"],["tubi_tang","hilltop"],["hengwu_yuan","courtyard"],["daguan_lou","imperial"],["yihong_yuan","red-court"],["xiaoxiang_guan","bamboo"],["longcui_an","nunnery"],["aojing_guan","reflection"],["daoxiang_cun","farmhouse"]]:
   route.player.position = {"terminal_room":Vector3(-1.3,0,37.4),"rockery_gate":Vector3(0,0,32.5),"qinfang_ting":Vector3(0,0,1.8),"ouxiang_xie":Vector3(-23,0,0),"ziling_zhou":Vector3(-35.4,0,0),"qiushuang_zhai":Vector3(22,0,-13.5),"tubi_tang":Vector3(7,4,-31),"hengwu_yuan":Vector3(-18,0,-14.7),"daoxiang_cun":Vector3(-32,0,-19.3),"aojing_guan":Vector3(26,-.65,13.1),"longcui_an":Vector3(-25,0,10.6),"xiaoxiang_guan":Vector3(-6.6,0,13),"yihong_yuan":Vector3(22.6,0,1),"daguan_lou":Vector3(0,0,-20.5)}[pair[0]]+Vector3(0,.04,0)
   route._arrive(pair[0],true)
   await capture(route,("mobile-" if "--mobile" in OS.get_cmdline_user_args() else "")+pair[1])
  save_capture_report()
  quit()
  return
 await capture(route,"mobile-cell" if "--mobile" in OS.get_cmdline_user_args() else "cell")
 route.execute_command("exit")
 await route.transition_finished
 await capture(route,"mobile-gate" if "--mobile" in OS.get_cmdline_user_args() else "gate")
 route.execute_command("enter")
 await route.transition_finished
 await capture(route,"mobile-pavilion" if "--mobile" in OS.get_cmdline_user_args() else "pavilion")
 route.execute_command("west")
 await route.transition_finished
 await capture(route,"mobile-ouxiang" if "--mobile" in OS.get_cmdline_user_args() else "ouxiang")
 route.execute_command("island")
 await route.transition_finished
 await capture(route,"mobile-ziling" if "--mobile" in OS.get_cmdline_user_args() else "ziling")
 save_capture_report()
 quit()
