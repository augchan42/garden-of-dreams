extends SceneTree
func _initialize() -> void:
 var kit_name="corridor" if "--corridor" in OS.get_cmdline_user_args() else "pavilion"
 var parts=["straight","corner","tee","stair"] if kit_name=="corridor" else ["roof_hex","roof_square","post","bracket","eave_strip","bench"]
 if "--wall" in OS.get_cmdline_user_args():
  kit_name="wall"
  parts=["bay","moon_gate","vase_gate","window_square","window_diamond","window_ice","window_hex","roof_cap"]
 if "--rockery" in OS.get_cmdline_user_args():
  kit_name="rockery"
  parts=["small","medium","large","arch","tunnel","cliff"]
 for part in parts:
  for suffix in ["","_LOD1"]:
   var kit=load("res://assets/kits/"+kit_name+"/KIT_"+kit_name+"_"+part+suffix+".glb").instantiate()
   var meshes=kit.find_children("*","MeshInstance3D",true,false)
   if meshes.size()!=1 or meshes[0].mesh.get_surface_count()!=1:
    push_error("Expected one render surface: "+part+suffix);quit(1);return
   var material=meshes[0].get_active_material(0) as StandardMaterial3D
   if material==null or material.albedo_texture==null or material.normal_texture==null or material.roughness_texture==null or material.metallic_texture==null:
    push_error("Missing PBR textures: "+part+suffix);quit(1);return
   for texture in [material.albedo_texture,material.normal_texture,material.roughness_texture,material.metallic_texture]:
    if texture.get_size()!=Vector2(2048,2048):
     push_error("Wrong atlas dimensions");quit(1);return
   if not material.normal_enabled:
    push_error("Normal texture disabled");quit(1);return
   kit.free()
 print("ARCHITECTURAL_ATLAS_IMPORT_PASS: ",kit_name," one surface per part, complete 2048 PBR bindings")
 quit(0)
