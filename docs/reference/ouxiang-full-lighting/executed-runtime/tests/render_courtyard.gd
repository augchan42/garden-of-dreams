extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func capture(label:String) -> void:
 await create_timer(1.8).timeout
 await RenderingServer.frame_post_draw
 if root.get_texture().get_image().save_png("res://../docs/reference/route-"+label+".png")!=OK:
  push_error("Courtyard render failed")
  quit(1)
func run() -> void:
 var mobile="--mobile" in OS.get_cmdline_user_args()
 if mobile:root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(-18,.04,-14.7)
 route._arrive("hengwu_yuan",true)
 var prefix="mobile-courtyard" if mobile else "courtyard"
 await capture(prefix)
 for command in ["read","rocks"]:
  route.execute_command(command)
  await capture(prefix+"-"+command)
 route.execute_command("topics")
 var browser=route.get_node("TopicBrowser")
 var result=await browser.client.finished
 if not result.ok:
  push_error(result.error)
  quit(1)
  return
 for topic in browser.topics:assert(topic.category=="timeless")
 await capture(prefix+"-topics")
 var bounds=browser.get_node("TopicPanel").get_global_rect()
 assert(bounds.end.x<=root.size.x and bounds.end.y<=root.size.y)
 print("COURTYARD_RENDER_PASS ",prefix," ",browser.topics.size()," live ongoing topics")
 quit(0)
