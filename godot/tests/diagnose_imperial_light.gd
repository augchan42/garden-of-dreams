extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(0,.04,-20.5)
 route._arrive("daguan_lou",true)
 route.execute_command("doors")
 await create_timer(1.6).timeout
 var nodes:Array[Node]=[route]
 var key:SpotLight3D
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is SpotLight3D and "daguan" in str(node.name):key=node
 assert(key!=null)
 print("IMPERIAL_KEY ",key.global_position," energy ",key.light_energy," range ",key.spot_range," angle ",key.spot_angle)
 var original_transform=key.global_transform
 var original_energy=key.light_energy
 var original_bias=key.shadow_bias
 var original_normal_bias=key.shadow_normal_bias
 print("SHADOW_BIAS ",original_bias," NORMAL_BIAS ",original_normal_bias)
 var variants=["baseline","no-shadow","stronger","front-side","strong20","strong40","strong20-no-shadow","strong20-bias","bias05","bias1","bias2"]
 for variant in variants:
  key.global_transform=original_transform
  key.light_energy=original_energy
  key.shadow_enabled=true
  key.shadow_bias=original_bias
  key.shadow_normal_bias=original_normal_bias
  if variant=="no-shadow":key.shadow_enabled=false
  if variant=="stronger":key.light_energy=6.0
  if variant=="strong20":key.light_energy=20.0
  if variant=="strong40":key.light_energy=40.0
  if variant=="strong20-no-shadow":
   key.light_energy=20.0
   key.shadow_enabled=false
  if variant=="strong20-bias":
   key.light_energy=20.0
   key.shadow_bias=original_bias*2.0
   key.shadow_normal_bias=original_normal_bias*1.5
  if variant in ["bias05","bias1","bias2"]:
   key.light_energy=20.0
   key.shadow_bias={"bias05":0.5,"bias1":1.0,"bias2":2.0}[variant]
  if variant=="front-side":
   key.global_position=Vector3(2,2.8,-18)
   key.look_at(Vector3(0,1.5,-23))
   key.light_energy=3.0
  await create_timer(.3).timeout
  await RenderingServer.frame_post_draw
  assert(root.get_texture().get_image().save_png("res://../docs/reference/imperial-light-"+variant+".png")==OK)
 print("IMPERIAL_LIGHT_DIAGNOSTICS_SAVED")
 quit(0)
