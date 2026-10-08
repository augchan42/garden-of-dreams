@tool
extends EditorScenePostImport
func _post_import(scene: Node) -> Object:
 var nodes:Array[Node]=[scene]
 while not nodes.is_empty():
  var node=nodes.pop_back();nodes.append_array(node.get_children())
  if node is MeshInstance3D:
   for i in range(node.mesh.get_surface_count()):
    var source=node.mesh.surface_get_material(i)
    assert(source!=null)
    var key=source.resource_name.trim_prefix("MAT_stage_").split(".")[0]
    var shared=load("res://materials/stage/"+key+".tres") as Material
    assert(shared!=null,"Unknown stage material "+key)
    node.mesh.surface_set_material(i,shared);node.set_surface_override_material(i,shared)
 return scene
