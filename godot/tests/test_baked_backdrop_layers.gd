extends SceneTree
func _initialize():call_deferred("run")
func run():
 var scene=Node3D.new()
 root.add_child(scene)
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/demo-index.json"))
 var probe_record=records.values()[0]
 var baked={}
 var names=["SITE_stage_MAT_painted_mountains_0","SITE_stage_MAT_painted_mountains_1","SITE_stage_MAT_painted_mountains_2","SITE_stage_MAT_painted_moon","SITE_stage_MAT_stage_cyclorama_blue"]
 for name in names:
  var mesh=MeshInstance3D.new()
  mesh.name=name
  mesh.mesh=BoxMesh.new()
  mesh.mesh.material=StandardMaterial3D.new()
  scene.add_child(mesh)
  if not "cyclorama" in name:baked[name]=probe_record
 assert(preload("res://runtime/backdrop_wash.gd").configure(scene)==5)
 assert(preload("res://runtime/baked_materials.gd").apply_to_scene(scene,baked)==4)
 for name in names:
  var mesh=scene.get_node(name)
  var expected=5 if "cyclorama" in name else 6
  if mesh.layers!=expected:
   push_error("Baking dropped the linked backdrop receiver layer: "+name+" layers="+str(mesh.layers))
   scene.free()
   quit(1)
   return
 assert(scene.get_node("BackdropWash").light_cull_mask==4)
 scene.free()
 print("BAKED_BACKDROP_LAYERS_PASS: four baked flats retain the wash; unbaked sky and exclusive wash mask preserved")
 quit()
