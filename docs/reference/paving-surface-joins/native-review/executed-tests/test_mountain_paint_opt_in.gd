extends SceneTree

# A preceding unpainted scene must not accidentally receive a texture whose
# band UVs it does not have. Run with an explicit preceding-source fixture.
func _initialize():
 create_timer(20).timeout.connect(func():push_error("Mountain opt-in check timed out");quit(1))
 call_deferred("run")

func run():
 var args=OS.get_cmdline_user_args()
 assert(args.size()==1)
 var scene=load(args[0]).instantiate()
 var old_emission=[Color(.0108,.0288,.0114),Color(.0156,.0402,.0156),Color(.0204,.0516,.0198)]
 for index in range(3):
  var node=scene.find_child("SITE_stage_MAT_painted_mountains_"+str(index),true,false) as MeshInstance3D
  assert(node!=null)
  var extras=node.get_meta("extras",{})
  assert(not extras.has("paint_source"))
  var material=node.get_active_material(0) as StandardMaterial3D
  assert(material!=null and material.albedo_texture==null and material.emission_texture==null)
  # Godot material colors are sRGB properties; glTF factors are linear.
  var emitted=material.emission.srgb_to_linear()*material.emission_energy_multiplier
  assert(abs(emitted.r-old_emission[index].r)<.000001)
  assert(abs(emitted.g-old_emission[index].g)<.000001)
  assert(abs(emitted.b-old_emission[index].b)<.000001)
 scene.free()
 print("MOUNTAIN_PAINT_OPT_IN_PASS: preceding bare materials retain original emission and no paint override")
 quit()
