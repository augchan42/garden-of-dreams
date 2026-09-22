extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func capture(route: Node, label: String) -> void:
 await create_timer(1.8).timeout
 await RenderingServer.frame_post_draw
 var image = root.get_texture().get_image()
 var suffix="-baked" if "--baked" in OS.get_cmdline_user_args() else ""
 var result = image.save_png("res://../docs/reference/route-"+label+suffix+".png")
 assert(result==OK)
 print("ROUTE_RENDER_SAVED ",label)

func run() -> void:
 if "--mobile" in OS.get_cmdline_user_args(): root.size = Vector2i(390,844)
 var route = load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 if "--baked" in OS.get_cmdline_user_args():
  var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/index.json"))
  if preload("res://runtime/baked_materials.gd").apply_to_scene(route,records)!=records.size():
   push_error("Incomplete route bake")
   quit(1)
   return
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
 quit()
