extends SceneTree
const VARIANTS = ["lantern_hanging", "lantern_standing", "brazier", "stone_table", "stone_stool", "incense_burner", "scroll", "screen", "folding_chair"]
var stage: Node3D
func _initialize() -> void:
	create_timer(20).timeout.connect(func(): quit(1))
	call_deferred("run")
func run() -> void:
	root.content_scale_size = Vector2i.ZERO
	root.size = Vector2i(1000,1000)
	stage = Node3D.new()
	root.add_child(stage)
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color("b8bab7")
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color("dee2ec")
	environment.environment.ambient_light_energy = 0.7
	stage.add_child(environment)
	var sun := DirectionalLight3D.new()
	sun.light_energy = 1.3
	sun.light_color = Color("fff1dc")
	sun.rotation_degrees = Vector3(-40, -25, 0)
	stage.add_child(sun)
	var camera := Camera3D.new()
	stage.add_child(camera)
	camera.position = Vector3(4.5, 5.5, 20)
	camera.look_at(Vector3(4.5, 1.5, 0))
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.size = 20
	camera.current = true
	for lod in [false,true]:
		var suffix := "_LOD1" if lod else ""
		var model := (load("res://assets/kits/props/KIT_props_folding_chair%s.glb" % suffix) as PackedScene).instantiate() as Node3D
		stage.add_child(model)
		camera.position = Vector3(.95,.8,1.4)
		camera.look_at(Vector3(0,.45,0))
		camera.size = 1.25
		await create_timer(1).timeout
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png("res://../docs/reference/folding-chair%s.png" % ("-lod1" if lod else ""))==OK)
		model.queue_free()
		await process_frame
	print("CHAIR_RENDER_PASS")
	quit()
