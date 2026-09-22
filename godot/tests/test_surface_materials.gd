extends SceneTree
func _initialize() -> void:
 var scene=load("res://assets/garden-of-dreams.glb").instantiate()
 var nodes:Array[Node]=[scene]
 var counts={"MAT_water":0,"MAT_aojing_water":0,"MAT_fog_plane":0}
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D:
   for i in range(node.mesh.get_surface_count()):
    var original=node.mesh.surface_get_material(i)
    if original and original.resource_name in counts:
     var material=node.get_active_material(i)
     if not material is ShaderMaterial:
      push_error("Animated surface missing: "+original.resource_name)
      scene.free()
      quit(1)
      return
     counts[original.resource_name]+=1
 scene.free()
 if counts.MAT_aojing_water!=1 or counts.MAT_water<1 or counts.MAT_fog_plane<1:
  push_error("Water/fog surfaces were not checked")
  quit(1)
  return
 print("SURFACE_MATERIAL_PASS ",counts)
 quit(0)
