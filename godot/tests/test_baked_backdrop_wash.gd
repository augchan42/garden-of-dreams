extends SceneTree

func _initialize():call_deferred("run")

func run():
 var reference=load("res://garden_preview.tscn").instantiate()
 var route=load("res://runtime/entry_route.tscn").instantiate()
 route.demo_mode="--demo" in OS.get_cmdline_user_args()
 root.add_child(route)
 await process_frame
 if route.find_child("BackdropWash",true,false)!=null:
  push_error("Production backdrop wash still uses a realtime light")
  quit(1)
  return
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/backdrop-wash-index.json"))
 if not records is Dictionary or records.size()!=5:
  push_error("Missing native Area-light bakes for the five backdrop receivers")
  quit(1)
  return
 for name in records:
  if records[name].get("lights_baked",0)!=12 or records[name].get("site_blend_sha256",{}).size()!=12:
   push_error("Backdrop maps omit required exterior site washes")
   reference.free()
   route.free()
   quit(1)
   return
  var mesh=route.find_child(name,true,false) as MeshInstance3D
  if mesh==null:
   push_error("Missing painted wash receiver: "+name)
   quit(1)
   return
  for surface in range(mesh.mesh.get_surface_count()):
   var material=mesh.get_active_material(surface) as ShaderMaterial
   if material==null or not material.get_shader_parameter("use_backdrop_wash"):
    push_error("Wash bake is not applied: "+name)
    quit(1)
    return
   var texture=material.get_shader_parameter("backdrop_wash") as Texture2D
   if texture==null or texture.get_width()>256:
    push_error("Missing or oversized wash bake: "+name)
    quit(1)
    return
   if records[name].double_sided:
    var back=material.get_shader_parameter("backdrop_wash_back") as Texture2D
    if not material.get_shader_parameter("backdrop_wash_double_sided") or back==null or back.get_width()>256:
     push_error("Back-face native wash is missing: "+name)
     quit(1)
     return
   if "cyclorama" in name:
    var original=reference.find_child(name,true,false).get_active_material(surface) as BaseMaterial3D
    if material.get_shader_parameter("source_unshaded")!=(original.shading_mode==BaseMaterial3D.SHADING_MODE_UNSHADED):
     push_error("Painted sky lost its unshaded base")
     quit(1)
     return
   elif not material.get_shader_parameter("use_lightmap") or material.get_shader_parameter("lightmap")==null:
    push_error("Ordinary stage lighting was lost when adding the wash: "+name)
    quit(1)
    return
  if (mesh.layers&1)!=0:
   push_error("Static keys would double-light the baked backdrop: "+name)
   quit(1)
   return
 for mesh in route.find_children("*","MeshInstance3D",true,false):
  if records.has(str(mesh.name)):continue
  for surface in range(mesh.mesh.get_surface_count()):
   var material=mesh.get_active_material(surface)
   if material is ShaderMaterial and material.shader==load("res://shaders/baked_diffuse.gdshader"):
    if material.get_shader_parameter("use_backdrop_wash"):
     push_error("Backdrop wash leaked onto a building or floor: "+str(mesh.name))
     quit(1)
     return
 print("BAKED_BACKDROP_WASH_PASS: five Area-light maps, no realtime wash, no building receivers")
 if route.demo_audio:
  for player in route.demo_audio.players.values():player.stop()
 await create_timer(.2).timeout
 route.queue_free()
 reference.free()
 await create_timer(.2).timeout
 quit()
