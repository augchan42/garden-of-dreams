extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 if "--mobile" in OS.get_cmdline_user_args():root.size=Vector2i(390,844)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(0,.04,1.8)
 route._arrive("qinfang_ting",true)
 route.execute_command("topics")
 var browser=route.get_node("TopicBrowser")
 assert(not route.input.editable)
 var result=await browser.client.finished
 if not result.ok:
  push_error(result.error)
  quit(1)
  return
 if browser.topics.is_empty():
  push_error("No live topics available for the visual check")
  quit(1)
  return
 await create_timer(.3).timeout
 await RenderingServer.frame_post_draw
 var panel=browser.get_node("TopicPanel")
 var bounds=panel.get_global_rect()
 if bounds.end.x>root.size.x or bounds.end.y>root.size.y:
  push_error("Topic panel exceeds the viewport")
  quit(1)
  return
 var suffix="mobile" if "--mobile" in OS.get_cmdline_user_args() else "desktop"
 var saved=root.get_texture().get_image().save_png("res://../docs/reference/topics-"+suffix+".png")
 if saved!=OK:
  quit(1)
  return
 var count=browser.topics.size()
 browser._received({"ok":false,"error":"Connection unavailable. Please retry."})
 assert(browser.topics.size()==count and "Previously loaded" in browser.status.text)
 browser.queue_free()
 await process_frame
 assert(not route.has_node("TopicBrowser"))
 assert(route.input.editable)
 print("LIVE_TOPICS_PASS: ",count," public topics; error preserves prior data; panel closes")
 quit(0)
