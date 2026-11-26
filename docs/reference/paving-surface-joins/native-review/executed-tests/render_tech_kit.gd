extends SceneTree
const VARIANTS=["crt_amber","crt_green","monitor_bank","cable_run","cell_door","terminal_desk"]
func _initialize() -> void:
 create_timer(20).timeout.connect(func():quit(1))
 call_deferred("run")
func run() -> void:
 root.size=Vector2i(1600,1000)
 var stage=Node3D.new();root.add_child(stage)
 var world=WorldEnvironment.new();world.environment=Environment.new();world.environment.background_mode=Environment.BG_COLOR;world.environment.background_color=Color("bbb9b1");world.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;world.environment.ambient_light_color=Color("e0e4eb");world.environment.ambient_light_energy=.6;stage.add_child(world)
 var sun=DirectionalLight3D.new();sun.light_energy=1.2;sun.light_color=Color("fff1dc");sun.rotation_degrees=Vector3(-35,-25,0);stage.add_child(sun)
 var camera=Camera3D.new();stage.add_child(camera);camera.position=Vector3(3.6,4.5,15);camera.look_at(Vector3(3.6,2.3,0));camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.keep_aspect=Camera3D.KEEP_WIDTH;camera.size=14.5;camera.current=true
 for suffix in ["","_LOD1"]:
  var models=Node3D.new();stage.add_child(models)
  for index in range(VARIANTS.size()):
   var model=(load("res://assets/kits/tech/KIT_tech_%s%s.glb"%[VARIANTS[index],suffix]) as PackedScene).instantiate();models.add_child(model);model.position=Vector3((index%3)*3.6,(1-index/3)*3.2,0)
   var label=Label3D.new();label.text=VARIANTS[index].replace("_"," ");label.position=model.position+Vector3(.8 if VARIANTS[index]=="cable_run" else 0,-.26,.2);label.font_size=32;label.pixel_size=.006;label.outline_size=0;label.modulate=Color("35322f");label.billboard=BaseMaterial3D.BILLBOARD_ENABLED;models.add_child(label)
  await create_timer(1).timeout
  await RenderingServer.frame_post_draw
  assert(root.get_texture().get_image().save_png("res://../docs/reference/tech-kit"+("-lod1" if suffix!="" else "")+".png")==OK)
  models.queue_free();await process_frame
 camera.position=Vector3(0,.6,2)
 camera.look_at(Vector3(0,.34,0))
 camera.size=1.7
 for index in range(2):
  var model=(load("res://assets/kits/tech/KIT_tech_%s.glb"%VARIANTS[index]) as PackedScene).instantiate()
  stage.add_child(model);model.position.x=(index-.5)*.85
 await create_timer(1).timeout
 await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png("res://../docs/reference/tech-crt-detail.png")==OK)
 print("TECH_RENDER_PASS")
 quit(0)
