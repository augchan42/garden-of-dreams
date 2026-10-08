extends SceneTree
func _initialize() -> void:
	create_timer(10).timeout.connect(func(): quit(1))
	call_deferred("run")
func run() -> void:
	var garden: Node = load("res://garden_preview.tscn").instantiate()
	root.add_child(garden)
	var flora := preload("res://runtime/flora_lod.gd").new()
	root.add_child(flora)
	flora.configure(garden)
	assert(flora.plants.size() == 23)
	var material := load("res://materials/flora_atlas.tres")
	for plant in flora.plants:
		assert(plant.node.get_active_material(0) == material)
		assert(plant.base.surface_get_material(0) == material)
		var before: AABB = plant.base.get_aabb()
		var after: AABB = plant.lower.get_aabb()
		# Both imported meshes must use the same local axes and nearly the same bounds.
		assert(before.position.distance_to(after.position) < 0.15)
		assert(before.size.distance_to(after.size) < 0.2)
		flora.update_distance(plant.node.global_position + Vector3(40, 0, 0))
		assert(plant.node.mesh == plant.lower)
		flora.update_distance(plant.node.global_position + Vector3(14, 0, 0))
		assert(plant.node.mesh == plant.lower, "Distance hysteresis failed")
		flora.update_distance(plant.node.global_position)
		assert(plant.node.mesh == plant.base)
		assert(plant.node.get_active_material(0) == material)
	print("FLORA_PLACEMENT_RUNTIME_PASS: 23 plants, aligned LOD bounds, shared material, distance hysteresis")
	quit()
