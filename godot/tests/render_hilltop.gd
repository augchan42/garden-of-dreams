extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func capture(label:String) -> void:
 await create_timer(1.8).timeout
 await RenderingServer.frame_post_draw
 if root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")!=OK:
  push_error("Hilltop render failed")
  quit(1)
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(7,4.04,-31)
 route._arrive("tubi_tang",true)
 var prefix="mobile-hilltop" if mobile else "hilltop"
 await capture(prefix)
 route.execute_command("overlook")
 await capture(prefix+"-overlook")
 route._camera_to(Vector3(6.4,5.6,-30.1),Vector3(4.4,4.9,-31.05))
 await capture(prefix+"-table")
 route.execute_command("topics")
 var browser=route.get_node("TopicBrowser")
 var result=await browser.client.finished
 if not result.ok:
  push_error(result.error)
  quit(1)
  return
 for topic in browser.topics:
  assert(topic.category=="temporal")
 await capture(prefix+"-events")
 var bounds=browser.get_node("TopicPanel").get_global_rect()
 assert(bounds.end.x<=root.size.x and bounds.end.y<=root.size.y)
 print("HILLTOP_RENDER_PASS ",prefix," ",browser.topics.size()," live current events")
 quit(0)
