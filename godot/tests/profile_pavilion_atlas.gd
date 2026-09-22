extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
 var route=load("res://runtime/entry_route.tscn").instantiate();root.add_child(route)
 route.player.position=Vector3(0,.04,1.8);route._arrive("qinfang_ting",true)
 await create_timer(2).timeout
 await RenderingServer.frame_post_draw
 var mesh=route.find_child("SITE_qinfang-ting_MAT_pavilion_atlas*",true,false) as MeshInstance3D
 if mesh==null or mesh.mesh.get_surface_count()!=1:
  push_error("Pavilion should be one atlas batch");quit(1);return
 var mat=mesh.get_active_material(0) as StandardMaterial3D
 var report={"device":RenderingServer.get_video_adapter_name(),"pavilion_surfaces":1,"textures":{},"scope":"Desktop imported image data and whole-scene texture memory; not a phone measurement"}
 for key in ["albedo_texture","normal_texture","roughness_texture"]:
  var tex=mat.get(key) as Texture2D
  var img=tex.get_image()
  report.textures[key]={"width":img.get_width(),"height":img.get_height(),"compressed":img.is_compressed(),"data_bytes":img.get_data_size(),"mipmaps":img.has_mipmaps()}
 report["scene_texture_bytes"]=RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TEXTURE_MEM_USED)
 var label="compressed" if mat.albedo_texture.get_image().is_compressed() else "uncompressed"
 var file=FileAccess.open("res://pavilion-atlas-"+label+".json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "))
 root.get_texture().get_image().save_png("res://../docs/reference/pavilion-atlas-"+label+".png")
 print("PAVILION_ATLAS_PROFILE ",JSON.stringify(report))
 quit(0)
