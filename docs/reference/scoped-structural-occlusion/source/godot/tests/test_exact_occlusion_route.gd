extends SceneTree
func _initialize():
 create_timer(12).timeout.connect(func():quit(1))
 call_deferred("run")
func run():
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 assert(root.use_occlusion_culling,"Normal route must enable verified exact structural occluders")
 var nodes=route.find_children("ExactOpaque_*","OccluderInstance3D",true,false)
 assert(nodes.size()==5,"Normal route must derive exactly five opaque source occluders")
 assert(not route.get_node("PondReflection").viewport.use_occlusion_culling,"Main culling must not change reflection viewport culling")
 for occluder in nodes:
  assert(occluder.occluder is ArrayOccluder3D)
  assert(occluder.occluder.get_vertices().size()>0 and occluder.occluder.get_indices().size()>0)
 print("EXACT_OCCLUSION_ROUTE_PASS five actual source occluders; reflection unchanged")
 quit()
