@tool
extends EditorScenePostImport

# All variants and LODs share one material and one 2048px atlas in runtime memory.
func _post_import(scene: Node) -> Object:
	var material: Material = load("res://materials/flora_atlas.tres")
	_apply(scene, material)
	return scene

func _apply(node: Node, material: Material) -> void:
	if node is MeshInstance3D:
		for surface in range(node.mesh.get_surface_count()):
			node.set_surface_override_material(surface, material)
	for child in node.get_children():
		_apply(child, material)
