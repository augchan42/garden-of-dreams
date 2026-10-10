extends "res://tests/full_profile_base.gd"

# Read actual Android resources before the unchanged timed tour starts.
func run() -> void:
 if not OS.has_feature("android") or not OS.has_feature("garden_profile"):
  push_error("CAP_PREFLIGHT_REJECTED requires dedicated actual Android export")
  return
 var proof={"status":"running","scope":"Actual Android loaded cap resources before timed frames; no extra scene or lighting changes.","build_sha256":FileAccess.get_sha256("res://phone-profile-build.json"),"device_model":OS.get_model_name(),"renderer_device":RenderingServer.get_video_adapter_name(),"textures":{},"errors":[]}
 for name in ["pavilion_basecolor","wall_basecolor","gate-inscription","gate-inscription-normal","moon-paint"]:
  var texture=load("res://assets/garden-of-dreams_"+name+".png") as Texture2D
  if texture==null:
   proof.errors.append("Missing actual texture "+name)
   continue
  var wanted=Vector2(1024,1024) if "basecolor" in name else Vector2(512,512) if name=="moon-paint" else Vector2(512,170)
  var image=texture.get_image()
  if texture.get_size()!=wanted:proof.errors.append("Actual loaded size differs "+name)
  if image==null or not image.has_mipmaps():
   proof.errors.append("Missing mip data "+name)
   continue
  var format=texture.get_format()
  var stored_bytes=Image.create_empty(texture.get_width(),texture.get_height(),true,format).get_data_size()
  if "basecolor" in name:
   if stored_bytes>700000:proof.errors.append("Compressed cap footprint differs "+name)
  elif name=="gate-inscription":
   if format!=Image.FORMAT_RGBA8 or stored_bytes!=463772:proof.errors.append("Lossless color allocation differs "+name)
  elif name=="gate-inscription-normal":
   if format!=Image.FORMAT_RGB8 or stored_bytes!=347829:proof.errors.append("Lossless normal allocation differs "+name)
  elif format!=Image.FORMAT_RGB8 or stored_bytes!=1048575:proof.errors.append("Lossless moon allocation differs")
  proof.textures[name]={"size":[texture.get_width(),texture.get_height()],"stored_format":format,"stored_mip_bytes":stored_bytes,"readback_bytes":image.get_data_size(),"mipmaps":image.has_mipmaps()}
 proof.status="passed" if proof.errors.is_empty() else "failed"
 var error=preload("res://tests/profile_report_store.gd").publish("user://garden-cap-resources.json",proof)
 if error!=OK or not proof.errors.is_empty():
  push_error("CAP_PREFLIGHT_REJECTED "+JSON.stringify(proof.errors)+" publication="+error_string(error))
  return
 await super.run()
