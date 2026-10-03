@tool
extends EditorScenePostImport

func _post_import(scene: Node) -> Object:
	var material := load("res://materials/props_atlas.tres") as Material
	_apply(scene, material)
	return scene

func _apply(node: Node, material: Material) -> void:
	if node is MeshInstance3D:
		for surface in range(node.mesh.get_surface_count()):
			node.mesh.surface_set_material(surface, material)
			node.set_surface_override_material(surface, material)
	for child in node.get_children():
		_apply(child, material)
