extends SceneTree
func _initialize() -> void:
 create_timer(40).timeout.connect(func():push_error("Prop view capture timed out");quit(1))
 call_deferred("run")
func run() -> void:
 var portrait="--portrait" in OS.get_cmdline_user_args()
 root.size=Vector2i(390,844) if portrait else Vector2i(1410,600)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var views=[
  ["rockery_gate",Vector3(0,.04,32.5)],
  ["qinfang_ting",Vector3(0,.04,1.8)],
  ["qiushuang_zhai",Vector3(22,.04,-13.5)],
  ["tubi_tang",Vector3(7,4.04,-31)],
  ["hengwu_yuan",Vector3(-18,.04,-14.7)],
  ["longcui_an",Vector3(-25,.04,10.6)],
  ["ouxiang_xie",Vector3(-23,.04,0)]]
 for view in views:
  route.player.position=view[1]
  route._arrive(view[0],true)
  if view[0]=="longcui_an":route.execute_command("incense")
  if view[0]=="hengwu_yuan":route.execute_command("read")
  if view[0]=="tubi_tang":route._camera_to(Vector3(6.4,5.6,-30.1),Vector3(4.4,4.9,-31.05))
  await create_timer(1.5).timeout
  await RenderingServer.frame_post_draw
  assert(root.get_texture().get_image().save_png("res://../docs/reference/props-placed-"+view[0]+("-portrait" if portrait else "")+".png")==OK)
 print("PROP_VIEWS_PASS: seven sites ","portrait" if portrait else "desktop")
 quit(0)
