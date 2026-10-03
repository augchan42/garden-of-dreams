extends SceneTree
func _initialize() -> void:
 var scene=(load("res://assets/garden-of-dreams.glb") as PackedScene).instantiate()
 var shared=load("res://materials/props_atlas.tres")
 var nodes:Array[Node]=[scene]
 var batches=0
 var triangles=0
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D and str(node.name).contains("MAT_props_atlas"):
   batches+=1
   assert(node.mesh.get_surface_count()==1,"A prop batch gained an extra draw surface")
   assert(node.mesh.surface_get_material(0)==shared,"Prop source material is duplicated")
   assert(node.get_active_material(0)==shared)
   assert(node.visibility_range_end==28.0)
   var arrays=node.mesh.surface_get_arrays(0)
   assert(not arrays[Mesh.ARRAY_TEX_UV2].is_empty())
   triangles+=arrays[Mesh.ARRAY_INDEX].size()/3
 assert(batches==7,str(batches))
 assert(triangles==25060,str(triangles))
 scene.free()
 print("PROP_PLACEMENTS_PASS: 32 props in 7 shared-material batches, UV2 present")
 quit(0)
