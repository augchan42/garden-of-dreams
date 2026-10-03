extends SceneTree
const VARIANTS = ["lantern_hanging", "lantern_standing", "brazier", "stone_table", "stone_stool", "incense_burner", "scroll", "screen"]
var meshes := 0
var collisions := 0
var lights := 0
var material: ORMMaterial3D
func _initialize() -> void:
	create_timer(10).timeout.connect(func(): quit(1))
	call_deferred("run")
func run() -> void:
	material = load("res://materials/props_atlas.tres")
	assert(material.albedo_texture.get_width() == 1024)
	assert(material.orm_texture.get_width() == 256)
	assert(material.emission_texture.get_width() == 256)
	assert(material.emission_enabled and material.emission_operator == BaseMaterial3D.EMISSION_OP_MULTIPLY)
	for name in VARIANTS:
		for suffix in ["", "_LOD1"]:
			var scene := (load("res://assets/kits/props/KIT_props_%s%s.glb" % [name, suffix]) as PackedScene).instantiate()
			var before := collisions
			inspect(scene)
			var expected: int = {"lantern_hanging":0, "lantern_standing":2, "brazier":1, "stone_table":1, "stone_stool":1, "incense_burner":1, "scroll":0, "screen":3}[name]
			assert(collisions-before == expected)
			scene.free()
	assert(meshes == 16 and collisions == 18 and lights == 0)
	print("PROPS_RUNTIME_PASS: 16 models, shared PBR material, 18 colliders, no embedded practical lights")
	quit()
func inspect(node: Node) -> void:
	if node is MeshInstance3D:
		meshes += 1
		assert(not str(node.name).begins_with("COL_"))
		assert(node.mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV2].size()>0)
		for index in range(node.mesh.get_surface_count()):
			assert(node.get_active_material(index) == material)
			assert(node.mesh.surface_get_material(index) == material)
	if node is CollisionShape3D:
		collisions += 1
		assert(node.shape != null)
	if node is Light3D:lights += 1
	for child in node.get_children():inspect(child)
