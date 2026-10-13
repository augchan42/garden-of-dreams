extends SceneTree
func _initialize()->void:
 create_timer(60).timeout.connect(func():quit(1))
 call_deferred("run")
func run()->void:
 var viewport:=SubViewport.new()
 viewport.size=Vector2i(1410,600)
 viewport.own_world_3d=true
 viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
 root.add_child(viewport)
 var stage:=Node3D.new()
 viewport.add_child(stage)
 var environment:=WorldEnvironment.new()
 environment.environment=Environment.new()
 environment.environment.background_mode=Environment.BG_COLOR
 environment.environment.background_color=Color("bcb9b2")
 environment.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
 environment.environment.ambient_light_color=Color.WHITE
 environment.environment.ambient_light_energy=0.7
 stage.add_child(environment)
 var camera:=Camera3D.new()
 stage.add_child(camera)
 camera.position=Vector3(0,3.75,18)
 camera.look_at(Vector3(0,3.75,0))
 camera.projection=Camera3D.PROJECTION_ORTHOGONAL
 camera.keep_aspect=Camera3D.KEEP_WIDTH
 camera.size=22
 camera.current=true
 for mode in ["baseline","candidate"]:
  for name in ["moonlit","dusk","mist"]:
   var model:Node3D=(load("res://assets/%s-%s.glb"%[mode,name]) as PackedScene).instantiate()
   stage.add_child(model)
   var mesh:=model.find_child("*render*",true,false) as MeshInstance3D
   var material:=mesh.get_active_material(0) as StandardMaterial3D
   assert(material.albedo_texture.get_width()==(4096 if mode=="baseline" else 2048))
   await create_timer(0.5).timeout
   RenderingServer.force_draw()
   var file="res://../native-raw/%s-%s.png"%[mode,name]
   assert(viewport.get_texture().get_image().save_png(file)==OK)
   print("STAGE_RAW_VIEW_SAVED ",mode," ",name)
   model.queue_free()
   await process_frame
 print("STAGE_RAW_RENDER_PASS")
 quit(0)
