extends SceneTree

func _initialize() -> void:
 var scene=load("res://garden_preview.tscn").instantiate()
 for slug in ["qinfang-ting","ouxiang-xie","ziling-zhou"]:
  var keys=scene.find_children("LGT_"+slug+"_key*","Light3D",true,false)
  assert(keys.size()==1,"Missing or duplicate imported key: "+slug)
  var key=keys[0] as Light3D
  assert(key.light_energy>0 and key.shadow_enabled)
  if slug=="qinfang-ting":
   assert(key is DirectionalLight3D and abs(key.light_energy-.6)<.0001)
  else:
   assert(key is SpotLight3D and key.spot_range>=10)
 var fill=scene.find_children("LGT_stage_green_key*","DirectionalLight3D",true,false)
 assert(fill.size()==1)
 assert(fill[0].light_color.g-(fill[0].light_color.r+fill[0].light_color.b)/2<=.01)
 scene.free()
 print("SITE_KEY_IMPORT_PASS: three native keys, calibrated Sun, neutral shared fill")
 quit(0)
