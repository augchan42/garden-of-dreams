extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func capture(label:String) -> void:
 await create_timer(.5).timeout
 await RenderingServer.frame_post_draw
 var result=root.get_texture().get_image().save_png("res://../docs/reference/lightmap-"+label+".png")
 assert(result==OK)
func run() -> void:
 var scene=load("res://garden_preview.tscn").instantiate()
 root.add_child(scene)
 var camera=Camera3D.new()
 scene.add_child(camera)
 camera.position=Vector3(8,4,9)
 camera.look_at(Vector3(0,1.2,0))
 camera.current=true
 var target:MeshInstance3D
 var nodes:Array[Node]=[scene]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D and str(node.name)=="SITE_qinfang-ting_MAT_plaster_rock":target=node
  if node is OmniLight3D:node.light_cull_mask=3
 assert(target!=null)
 await capture("dynamic")
 var records = JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/index.json"))
 var selected = {}
 for key in records:
  if records[key].site == "qinfang-ting":selected[key]=records[key]
 var count = preload("res://runtime/baked_materials.gd").apply_to_scene(scene,selected)
 if count!=15:
  push_error("Incomplete Qinfang bake coverage: %d" % count)
  quit(1)
  return
 print("BAKED_MATERIALS_APPLIED ",count)
 await capture("baked")
 print("LIGHTMAP_PREVIEW_SAVED")
 quit(0)
