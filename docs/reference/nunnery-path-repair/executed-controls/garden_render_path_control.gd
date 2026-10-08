extends SceneTree

var destination=""
var report={"status":"running","scope":"Native controlled paving-only lighting and cyan surface-ID comparison. Other geometry is flat gray; dynamic lights, grade, water animation and UI are absent. Not a full-scene art acceptance.","captures":[]}
func _initialize():call_deferred("run")
func run():
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):destination=arg.trim_prefix("--output=")
 assert(not destination.is_empty())
 assert(DisplayServer.get_name()!="headless")
 DirAccess.make_dir_recursive_absolute(destination)
 root.size=Vector2i(390,844)
 var camera=Camera3D.new()
 root.add_child(camera)
 camera.position=Vector3(-7,9.5,20)
 camera.look_at(Vector3(-23,.5,0))
 camera.fov=55
 camera.keep_aspect=Camera3D.KEEP_HEIGHT
 camera.current=true
 camera.far=250
 var helper=load("res://runtime/baked_materials.gd")
 for mode in ["before","after"]:
  var path="res://assets/"+mode+".glb"
  var metadata=JSON.parse_string(FileAccess.get_file_as_string("res://maps/"+mode+".json"))
  assert(metadata.source_glb_sha256==FileAccess.get_sha256(path),"Fresh map/source mismatch")
  var garden=load(path).instantiate()
  root.add_child(garden)
  var pending:Array[Node]=[garden]
  var floor:MeshInstance3D=null
  var source:BaseMaterial3D=null
  while not pending.is_empty():
   var node=pending.pop_back()
   pending.append_array(node.get_children())
   if node is Light3D:node.visible=false
   if node is MeshInstance3D:
    if node.name=="SITE_stage_MAT_plaster_rock":
     floor=node
     source=node.mesh.surface_get_material(0)
    else:
     var hide=false
     for index in range(node.mesh.get_surface_count()):
      var original=node.mesh.surface_get_material(index)
      if original is BaseMaterial3D and original.transparency==BaseMaterial3D.TRANSPARENCY_ALPHA:hide=true
     if hide:node.visible=false
     else:
      var flat=StandardMaterial3D.new()
      flat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
      flat.albedo_color=Color(.1,.1,.1)
      flat.cull_mode=BaseMaterial3D.CULL_DISABLED
      node.material_override=flat
  assert(floor!=null and source!=null)
  for treatment in ["surface-id","baked256","baked1024"]:
   if treatment=="surface-id":
    var id=StandardMaterial3D.new()
    id.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
    id.albedo_color=Color.CYAN
    id.cull_mode=BaseMaterial3D.CULL_DISABLED
    floor.material_override=id
   else:
    floor.material_override=null
    var material=helper.material_from_source(source)
    var texture:Texture2D
    if treatment=="baked256":texture=load("res://maps/"+mode+".png")
    else:texture=ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path("res://maps/"+mode+".png")))
    assert(texture.get_size()==(Vector2(256,256) if treatment=="baked256" else Vector2(1024,1024)))
    material.set_shader_parameter("lightmap",texture)
    material.set_shader_parameter("lightmap_scale",metadata.scale)
    material.set_shader_parameter("use_lightmap",true)
    floor.set_surface_override_material(0,material)
   for tick in range(12):await process_frame
   await RenderingServer.frame_post_draw
   var image=root.get_texture().get_image()
   var filename=mode+"-"+treatment+".png"
   assert(image.save_png(destination+"/"+filename)==OK)
   var samples=[]
   for point in [Vector2i(34,468),Vector2i(193,512),Vector2i(120,502)]:
    var col=image.get_pixelv(point)
    samples.append({"pixel":[point.x,point.y],"rgb":[col.r,col.g,col.b]})
   report.captures.append({"file":filename,"sha256":FileAccess.get_sha256(destination+"/"+filename),"source_glb_sha256":FileAccess.get_sha256(path),"lightmap_png_sha256":FileAccess.get_sha256("res://maps/"+mode+".png"),"samples":samples,"actual_size":[image.get_width(),image.get_height()]})
  garden.queue_free()
  for tick in range(3):await process_frame
 report.status="native_control_captures_complete_visual_review_pending"
 var file=FileAccess.open(destination+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify(report," ")+"\n")
 file.close()
 print("PATH_NATIVE_CONTROL_CAPTURE_PASS")
 quit(0)
