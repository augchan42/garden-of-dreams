extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route._arrive("rockery_gate",true)
 var views=[
  ["mouth",Vector3(0,1.65,32.3),Vector3(1.273,1.5,29.5)],
  ["bend-one",Vector3(1.8,1.65,28),Vector3(0,1.5,25)],
  ["bend-two",Vector3(-1.8,1.65,22),Vector3(0,1.5,19)],
  ["exit",Vector3(0,1.65,18.5),Vector3(0,1.8,0)]]
 for view in views:
  route.player.position=Vector3(view[1].x,.04,view[1].z)
  route._camera_to(view[1],view[2],true)
  await create_timer(1.5).timeout;await RenderingServer.frame_post_draw
  var label=("mobile-" if mobile else "")+"gate-kit-"+view[0]
  root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")
  print("GATE_KIT_RENDER_SAVED ",label)
 quit(0)
