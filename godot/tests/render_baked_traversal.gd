extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/index.json"))
 if preload("res://runtime/baked_materials.gd").apply_to_scene(route,records)!=records.size():
  push_error("Incomplete traversal bake")
  quit(1)
  return
 var nodes:Array[Node]=[route]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is Light3D:node.shadow_enabled=false
 var directory="res://../docs/reference/baked-traversal"
 DirAccess.make_dir_recursive_absolute(directory)
 var legs=[["exit","rockery_gate"],["enter","qinfang_ting"],["west","ouxiang_xie"],["island","ziling_zhou"],["back","ouxiang_xie"],["back","qinfang_ting"],["board","qiushuang_zhai"],["back","qinfang_ting"],["back","rockery_gate"],["back","terminal_room"]]
 var report={"scope":"Real physics traversal with compressed baked lighting on desktop. Captures are sampled frames, not continuous-motion visual acceptance.","legs":[]}
 for i in range(legs.size()):
  var leg=legs[i]
  route.execute_command(leg[0])
  if not route.travelling:
   push_error("Command did not begin traversal: "+leg[0])
   quit(1)
   return
  var start=Time.get_ticks_msec()
  var next_capture=start+1000
  var frames=[]
  var maximum_practicals=0
  var minimum_y=route.player.position.y
  while route.travelling:
   await RenderingServer.frame_post_draw
   var now=Time.get_ticks_msec()
   minimum_y=minf(minimum_y,route.player.position.y)
   var active=route.get_node("PracticalLights").lights.filter(func(light):return light.visible).size()
   maximum_practicals=maxi(maximum_practicals,active)
   if now-start>60000 or minimum_y < -0.3 or active>4:
    push_error("Traversal timeout, lost floor support or exceeded light budget")
    quit(1)
    return
   if now>=next_capture:
    var name="%02d-%02d-%s.png" % [i,frames.size(),leg[1]]
    if root.get_texture().get_image().save_png(directory+"/"+name)!=OK:
     push_error("Could not write traversal reference")
     quit(1)
     return
    frames.append(name)
    next_capture=now+4000
  if route.room_id!=leg[1]:
   push_error("Failed to reach "+leg[1])
   quit(1)
   return
  report.legs.append({"destination":leg[1],"duration_seconds":(Time.get_ticks_msec()-start)/1000.0,"minimum_player_y":minimum_y,"maximum_practicals":maximum_practicals,"captures":frames})
  print("BAKED_TRAVERSAL_LEG_PASS ",i," ",leg[1])
  await create_timer(1.5).timeout
 FileAccess.open("res://baked-traversal-validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("BAKED_TRAVERSAL_PASS ten legs, floor support, practical budget")
 quit(0)
