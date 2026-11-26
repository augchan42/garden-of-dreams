extends SceneTree

func _initialize() -> void:
 create_timer(20).timeout.connect(func():push_error("Site key import check timed out");quit(1))
 call_deferred("run")

func run() -> void:
 var args=OS.get_cmdline_user_args()
 var scene_path="res://garden_preview.tscn" if args.is_empty() else args[0]
 var scene=load(scene_path).instantiate()
 var records=[]
 for slug in ["qinfang-ting","ouxiang-xie","ziling-zhou"]:
  var keys=scene.find_children("LGT_"+slug+"_key*","Light3D",true,false)
  assert(keys.size()==1,"Missing or duplicate imported key: "+slug)
  var key=keys[0] as Light3D
  assert(key.light_energy>0 and key.shadow_enabled)
  if slug=="qinfang-ting":
   assert(key is DirectionalLight3D and abs(key.light_energy-.6)<.0001)
  else:
   assert(key is SpotLight3D and abs(key.spot_range-14)<.0001)
   assert(abs(key.spot_angle-32.5)<.0001,"Imported cone lost its source angle: "+slug)
   assert(abs(key.light_energy-1.8)<.0001)
   # The very narrow source edge must retain a hard falloff after import.
   assert(abs(key.spot_angle_attenuation-1999.9)<2,"Spot edge is unexpectedly broad: "+slug)
   records.append({"name":str(key.name),"half_angle_degrees":key.spot_angle,
    "range_m":key.spot_range,"energy":key.light_energy,
    "distance_attenuation":key.spot_attenuation,
    "angle_attenuation":key.spot_angle_attenuation,"shadow_enabled":key.shadow_enabled})
 var fill=scene.find_children("LGT_stage_green_key*","DirectionalLight3D",true,false)
 assert(fill.size()==1)
 assert(fill[0].light_color.g-(fill[0].light_color.r+fill[0].light_color.b)/2<=.01)
 if args.size()>1:
  var output=FileAccess.open(args[1],FileAccess.WRITE)
  assert(output!=null)
  output.store_string(JSON.stringify({"tested_scene_sha256":FileAccess.get_sha256(scene_path),
   "import_hook_sha256":FileAccess.get_sha256("res://garden_import.gd"),
   "scope":"Actual imported source key angles, falloff and preview rig properties; not rendered lighting or complete scene acceptance.",
   "spots":records,"passed":true},"  ")+"\n")
  output.close()
 scene.free()
 print("SITE_KEY_IMPORT_PASS: three native keys, exact Spot cone angles/hard falloff, calibrated Sun, neutral shared fill")
 quit(0)
