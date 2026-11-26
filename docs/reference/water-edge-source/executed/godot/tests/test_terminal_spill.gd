extends SceneTree

func _initialize():call_deferred("run")

func run():
 if not FileAccess.file_exists("res://lightmaps/terminal-spill-index.json"):
  push_error("Missing native terminal window-spill catalog")
  quit(1)
  return
 var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/terminal-spill-index.json"))
 assert(records is Dictionary and records.size()==7)
 var route=load("res://runtime/entry_route.tscn").instantiate()
 route.demo_mode="--demo" in OS.get_cmdline_user_args()
 root.add_child(route)
 await process_frame
 var count=0
 for mesh in route.find_children("*","MeshInstance3D",true,false):
  for surface in range(mesh.mesh.get_surface_count()):
   var material=mesh.get_active_material(surface)
   if not material is ShaderMaterial or material.shader!=load("res://shaders/baked_diffuse.gdshader"):continue
   var enabled=material.get_shader_parameter("use_terminal_spill")
   assert((enabled==true)==records.has(str(mesh.name)),"Spill missing or leaked: "+str(mesh.name))
   if not enabled:continue
   var record=records[str(mesh.name)]
   var texture=material.get_shader_parameter("terminal_spill") as Texture2D
   assert(texture!=null and texture.get_width()<=256)
   assert(material.get_shader_parameter("use_lightmap"),"Ordinary bake lost")
   assert(not material.get_shader_parameter("use_backdrop_wash"),"Direct backdrop wash entered a cell")
   assert(is_equal_approx(material.get_shader_parameter("terminal_spill_scale"),float(record.scale)))
   assert(record.pass_filter==["INDIRECT"] and not record.adaptive_sampling)
   assert(record.samples>=2048 and record.lights_baked==12)
   assert(not record.point_lights_baked and not record.emissive_geometry_baked)
   assert((mesh.layers&1)==0 and (mesh.layers&2)!=0)
   count+=1
 assert(count==7)
 var manifest=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/terminal-spill/manifest.json"))
 for cell in manifest.controls.window_only:assert(float(cell.linear_max)>1e-9)
 for name in ["direct","sealed","washes_off"]:
  for cell in manifest.controls[name]:assert(float(cell.linear_max)<=1e-7)
 print("TERMINAL_SPILL_PASS: seven indirect receivers, six window controls, base bakes retained, no direct wash")
 if route.demo_audio:
  for player in route.demo_audio.players.values():player.stop()
 await create_timer(.2).timeout
 route.queue_free()
 await create_timer(.2).timeout
 quit(0)
