extends Node

# Reserved capture layer includes only the hall and distant painted scenery.
# The pond and stage floor are excluded, preventing feedback and below-water occlusion.
const REFLECTION_LAYER = 1 << 19
const WATER_HEIGHT = -1.1
var viewport: SubViewport
var reflection_camera: Camera3D
var source_camera: Camera3D
var visitor: Node3D
var material: ShaderMaterial
var reflected_meshes = 0
var pond_meshes = 0

func _ready() -> void:
 RenderingServer.frame_pre_draw.connect(_sync_before_draw)

func _exit_tree() -> void:
 RenderingServer.frame_pre_draw.disconnect(_sync_before_draw)

func _sync_before_draw() -> void:
 # Camera tweens run after _process; synchronize once more before rendering.
 if is_processing(): update_reflection()

func configure(environment: Node3D, camera: Camera3D, target: Node3D) -> void:
 source_camera=camera
 visitor=target
 material=ShaderMaterial.new()
 material.shader=load("res://shaders/pond_reflection.gdshader")
 material.set_shader_parameter("wave_normal",load("res://materials/water-normal.png"))
 viewport=SubViewport.new()
 viewport.name="ReflectionCapture"
 viewport.size=Vector2i(768,327)
 viewport.world_3d=environment.get_world_3d()
 viewport.render_target_update_mode=SubViewport.UPDATE_DISABLED
 add_child(viewport)
 reflection_camera=Camera3D.new()
 reflection_camera.name="MirroredCamera"
 reflection_camera.cull_mask=REFLECTION_LAYER
 viewport.add_child(reflection_camera)
 reflection_camera.current=true
 material.set_shader_parameter("reflection_texture",viewport.get_texture())
 var nodes:Array[Node]=[environment]
 while not nodes.is_empty():
  var node=nodes.pop_back()
  nodes.append_array(node.get_children())
  if not node is MeshInstance3D:continue
  var is_pond=false
  for i in range(node.mesh.get_surface_count()):
   var original=node.mesh.surface_get_material(i)
   if original and original.resource_name=="MAT_aojing_water":
    node.set_surface_override_material(i,material)
    pond_meshes+=1
    is_pond=true
  var label=str(node.name)
  if not is_pond and (label.begins_with("SITE_aojing") or (label.begins_with("SITE_stage") and ("painted_mountain" in label or "cyclorama" in label or "painted_moon" in label))):
   node.layers |= REFLECTION_LAYER
   reflected_meshes+=1
 update_reflection()

func _process(_delta:float) -> void:
 update_reflection()

func mirrored(point:Vector3) -> Vector3:
 return Vector3(point.x,2.0*WATER_HEIGHT-point.y,point.z)

func update_reflection() -> void:
 if not is_instance_valid(source_camera):return
 var enabled=visitor.global_position.distance_to(Vector3(26,-.65,13.1))<18.0 and source_camera.global_position.y>WATER_HEIGHT
 viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS if enabled else SubViewport.UPDATE_DISABLED
 if not enabled:return
 var screen=source_camera.get_viewport().get_visible_rect().size
 var scale=minf(1.0,768.0/maxf(screen.x,screen.y))
 viewport.size=Vector2i(maxi(2,int(screen.x*scale)),maxi(2,int(screen.y*scale)))
 reflection_camera.fov=source_camera.fov
 reflection_camera.keep_aspect=source_camera.keep_aspect
 reflection_camera.near=source_camera.near
 reflection_camera.far=source_camera.far
 var original=source_camera.global_transform
 var eye=mirrored(original.origin)
 var target=mirrored(original.origin-original.basis.z)
 var up=original.basis.y
 up.y=-up.y
 reflection_camera.global_transform=Transform3D.IDENTITY.looking_at(target-eye,up)
 reflection_camera.global_position=eye
 var projection=reflection_camera.get_camera_projection()*Projection(reflection_camera.get_camera_transform().affine_inverse())
 material.set_shader_parameter("reflection_matrix",projection)
