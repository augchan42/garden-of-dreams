extends SceneTree

const VARIANTS = ["bamboo_small", "bamboo_medium", "bamboo_large", "plum", "willow", "banana", "reed", "potted"]
var stage: Node3D
var camera: Camera3D

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	stage = Node3D.new()
	root.add_child(stage)
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color("cec7bb")
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color("e1e5ee")
	environment.environment.ambient_light_energy = 0.65
	stage.add_child(environment)
	var sun := DirectionalLight3D.new()
	sun.light_energy = 1.5
	sun.light_color = Color("fff1df")
	sun.rotation_degrees = Vector3(-48, -30, 0)
	stage.add_child(sun)
	camera = Camera3D.new()
	stage.add_child(camera)
	camera.position = Vector3(5.25, 5.0, 20)
	camera.look_at(Vector3(5.25, 5.0, 0))
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 25
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.current = true
	root.size = Vector2i(1600, 1000)
	for lod in [false, true]:
		var models := Node3D.new()
		stage.add_child(models)
		for index in range(VARIANTS.size()):
			var suffix := "_LOD1" if lod else ""
			var path := "res://assets/kits/flora/KIT_flora_%s%s.glb" % [VARIANTS[index], suffix]
			var scene := load(path) as PackedScene
			assert(scene != null, path)
			var plant := scene.instantiate() as Node3D
			models.add_child(plant)
			plant.position = Vector3((index % 4) * 3.5, (1 - index / 4) * 5.2, 0)
			var label := Label3D.new()
			label.text = VARIANTS[index].replace("_", " ")
			label.position = plant.position + Vector3(0, -0.15, 0.9)
			label.font_size = 36
			label.pixel_size = 0.006
			label.modulate = Color("433d38")
			label.outline_size = 0
			label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
			models.add_child(label)
		await create_timer(1).timeout
		await RenderingServer.frame_post_draw
		var path := "res://../docs/reference/flora-kit%s.png" % ("-lod1" if lod else "")
		assert(root.get_texture().get_image().save_png(path) == OK)
		models.queue_free()
		await process_frame
	print("FLORA_RENDER_PASS")
	quit()
