extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var output=""
 var baseline="--baseline" in OS.get_cmdline_user_args()
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 var record={"status":"running","baseline":baseline,"source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"textures":{},"errors":[],"modes":[]}
 var loaded={}
 var corrupted=false
 for name in ["pavilion_basecolor","wall_basecolor","gate-inscription","gate-inscription-normal"]:
  var path="res://assets/garden-of-dreams_"+name+".png"
  var texture=load(path) as Texture2D
  if texture==null:
   record.errors.append("Missing texture "+name)
   continue
  loaded[name]=texture
  var image=texture.get_image()
  var width=(2048 if baseline else 1024) if "basecolor" in name else (1024 if baseline else 512)
  var wanted_height=width if "basecolor" in name else int(width/3)
  if texture.get_width()!=width or texture.get_height()!=wanted_height:record.errors.append("Actual loaded size differs: "+name)
  if image==null or not image.has_mipmaps():record.errors.append("Missing mip image: "+name)
  if image==null:continue
  if not "basecolor" in name and image.is_compressed():record.errors.append("Inscription lost lossless pixels: "+name)
  var stored=Image.create_empty(texture.get_width(),texture.get_height(),image.has_mipmaps(),texture.get_format()).get_data_size()
  record.textures[name]={"loaded_size":[texture.get_width(),texture.get_height()],"stored_format":texture.get_format(),"stored_mip_bytes":stored,"readback_bytes":image.get_data_size(),"mipmaps":image.has_mipmaps(),"source_sha256":FileAccess.get_sha256(path),"import_sha256":FileAccess.get_sha256(path+".import"),"bindings":{}}
 for mode in ["normal","demo"]:
  var route=load("res://runtime/entry_route.tscn" if mode=="normal" else "res://runtime/first_reading_demo.tscn").instantiate()
  root.add_child(route)
  await process_frame
  for name in loaded:
   var count=0
   var texture=loaded[name]
   for mesh in route.find_children("*","MeshInstance3D",true,false):
    for surface in range(mesh.mesh.get_surface_count()):
     var original=mesh.mesh.surface_get_material(surface)
     if not corrupted and "--corrupt-active" in OS.get_cmdline_user_args() and original is StandardMaterial3D and original.albedo_texture==loaded.pavilion_basecolor:
      mesh.set_surface_override_material(surface,StandardMaterial3D.new())
      corrupted=true
     var active=mesh.get_active_material(surface)
     var field="normal_texture" if name=="gate-inscription-normal" else "albedo_texture"
     if original is StandardMaterial3D and original.get(field)==texture:
      count+=1
      if active is ShaderMaterial:
       if active.get_shader_parameter(field)!=texture:record.errors.append(mode+": active shader binding differs "+name)
      elif active is StandardMaterial3D:
       if active.get(field)!=texture:record.errors.append(mode+": active standard binding differs "+name)
      else:record.errors.append(mode+": unexpected active material type "+name)
   record.textures[name].bindings[mode]=count
   if count==0:record.errors.append(mode+": no actual imported bindings "+name)
  record.modes.append(mode)
  route.queue_free()
  await process_frame
 record.status="passed" if record.errors.is_empty() else "failed"
 FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(record," ")+"\n")
 await create_timer(.2).timeout
 if not record.errors.is_empty():push_error("MEMORY_CAP_RESOURCE_REJECTED "+JSON.stringify(record.errors))
 else:print("MEMORY_CAP_RESOURCE_PASS baseline=",baseline)
 quit(0 if record.errors.is_empty() else 1)
