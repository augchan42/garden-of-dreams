extends SceneTree
func _initialize() -> void:
 var scene=load("res://garden_preview.tscn").instantiate()
 var nodes:Array[Node]=[scene]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if node is MeshInstance3D and (str(node.name).begins_with("HERO_") or "qinfang" in str(node.name)):print(node.name)
 scene.free()
 quit(0)
