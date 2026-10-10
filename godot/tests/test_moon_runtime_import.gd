extends SceneTree

# Reject stale generated pixels even when the import sidecar declares a cap.
func _initialize() -> void:
 call_deferred("run")

func run() -> void:
 var output=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 var texture=load("res://assets/garden-of-dreams_moon-paint.png") as Texture2D
 var atlas=JSON.parse_string(FileAccess.get_file_as_string("res://tests/moon-paint-atlas.json"))
 if texture==null or not atlas is Dictionary or not atlas.has("png_sha256"):
  push_error("MOON_RUNTIME_IMPORT_REJECTED missing texture or source-paint contract")
  quit(1)
  return
 var record={"status":"running","source_glb_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams.glb"),"source_png_sha256":FileAccess.get_sha256("res://assets/garden-of-dreams_moon-paint.png"),"loaded_size":[texture.get_width(),texture.get_height()],"errors":[],"modes":[]}
 var image=texture.get_image()
 if texture.get_width()!=512 or texture.get_height()!=512:record.errors.append("Loaded moon exceeds the reviewed 512px footprint")
 if image==null or image.is_compressed():record.errors.append("Moon requires the reviewed lossless decoded resource")
 if image!=null:
  record.image_bytes=image.get_data_size()
  if record.image_bytes>1398100:record.errors.append("Moon mip allocation exceeds the 512px RGBA budget")
 if record.source_png_sha256!=atlas.png_sha256:record.errors.append("Original moon painting changed")
 for mode in ["normal","demo"]:
  var route=load("res://runtime/entry_route.tscn" if mode=="normal" else "res://runtime/first_reading_demo.tscn").instantiate()
  root.add_child(route)
  await process_frame
  var mesh=route.find_child("SITE_stage_MAT_painted_moon",true,false) as MeshInstance3D
  if mesh==null:record.errors.append(mode+": painted moon missing")
  else:
   var source=mesh.mesh.surface_get_material(0) as StandardMaterial3D
   var active=mesh.get_active_material(0) as ShaderMaterial
   if source==null or source.albedo_texture!=texture or source.emission_texture!=texture:record.errors.append(mode+": imported moon does not share the capped texture")
   if active==null or active.get_shader_parameter("albedo_texture")!=texture or active.get_shader_parameter("emission_texture")!=texture:record.errors.append(mode+": active moon lost shared paint/emission bindings")
   record.modes.append(mode)
  route.queue_free()
  await process_frame
 await create_timer(0.3).timeout
 record.status="passed" if record.errors.is_empty() else "failed"
 if not output.is_empty():FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(record," ")+"\n")
 if not record.errors.is_empty():push_error("MOON_RUNTIME_IMPORT_REJECTED "+JSON.stringify(record.errors))
 else:print("MOON_RUNTIME_IMPORT_PASS normal/demo originalpaint shared512px lossless")
 quit(0 if record.errors.is_empty() else 1)
