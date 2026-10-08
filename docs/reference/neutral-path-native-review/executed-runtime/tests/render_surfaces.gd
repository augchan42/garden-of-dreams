extends SceneTree
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var scene=load("res://garden_preview.tscn").instantiate()
 root.add_child(scene)
 var camera=Camera3D.new()
 scene.add_child(camera)
 camera.position=Vector3(12,3.1,7)
 camera.look_at(Vector3(9,-.6,0))
 camera.current=true
 var water=load("res://materials/water.tres")
 var fog=load("res://materials/floor_fog.tres")
 water.set_shader_parameter("timeline_time",0.0)
 fog.set_shader_parameter("timeline_time",0.0)
 for phase in [["baseline",0.0,0.0],["water",100.0,0.0],["fog",0.0,100.0]]:
  water.set_shader_parameter("phase_offset",phase[1])
  fog.set_shader_parameter("phase_offset",phase[2])
  await create_timer(1).timeout
  await RenderingServer.frame_post_draw
  var image=root.get_texture().get_image()
  var result=image.save_png("res://../docs/reference/surfaces-%s.png" % phase[0])
  if result != OK:
   push_error("Surface render failed")
   quit(1)
   return
 water.set_shader_parameter("phase_offset",0.0)
 fog.set_shader_parameter("phase_offset",0.0)
 water.set_shader_parameter("timeline_time",-1.0)
 fog.set_shader_parameter("timeline_time",-1.0)
 print("SURFACE_RENDERS_SAVED")
 quit(0)
