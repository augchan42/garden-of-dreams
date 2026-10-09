extends SceneTree
func _initialize() -> void:
 create_timer(30).timeout.connect(func():quit(1))
 call_deferred("run")
func run() -> void:
 root.content_scale_size=Vector2i.ZERO;root.size=Vector2i(940,400)
 var garden=(load("res://assets/garden-of-dreams.glb") as PackedScene).instantiate() as Node3D;root.add_child(garden)
 preload("res://runtime/backdrop_wash.gd").configure(garden)
 var world=WorldEnvironment.new();world.environment=Environment.new();world.environment.background_mode=Environment.BG_COLOR;world.environment.background_color=Color("bd00bd");world.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;world.environment.ambient_light_color=Color(.25,.25,.3);world.environment.ambient_light_energy=.5;root.add_child(world)
 var camera=Camera3D.new();root.add_child(camera);camera.current=true;camera.fov=22;camera.position=Vector3(0,12,0)
 root.add_child(load("res://runtime/color_grade.tscn").instantiate())
 for i in range(8):
  var angle=float(i)*TAU/8.;camera.look_at(Vector3(48*sin(angle),9,48*cos(angle)))
  await create_timer(.5).timeout;await RenderingServer.frame_post_draw
  assert(root.get_texture().get_image().save_png("res://../docs/reference/enclosure-view-"+str(i)+".png")==OK)
 print("STAGE_ENCLOSURE_RENDER_PASS: eight graded pavilion perimeter views")
 quit(0)
