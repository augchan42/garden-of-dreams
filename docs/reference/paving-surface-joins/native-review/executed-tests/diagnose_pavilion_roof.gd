extends SceneTree

func _initialize():
 create_timer(45).timeout.connect(func(): push_error("Roof probe timed out"); quit(1))
 call_deferred("run")

func run():
 root.size=Vector2i(390,844)
 var route=load("res://runtime/first_reading_demo.tscn").instantiate()
 root.add_child(route)
 route.player.position=Vector3(0,.03,1.8)
 route._arrive("qinfang_ting",true)
 await create_timer(1.5).timeout
 var mesh=route.find_child("SITE_qinfang-ting_MAT_pavilion_atlas",true,false) as MeshInstance3D
 assert(mesh!=null)
 var original=mesh.get_active_material(0) as ShaderMaterial
 assert(original!=null)
 RenderingServer.force_draw()
 assert(root.get_texture().get_image().save_png("/tmp/garden-roof-baseline.png")==OK)
 var shader=Shader.new()
 shader.code="""shader_type spatial;
render_mode unshaded,cull_disabled;
uniform sampler2D paint:source_color,filter_linear_mipmap;
uniform sampler2D irradiance:repeat_disable,filter_linear;
uniform float irradiance_scale=1.0;
uniform int mode=0;
varying vec3 normal_world;
void vertex(){normal_world=MODEL_NORMAL_MATRIX*NORMAL;}
void fragment(){
 bool roof=UV.x>0.515625 && UV.x<0.984375 && UV.y>0.015625 && UV.y<0.484375;
 vec3 color=vec3(0.02);
 if(roof){
  if(mode==0)color=texture(paint,UV).rgb;
  if(mode==1)color=texture(irradiance,UV2).rgb*irradiance_scale*3.14159265;
  if(mode==2)color=normalize(normal_world)*0.5+0.5;
  if(mode==3)color=normal_world.y>0.25?vec3(0.0,0.25,1.0):(normal_world.y< -0.25?vec3(1.0,0.0,0.0):vec3(0.0,1.0,0.0));
 }
 ALBEDO=color;
}"""
 var probe=ShaderMaterial.new()
 probe.shader=shader
 probe.set_shader_parameter("paint",original.get_shader_parameter("albedo_texture"))
 probe.set_shader_parameter("irradiance",original.get_shader_parameter("lightmap"))
 probe.set_shader_parameter("irradiance_scale",original.get_shader_parameter("lightmap_scale"))
 mesh.set_surface_override_material(0,probe)
 for i in range(4):
  probe.set_shader_parameter("mode",i)
  await create_timer(.3).timeout
  RenderingServer.force_draw()
  assert(root.get_texture().get_image().save_png("/tmp/garden-roof-"+["albedo","irradiance","normals","orientation"][i]+".png")==OK)
 print("ROOF_RENDER_PROBE_PASS source=",FileAccess.get_sha256("res://assets/garden-of-dreams.glb")," scale=",original.get_shader_parameter("lightmap_scale"))
 route.queue_free()
 await process_frame
 quit(0)
