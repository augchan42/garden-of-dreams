extends SceneTree

func _initialize() -> void:call_deferred("run")

func check(value: bool, message: String) -> bool:
 if not value:
  push_error(message)
  quit(1)
 return value

func run() -> void:
 var factory=preload("res://runtime/baked_materials.gd")
 var image=Image.create(2,2,false,Image.FORMAT_RGBA8)
 image.fill(Color(.2,.5,.8,.6))
 var texture=ImageTexture.create_from_image(image)
 var standard=StandardMaterial3D.new()
 standard.roughness=.7
 standard.metallic=.6
 standard.metallic_specular=.35
 standard.roughness_texture=texture
 standard.roughness_texture_channel=BaseMaterial3D.TEXTURE_CHANNEL_GREEN
 standard.metallic_texture=texture
 standard.metallic_texture_channel=BaseMaterial3D.TEXTURE_CHANNEL_BLUE
 var adapted=factory.material_from_source(standard)
 if not check(adapted.get_shader_parameter("use_orm_texture")==true and adapted.get_shader_parameter("orm_texture")==texture,"Shared glTF G/B roughness/metallic map was dropped"):return
 if not check(is_equal_approx(adapted.get_shader_parameter("material_roughness"),.7) and is_equal_approx(adapted.get_shader_parameter("material_metallic"),.6),"Standard material factors changed"):return
 if not check(is_equal_approx(adapted.get_shader_parameter("material_specular"),.35),"Source specular factor was dropped"):return
 var masks=[Vector4(1,0,0,0),Vector4(0,1,0,0),Vector4(0,0,1,0),Vector4(0,0,0,1),Vector4(1.0/3.0,1.0/3.0,1.0/3.0,0)]
 for channel in range(5):
  standard.metallic_texture=null
  standard.roughness_texture_channel=channel
  adapted=factory.material_from_source(standard)
  if not check(adapted.get_shader_parameter("use_roughness_texture")==true and adapted.get_shader_parameter("roughness_texture")==texture,"Independent roughness texture was dropped"):return
  if not check(adapted.get_shader_parameter("roughness_channel_mask").is_equal_approx(masks[channel]),"Wrong roughness texture channel"):return
  standard.roughness_texture=null
  standard.metallic_texture=texture
  standard.metallic_texture_channel=channel
  adapted=factory.material_from_source(standard)
  if not check(adapted.get_shader_parameter("use_metallic_texture")==true and adapted.get_shader_parameter("metallic_texture")==texture,"Independent metallic texture was dropped"):return
  if not check(adapted.get_shader_parameter("metallic_channel_mask").is_equal_approx(masks[channel]),"Wrong metallic texture channel"):return
  standard.roughness_texture=texture
 var orm=ORMMaterial3D.new()
 orm.orm_texture=texture
 orm.roughness=.2
 orm.metallic=.3
 orm.metallic_specular=.12
 adapted=factory.material_from_source(orm)
 if not check(adapted.get_shader_parameter("material_roughness")==1.0 and adapted.get_shader_parameter("material_metallic")==1.0,"ORMMaterial3D channels incorrectly multiplied by hidden Standard factors"):return
 if not check(adapted.get_shader_parameter("material_specular")==.5,"ORMMaterial3D inherited hidden Standard specular factor"):return
 var scene=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(scene)
 var count=0
 for mesh in scene.find_children("*","MeshInstance3D",true,false):
  for surface in range(mesh.mesh.get_surface_count()):
   var source=mesh.mesh.surface_get_material(surface)
   var material=mesh.get_active_material(surface)
   if source is StandardMaterial3D and source.roughness_texture and material is ShaderMaterial and material.shader==load("res://shaders/baked_diffuse.gdshader"):
    if not check(material.get_shader_parameter("use_orm_texture")==true and material.get_shader_parameter("orm_texture")==source.roughness_texture,"Placed imported material lost its packed PBR map: "+str(mesh.name)):return
    count+=1
 if not check(count>=2,"Placed pavilion/wall roughness materials were not inspected"):return
 scene.queue_free()
 await create_timer(.2).timeout
 print("BAKED_PBR_TEXTURE_TRANSFER_PASS channels=5 placed=",count)
 quit(0)
