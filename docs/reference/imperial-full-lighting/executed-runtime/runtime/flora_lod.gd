extends Node

var plants: Array[Dictionary] = []
var updates := 0
var elapsed := 0.0

func configure(environment: Node) -> void:
	var catalog = JSON.parse_string(FileAccess.get_file_as_string("res://assets/flora-placements.json"))
	assert(catalog is Dictionary)
	var material := load("res://materials/flora_atlas.tres") as Material
	for name in catalog:
		var node := environment.find_child(name, true, false) as MeshInstance3D
		assert(node != null, "Missing placed flora: " + name)
		var resource := load("res://assets/kits/flora/KIT_flora_%s_LOD1.glb" % catalog[name].variant) as PackedScene
		var temporary := resource.instantiate()
		var lower := _mesh(temporary)
		assert(lower != null)
		plants.append({"node":node, "base":node.mesh, "lower":lower.mesh, "distance":float(catalog[name].lod_distance), "is_lower":false})
		node.lod_bias = 128.0
		for surface in range(node.mesh.get_surface_count()):
			node.set_surface_override_material(surface, material)
		temporary.free()

func _mesh(node: Node) -> MeshInstance3D:
	if node is MeshInstance3D:return node
	for child in node.get_children():
		var result := _mesh(child)
		if result != null:return result
	return null

func _process(delta: float) -> void:
	elapsed += delta
	if elapsed < 0.2:return
	elapsed = 0.0
	var camera := get_viewport().get_camera_3d()
	if camera != null:update_distance(camera.global_position)

func update_distance(position: Vector3) -> void:
	for plant in plants:
		var distance := position.distance_to(plant.node.global_position)
		var lower: bool = plant.is_lower
		if distance > plant.distance + 2.0:lower = true
		elif distance < plant.distance - 2.0:lower = false
		if lower == plant.is_lower:continue
		plant.node.mesh = plant.lower if lower else plant.base
		plant.is_lower = lower
		updates += 1
