extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route._arrive("rockery_gate",true);route.player.position=Vector3(-1.273,.04,20.5)
 route._camera_to(Vector3(-1.273,1.6,21.6),Vector3(0,1.2,19),true)
 await create_timer(.5).timeout
 route._travel(route.GATE_PATH.slice(8),"qinfang_ting")
 for i in range(600):
  await physics_frame
  if route.gate_reveal_active:break
 if not route.gate_reveal_active:
  push_error("Walking route did not reach reveal");quit(1);return
 print("REVEAL_START_CAMERA ",route.camera.position)
 var previous=0.0
 for t in [.1,.4,.8,1.2,1.6,2.4,3.4,4.1]:
  await create_timer(t-previous).timeout;previous=t
  await RenderingServer.frame_post_draw
  var label=("mobile-" if mobile else "")+"gate-reveal-"+str(t)
  root.get_texture().get_image().save_png("res://../docs/reference/"+label+".png")
  print("GATE_REVEAL_RENDER_SAVED ",label)
 quit(0)
