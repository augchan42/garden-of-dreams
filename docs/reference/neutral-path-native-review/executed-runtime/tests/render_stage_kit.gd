extends SceneTree
const VARIANTS=["cyclorama_moonlit","cyclorama_dusk","cyclorama_mist","studio_wall","floor_boards","fog_plane","gel_frame"]
func _initialize() -> void:
 create_timer(30).timeout.connect(func():quit(1))
 call_deferred("run")
func capture(name:String) -> void:
 await create_timer(1).timeout
 await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png("res://../docs/reference/"+name+".png")==OK)
func run() -> void:
 root.content_scale_size=Vector2i.ZERO;root.size=Vector2i(1600,1000)
 var stage=Node3D.new();root.add_child(stage)
 var world=WorldEnvironment.new();world.environment=Environment.new();world.environment.background_mode=Environment.BG_COLOR;world.environment.background_color=Color("bcb9b2");world.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;world.environment.ambient_light_color=Color("e2e4eb");world.environment.ambient_light_energy=.7;stage.add_child(world)
 var sun=DirectionalLight3D.new();sun.light_energy=1.3;sun.light_color=Color("fff0d8");sun.rotation_degrees=Vector3(-40,-25,0);stage.add_child(sun)
 var camera=Camera3D.new();stage.add_child(camera);camera.position=Vector3(5.5,8.7,20);camera.look_at(Vector3(5.5,4.9,0));camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.keep_aspect=Camera3D.KEEP_WIDTH;camera.size=19;camera.current=true
 for suffix in ["","_LOD1"]:
  var models=Node3D.new();stage.add_child(models)
  for index in range(VARIANTS.size()):
   var model=(load("res://assets/kits/stage/KIT_stage_%s%s.glb"%[VARIANTS[index],suffix]) as PackedScene).instantiate() as Node3D;models.add_child(model);model.position=Vector3((index%3)*5.5,(2-index/3)*4.1,0)
   if index<3:model.scale=Vector3.ONE*.25
   if VARIANTS[index]=="gel_frame":model.scale=Vector3.ONE*2
   var label=Label3D.new();label.text=VARIANTS[index].replace("_"," ");label.position=model.position+Vector3(0,-.35,.5);label.font_size=32;label.pixel_size=.006;label.outline_size=0;label.modulate=Color("33312d");label.billboard=BaseMaterial3D.BILLBOARD_ENABLED;models.add_child(label)
  await capture("stage-kit"+("-lod1" if suffix!="" else ""))
  models.queue_free();await process_frame
 root.size=Vector2i(1410,600);camera.position=Vector3(0,3.75,18);camera.look_at(Vector3(0,3.75,0));camera.size=22
 for name in ["moonlit","dusk","mist"]:
  var model=(load("res://assets/kits/stage/KIT_stage_cyclorama_%s.glb"%name) as PackedScene).instantiate();stage.add_child(model)
  await capture("stage-cyclorama-"+name);model.queue_free();await process_frame
 # Floor/fog and gel detail views retain full-sized source geometry.
 root.size=Vector2i(1000,1000);camera.position=Vector3(3.5,3.5,4);camera.look_at(Vector3(0,.1,0));camera.size=4.6
 var floor_model=(load("res://assets/kits/stage/KIT_stage_floor_boards.glb") as PackedScene).instantiate();stage.add_child(floor_model)
 await capture("stage-floor-detail")
 var fog_model=(load("res://assets/kits/stage/KIT_stage_fog_plane.glb") as PackedScene).instantiate();stage.add_child(fog_model)
 var fog_material=load("res://materials/stage/fog.tres") as ShaderMaterial;fog_material.set_shader_parameter("timeline_time",0.0)
 await capture("stage-fog-detail");fog_material.set_shader_parameter("timeline_time",-1.0)
 floor_model.queue_free();fog_model.queue_free();await process_frame
 camera.position=Vector3(.9,.8,2);camera.look_at(Vector3(0,.55,0));camera.size=1.8
 var gel_model=(load("res://assets/kits/stage/KIT_stage_gel_frame.glb") as PackedScene).instantiate();stage.add_child(gel_model)
 await capture("stage-gel-detail")
 print("STAGE_RENDER_PASS")
 quit(0)
