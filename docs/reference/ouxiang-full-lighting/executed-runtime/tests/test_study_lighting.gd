extends SceneTree

func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 await process_frame
 var key:SpotLight3D=null
 var lanterns:Array[OmniLight3D]=[]
 for light in route.find_children("*","Light3D",true,false):
  if light is SpotLight3D and "qiushuang" in light.name:key=light
  if light is OmniLight3D and "study_warm" in light.name:lanterns.append(light)
 if key==null or lanterns.size()!=2:
  push_error("Study key or lantern lights missing from imported scene")
  quit(1)
  return
 if key.global_position.distance_to(Vector3(22,2.6,-12))>.1 or key.light_energy<2.5 or key.light_color.r<=key.light_color.g:
  push_error("Study key is not the approved warm frontal key")
  quit(1)
  return
 if lanterns[0].light_color.r<=lanterns[0].light_color.g or lanterns[1].light_color.r<=lanterns[1].light_color.g:
  push_error("Study lanterns should provide warm light")
  quit(1)
  return
 print("STUDY_LIGHTING_PASS: warm frontal key and two imported lantern lights")
 quit(0)
