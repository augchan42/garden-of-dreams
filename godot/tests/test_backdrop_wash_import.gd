extends SceneTree

func _initialize():call_deferred("run")

func run():
 var reject="--expect-rejection" in OS.get_cmdline_user_args()
 var output=""
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 var texture=load("res://lightmaps/backdrop-wash/SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas-front.png") as CompressedTexture2D
 assert(texture!=null)
 var report={"errors":[],"expect_rejection":reject,"loaded_size":[texture.get_width(),texture.get_height()],"stored_format":texture.get_format(),"source_sha256":FileAccess.get_sha256("res://lightmaps/backdrop-wash/SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas-front.png"),"modes":[]}
 for mode in ["normal","demo"]:
  var garden=load("res://garden_preview.tscn").instantiate()
  root.add_child(garden)
  preload("res://runtime/backdrop_wash.gd").configure(garden)
  var records=JSON.parse_string(FileAccess.get_file_as_string("res://lightmaps/"+("full-index.json" if mode=="normal" else "demo-index.json")))
  assert(preload("res://runtime/baked_materials.gd").apply_to_scene(garden,records)==records.size())
  var applied=preload("res://runtime/backdrop_wash.gd").apply_baked(garden)
  if reject:
   if applied!=-1:report.errors.append(mode+": incompatible wash resource accepted")
  else:
   if applied!=6:report.errors.append(mode+": six wash receivers not applied")
   if report.loaded_size!=[256,256] or texture.get_format()!=Image.FORMAT_RGB8:report.errors.append(mode+": actual wash resource is not lossless256 RGB")
   var mesh=garden.find_child("SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas",true,false) as MeshInstance3D
   var surfaces=0
   for surface in range(mesh.mesh.get_surface_count()):
    var material=mesh.get_active_material(surface) as ShaderMaterial
    if material==null or material.get_shader_parameter("use_backdrop_wash")!=true or material.get_shader_parameter("backdrop_wash")!=texture or material.get_shader_parameter("backdrop_wash_back")!=texture:
     report.errors.append(mode+": active wash binding differs")
    surfaces+=1
   if surfaces!=2:report.errors.append(mode+": painted front and sealed back missing")
  report.modes.append({"mode":mode,"applied":applied})
  garden.queue_free()
  await process_frame
 report.status="passed" if report.errors.is_empty() else "failed"
 if not output.is_empty():FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report," ")+"\n")
 if report.errors.is_empty():print("BACKDROP_WASH_IMPORT_PASS ",report.modes)
 else:push_error("BACKDROP_WASH_IMPORT_REJECTED ",report.errors)
 quit(0 if report.errors.is_empty() else 1)
