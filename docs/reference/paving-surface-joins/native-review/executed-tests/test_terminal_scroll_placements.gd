extends SceneTree
func _initialize() -> void:
 create_timer(15).timeout.connect(func():push_error("Terminal scroll check timed out");quit(1))
 call_deferred("run")
func run() -> void:
 var garden=(load("res://assets/garden-of-dreams.glb") as PackedScene).instantiate() as Node3D;root.add_child(garden)
 var batch=garden.find_child("SITE_terminal-cells_MAT_terminal_scroll",true,false) as MeshInstance3D
 assert(batch!=null and batch.mesh.get_surface_count()==1)
 var material=batch.get_active_material(0) as ORMMaterial3D
 assert(material.albedo_color==Color(.025,.025,.025,1))
 var base=load("res://materials/props_atlas.tres") as ORMMaterial3D
 assert(material.albedo_texture==base.albedo_texture and material.orm_texture==base.orm_texture and material.emission_texture==base.emission_texture)
 var emission=material.emission_texture.get_image()
 if emission.is_compressed():assert(emission.decompress()==OK)
 var arrays=batch.mesh.surface_get_arrays(0);var vertices=arrays[Mesh.ARRAY_VERTEX];var uvs=arrays[Mesh.ARRAY_TEX_UV]
 var centres=[-6.5,-3.9,-1.3,1.3,3.9,6.5];var counts=[0,0,0,0,0,0]
 for i in range(vertices.size()):
  var p=batch.global_transform*vertices[i]
  if p.z<35.85 or p.z>35.95 or p.y<.9:continue
  var cell=-1
  for j in range(centres.size()):
   if p.x>centres[j]+.65 and p.x<centres[j]+1.15:cell=j;break
  assert(cell>=0,"Scroll vertex lies outside a solid wall strip: "+str(p))
  assert(p.y<=2.10,"Scroll crosses the window head")
  counts[cell]+=1
  var texel=Vector2i(clampi(int(uvs[i].x*emission.get_width()),0,emission.get_width()-1),clampi(int(uvs[i].y*emission.get_height()),0,emission.get_height()-1))
  var glow=emission.get_pixelv(texel)
  assert(maxf(glow.r,maxf(glow.g,glow.b))<.02,"A scroll surface emits light")
 for count in counts:assert(count>100,"Missing terminal wall scroll")
 assert(garden.find_children("*scroll*","Light3D",true,false).is_empty())
 await physics_frame;await physics_frame
 var space=garden.get_world_3d().direct_space_state
 for x in centres:
  var opening=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x+.1,1.7,36.3),Vector3(x+.1,1.7,35.3)))
  assert(opening.is_empty(),"Barred window opening is blocked")
 print("TERMINAL_SCROLLS_PASS: six wall-mounted scrolls, zero emission, clear barred windows, no added lights")
 garden.queue_free();quit(0)
