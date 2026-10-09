extends SceneTree
var route
var output:=""
var rows:Array=[]
var materials:Array=[]
var water:ShaderMaterial
var fog:ShaderMaterial
var mirror
var old_reflection:Shader
var neutral_reflection:Shader
var old_ambient:Color
var old_distance_fog:Color
var world_environment:WorldEnvironment
func _initialize()->void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 root.show()
 create_timer(180).timeout.connect(func():push_error("WATER_PALETTE_PROBE_TIMEOUT");quit(1))
 call_deferred("run")
func settle()->void:
 for f in range(16):await process_frame
 var deadline:=Time.get_ticks_msec()+10000
 while route.camera_tween!=null and route.camera_tween.is_valid() and route.camera_tween.is_running() and Time.get_ticks_msec()<deadline:await process_frame
 assert(route.camera_tween==null or not route.camera_tween.is_valid() or not route.camera_tween.is_running())
 RenderingServer.force_draw();await RenderingServer.frame_post_draw
func set_variant(name:String)->void:
 water.set_shader_parameter("water_color",null)
 fog.set_shader_parameter("fog_color",null)
 world_environment.environment.ambient_light_color=old_ambient
 world_environment.environment.fog_light_color=old_distance_fog
 mirror.material.shader=old_reflection
 if name in ["water-slate","slate-combined","lighter-combined","charcoal-combined"]:water.set_shader_parameter("water_color",Color(.25,.32,.40))
 if name in ["ambient-neutral","slate-combined","lighter-combined","charcoal-combined"]:world_environment.environment.ambient_light_color=Color(.38,.38,.40)
 if name in ["fog-grey","slate-combined","lighter-combined","charcoal-combined"]:fog.set_shader_parameter("fog_color",Color(.24,.28,.34))
 if name in ["distance-fog-neutral","slate-combined","lighter-combined","charcoal-combined"]:world_environment.environment.fog_light_color=Color(.10,.13,.18)
 if name in ["reflection-neutral","slate-combined","lighter-combined","charcoal-combined"]:mirror.material.shader=neutral_reflection
 if name=="lighter-combined":water.set_shader_parameter("water_color",Color(.38,.42,.48))
 if name=="charcoal-combined":water.set_shader_parameter("water_color",Color(.28,.30,.34))
 water.set_shader_parameter("timeline_time",10.0);fog.set_shader_parameter("timeline_time",10.0);mirror.material.set_shader_parameter("timeline_time",10.0)
 mirror.update_reflection()
func capture(room:String,aspect:String,variant:String)->void:
 var image:=root.get_texture().get_image();var path:=output+"/%s-%s-%s.png"%[room,aspect,variant];assert(image.save_png(path)==OK)
 var position:Vector3=route.camera.position
 rows.append({"room":room,"aspect":aspect,"variant":variant,"capture":path,"sha256":FileAccess.get_sha256(path),"pixels":[image.get_width(),image.get_height()],"logical_viewport":[root.get_visible_rect().size.x,root.get_visible_rect().size.y],"camera_position":[position.x,position.y,position.z],"camera_fov":route.camera.fov,"water_color":str(water.get_shader_parameter("water_color")),"fog_color":str(fog.get_shader_parameter("fog_color")),"ambient_color":str(world_environment.environment.ambient_light_color),"distance_fog_color":str(world_environment.environment.fog_light_color),"reflection_shader":"neutral_proposal" if mirror.material.shader==neutral_reflection else "original","timeline_time":10.0,"panel_top":route.command_panel.get_global_rect().position.y,"baked_enabled":route.site_bakes_enabled,"reflection_enabled":mirror.viewport.render_target_update_mode==SubViewport.UPDATE_ALWAYS})
func run()->void:
 assert(output!="" and DisplayServer.get_name()!="headless");DirAccess.make_dir_recursive_absolute(output)
 water=load("res://materials/water.tres");fog=load("res://materials/floor_fog.tres")
 water.set_shader_parameter("timeline_time",10.0);fog.set_shader_parameter("timeline_time",10.0)
 route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route);await settle()
 mirror=route.get_node("PondReflection");old_reflection=mirror.material.shader
 neutral_reflection=Shader.new();neutral_reflection.code=old_reflection.code.replace("ALBEDO=vec3(.009,.04,.018);","ALBEDO=vec3(.022,.03,.04);").replace("reflected*vec3(.55,.9,.6)","reflected*vec3(.85,.85,.85)")
 var environments=route.find_children("*","WorldEnvironment",true,false);assert(environments.size()==1);world_environment=environments[0];old_ambient=world_environment.environment.ambient_light_color;old_distance_fog=world_environment.environment.fog_light_color
 var diagnostics:Array=[]
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   var material=node.get_active_material(i)
   if material==water or material==mirror.material:
    diagnostics.append({"mesh":str(node.name),"surface":i,"layers":node.layers,"material":material.resource_name,"shader":material.shader.resource_path,"world_position":str(node.global_position)})
    materials.append({"node":node,"surface":i,"material":material})
 assert(materials.size()>=2)
 var variants=["baseline","water-slate","ambient-neutral","fog-grey","distance-fog-neutral","reflection-neutral","slate-combined","lighter-combined","charcoal-combined"]
 for room in ["qinfang_ting","ouxiang_xie","ziling_zhou","aojing_guan"]:
  route.player.position={"qinfang_ting":Vector3(0,.03,1.8),"ouxiang_xie":Vector3(-23,.03,0),"ziling_zhou":Vector3(-35.4,.03,0),"aojing_guan":Vector3(26,-.61,13.1)}[room]
  for aspect in ["desktop","portrait"]:
   root.size=Vector2i(1410,600) if aspect=="desktop" else Vector2i(390,844);route._configure_ui_scale(false,160);await settle();route._arrive(room,true);await settle()
   for variant in variants:set_variant(variant);await settle();capture(room,aspect,variant)
   set_variant("baseline")
   var control:=ShaderMaterial.new();control.shader=Shader.new();control.shader.code="shader_type spatial;render_mode unshaded,cull_disabled;void fragment(){ALBEDO=vec3(1.0,0.0,1.0);}"
   for item in materials:item.node.set_surface_override_material(item.surface,control)
   await settle();capture(room,aspect,"visible-water-control")
   for item in materials:item.node.set_surface_override_material(item.surface,item.material)
 # Keep the proposed reed pose separate from the production-camera comparisons.
 root.size=Vector2i(390,844);route.player.position=Vector3(-35.4,.03,0);route._arrive("ziling_zhou",true);await settle()
 route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=60;route._camera_to(Vector3(-40,3.2,6),Vector3(-34,-3,0),true)
 for variant in ["baseline","slate-combined","lighter-combined"]:set_variant(variant);await settle();capture("ziling_zhou","proposed-portrait",variant)
 var file:=FileAccess.open(output+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"comparison_complete_visual_review_pending","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"route_sha256":FileAccess.get_sha256("res://runtime/entry_route.gd"),"probe_sha256":FileAccess.get_sha256("res://tests/probe_water_palette.gd"),"original_ambient":str(old_ambient),"original_distance_fog":str(old_distance_fog),"ambient_energy":world_environment.environment.ambient_light_energy,"water_bindings":diagnostics,"rows":rows,"scope":"Isolated runtime water/fog/ambient/reflection palette proposals. Nine independent/combined variants at exact current desktop/portrait camera poses and fixed shader timeline10; visible-water magenta controls; proposed reed camera captures labeled separately. Baked geometry/maps/source unchanged. No product adoption, phone, performance or final scene-art acceptance."}," ")+"\n");file.close();print("WATER_PALETTE_PROBE_RESULT ",rows.size()," originals");quit(0)
