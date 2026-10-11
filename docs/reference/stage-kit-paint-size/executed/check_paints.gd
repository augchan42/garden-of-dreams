extends SceneTree
var rows:Array=[]
func _initialize()->void:
 call_deferred("run")
func run()->void:
 for mode in ["baseline","candidate"]:
  for name in ["moonlit","dusk","mist"]:
   var scene:Node3D=(load("res://assets/%s-%s.glb"%[mode,name]) as PackedScene).instantiate()
   var mesh:=scene.find_child("*render*",true,false) as MeshInstance3D
   assert(mesh!=null)
   var material:=mesh.get_active_material(0) as StandardMaterial3D
   assert(material!=null and material.albedo_texture!=null and material.emission_texture!=null)
   var expected:int=4096 if mode=="baseline" else 2048
   assert(material.albedo_texture.get_width()==expected and material.albedo_texture.get_height()==expected)
   assert(material.emission_texture==material.albedo_texture)
   rows.append({"mode":mode,"name":name,"width":material.albedo_texture.get_width(),"height":material.albedo_texture.get_height(),"triangles":mesh.mesh.surface_get_arrays(0)[Mesh.ARRAY_INDEX].size()/3})
   scene.free()
 var file:=FileAccess.open("res://../raw-native-textures.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"status":"passed","paint_bindings":rows},"  ")+"\n")
 print("STAGE_RAW_NATIVE_PAINT_PASS ",rows.size())
 quit(0)
