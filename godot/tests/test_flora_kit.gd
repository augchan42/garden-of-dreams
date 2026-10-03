extends SceneTree
const VARIANTS = ["bamboo_small", "bamboo_medium", "bamboo_large", "plum", "willow", "banana", "reed", "potted"]
var render_count := 0
var colliders := 0
var material: StandardMaterial3D

func _initialize() -> void:
	material = load("res://materials/flora_atlas.tres")
	assert(material.transparency == BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR)
	assert(material.cull_mode == BaseMaterial3D.CULL_DISABLED)
	assert(material.albedo_texture.get_width() == 2048)
	for variant in VARIANTS:
		for suffix in ["", "_LOD1"]:
			var plant := (load("res://assets/kits/flora/KIT_flora_%s%s.glb" % [variant, suffix]) as PackedScene).instantiate()
			var count_before := colliders
			check(plant)
			assert(colliders - count_before == (1 if variant in ["plum", "willow", "potted"] else 0))
			plant.free()
	assert(render_count == 16)
	assert(colliders == 6)
	print("FLORA_RUNTIME_PASS: 16 models, one shared 2048px alpha-scissor atlas, six colliders")
	quit()

func check(node: Node) -> void:
	if node is MeshInstance3D:
		render_count += 1
		assert(not node.name.begins_with("COL_"))
		assert(node.mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV].size() > 0)
		assert(node.mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV2].size() > 0)
		for surface in range(node.mesh.get_surface_count()):
			assert(node.get_active_material(surface) == material)
	if node is CollisionShape3D:
		colliders += 1
		assert(node.shape != null)
	for child in node.get_children():
		check(child)
