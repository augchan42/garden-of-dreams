extends SceneTree

func _initialize():call_deferred("run")

func run():
 var output=""
 var expected_count=0
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
  if arg.begins_with("--receivers="):expected_count=int(arg.trim_prefix("--receivers="))
 if output.is_empty() or expected_count not in [5,6]:
  push_error("Provide output and independently expected five/six receiver count")
  quit(1)
  return
 var scene=load("res://garden_preview.tscn").instantiate()
 root.add_child(scene)
 var contract=preload("res://runtime/backdrop_wash.gd")
 var original={}
 for mesh in scene.find_children("*","MeshInstance3D",true,false):original[str(mesh.name)]=mesh.layers
 var names=contract.receiver_names(scene)
 if names.size()!=expected_count or contract.configure(scene)!=expected_count:
  push_error("Actual imported backdrop does not have the expected receiver set")
  scene.free()
  quit(1)
  return
 var records={}
 for name in names:records[name]=true
 assert(contract.matches_receivers(records,scene))
 var missing=records.duplicate()
 missing.erase(names[-1])
 assert(not contract.matches_receivers(missing,scene))
 var substituted=missing.duplicate()
 substituted["SITE_building"]=true
 assert(substituted.size()==expected_count and not contract.matches_receivers(substituted,scene))
 var unchanged=0
 for mesh in scene.find_children("*","MeshInstance3D",true,false):
  var name=str(mesh.name)
  if name in names:
   assert(mesh.layers==(original[name]|4))
  else:
   assert(mesh.layers==original[name])
   unchanged+=1
 var wash=scene.get_node("BackdropWash")
 assert(wash.light_cull_mask==4 and not wash.shadow_enabled)
 var report={"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"test_sha256":FileAccess.get_sha256("res://tests/test_wash_receiver_contract.gd"),"runtime_sha256":FileAccess.get_sha256("res://runtime/backdrop_wash.gd"),"expected_count":expected_count,"receivers":names,"unchanged_other_meshes":unchanged,"missing_catalog_rejected":true,"same_count_substitution_rejected":true,"scope":"Actual native imported receiver metadata and dynamic layer isolation. Catalog key rejection only; no fresh baked lighting, pixels or production acceptance."}
 FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 scene.free()
 await process_frame
 print("NATIVE_WASH_RECEIVER_CONTRACT_PASS ",expected_count," receivers; ",unchanged," other meshes unchanged")
 quit(0)
