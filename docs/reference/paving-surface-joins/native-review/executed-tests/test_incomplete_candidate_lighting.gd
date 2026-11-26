extends SceneTree

func _initialize():call_deferred("run")

func run():
 var output=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 assert(not output.is_empty())
 var scene=load("res://garden_preview.tscn").instantiate()
 root.add_child(scene)
 var contract=preload("res://runtime/backdrop_wash.gd")
 var names=contract.receiver_names(scene)
 assert(names.size()==6)
 var wash=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/backdrop-wash-index.json"))
 var ordinary=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/full-index.json"))
 assert(contract.matches_receivers(wash,scene))
 assert(preload("res://runtime/baked_materials.gd").source_matches(wash))
 assert(not preload("res://runtime/baked_materials.gd").source_matches(ordinary))
 var before={}
 for name in names:
  var node=scene.find_child(name,true,false)
  before[name]={"layers":node.layers,"materials":[]}
  for surface in range(node.mesh.get_surface_count()):before[name].materials.append(node.get_active_material(surface))
 assert(contract.apply_baked(scene)==-1)
 for name in names:
  var node=scene.find_child(name,true,false)
  assert(node.layers==before[name].layers)
  for surface in range(node.mesh.get_surface_count()):assert(node.get_active_material(surface)==before[name].materials[surface])
 var report={"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"wash_manifest_sha256":FileAccess.get_sha256("res://lightmaps/backdrop-wash/manifest.json"),"test_sha256":FileAccess.get_sha256("res://tests/test_incomplete_candidate_lighting.gd"),"runtime_sha256":FileAccess.get_sha256("res://runtime/backdrop_wash.gd"),"current_wash_stale_ordinary_rejected":true,"receiver_materials_and_layers_unchanged":true,"scope":"Actual fresh six-receiver wash plus previous-source ordinary catalog is rejected before any material/layer mutation. Not full fresh lighting or art acceptance."}
 FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 scene.free()
 await process_frame
 print("INCOMPLETE_CANDIDATE_LIGHTING_REJECTED_WITHOUT_MUTATION")
 quit(0)
