extends SceneTree

var destination=""
var report={"status":"running","scope":"Material base-color preview on the complete current lighting. Bakes, geometry, lighting, grade, cameras and UI are retained; indirect color has not been rebaked. A new saved source and matching fresh bakes are required before adoption.","source_glb_sha256":"","captures":[],"changed_surfaces":[]}
var palette={"MAT_lattice_wood":Color(.085,.045,.022),"MAT_whitewash":Color(.36,.335,.29),"MAT_rooftile":Color(.045,.055,.065),"MAT_plaster_rock":Color(.21,.205,.19)}
func _initialize():call_deferred("run")
func run():
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):destination=arg.trim_prefix("--output=")
 assert(not destination.is_empty() and DisplayServer.get_name()!="headless")
 DirAccess.make_dir_recursive_absolute(destination)
 report.source_glb_sha256=FileAccess.get_sha256("res://assets/garden-of-dreams.glb")
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 for frame in range(12):await process_frame
 var nodes:Array[Node]=[route]
 var targets=[]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if not node is MeshInstance3D:continue
  for index in range(node.mesh.get_surface_count()):
   var source=node.mesh.surface_get_material(index)
   var active=node.get_active_material(index)
   if active is ShaderMaterial:
    for uniform in active.shader.get_shader_uniform_list():
     if uniform.name=="timeline_time":active.set_shader_parameter("timeline_time",3.0)
   if source is BaseMaterial3D and source.resource_name in palette:
    assert(active is ShaderMaterial and active.shader==load("res://shaders/baked_diffuse.gdshader"),"Unexpected common-material renderer")
    var original=active.get_shader_parameter("base_color")
    # Godot's glTF base colors are display values; source-color shader uniforms
    # convert them to linear light. Check that representation before previewing.
    var linear_originals={"MAT_lattice_wood":Color(.045,.07,.025),"MAT_whitewash":Color(.3,.39,.23),"MAT_rooftile":Color(.025,.06,.035),"MAT_plaster_rock":Color(.15,.24,.12)}
    var expected:Color=linear_originals[source.resource_name].linear_to_srgb()
    assert(original.is_equal_approx(expected),"Unexpected imported color representation")
    var replacement=active.duplicate()
    replacement.set_shader_parameter("base_color",palette[source.resource_name].linear_to_srgb())
    targets.append({"node":node,"index":index,"old":active,"new":replacement})
    report.changed_surfaces.append({"node":str(node.name),"surface":index,"material":source.resource_name,"old_display_color":[original.r,original.g,original.b],"new_linear_color":[palette[source.resource_name].r,palette[source.resource_name].g,palette[source.resource_name].b]})
 assert(targets.size()>20)
 for size in [Vector2i(1410,600),Vector2i(390,844)]:
  root.size=size
  route._configure_ui_scale(false,160)
  for frame in range(12):await process_frame
  for treatment in ["baseline","neutral"]:
   for row in targets:row.node.set_surface_override_material(row.index,row.old if treatment=="baseline" else row.new)
   for room in ["qinfang_ting","ouxiang_xie","qiushuang_zhai","hengwu_yuan"]:
    route._arrive(room,true)
    for frame in range(12):await process_frame
    await RenderingServer.frame_post_draw
    var image=root.get_texture().get_image()
    var filename="%s-%s-%dx%d.png"%[treatment,room,size.x,size.y]
    assert(image.save_png(destination+"/"+filename)==OK)
    report.captures.append({"file":filename,"sha256":FileAccess.get_sha256(destination+"/"+filename),"actual_size":[image.get_width(),image.get_height()]})
 report.status="preview_captures_complete_visual_review_pending"
 var file=FileAccess.open(destination+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify(report," ")+"\n")
 file.close()
 print("NEUTRAL_MATERIAL_PREVIEW_PASS ",targets.size())
 quit(0)
