from pathlib import Path
import json, shutil
root=Path('/Users/auchan/projects/garden-of-dreams')
fixture=Path(json.loads(Path('/tmp/garden-oux-camera-review.json').read_text())['folder'])
code='''extends SceneTree

var report = {"status":"running", "views":[], "failures":[], "scope":"Native camera projection and captures on the complete installed source; route interactions and devices are separate checks."}
var destination = ""

func _initialize() -> void:
 call_deferred("run")

func xyz(v: Vector3) -> Array:
 return [v.x,v.y,v.z]

func run() -> void:
 for argument in OS.get_cmdline_user_args():
  if argument.begins_with("--output="):destination=argument.trim_prefix("--output=")
 if destination.is_empty() or DisplayServer.get_name()=="headless":
  push_error("Ouxiang framing requires a native renderer and --output directory")
  quit(1)
  return
 DirAccess.make_dir_recursive_absolute(destination)
 create_timer(120).timeout.connect(func():push_error("Ouxiang framing timed out");quit(1))
 var route=load("res://runtime/entry_route.tscn").instantiate()
 root.add_child(route)
 for frame in range(12):await process_frame
 route.player.position=Vector3(-23,.04,0)
 var roof=route.find_child("SITE_ouxiang-xie_MAT_rooftile",true,false) as MeshInstance3D
 if roof==null:
  push_error("Ouxiang roof mesh missing")
  quit(1)
  return
 for resolution in [Vector2i(390,844),Vector2i(360,800),Vector2i(1410,600)]:
  root.size=resolution
  route._configure_ui_scale(false,160)
  for frame in range(12):await process_frame
  var poses={}
  for room in route.ROOMS:
   route._arrive(room,true)
   poses[room]={"position":xyz(route.camera.position),"basis":[xyz(route.camera.basis.x),xyz(route.camera.basis.y),xyz(route.camera.basis.z)],"fov":route.camera.fov,"keep_aspect":route.camera.keep_aspect}
  route._arrive("ouxiang_xie",true)
  for frame in range(12):await process_frame
  var minimum=Vector2(INF,INF)
  var maximum=Vector2(-INF,-INF)
  var behind=0
  var vertices=0
  for surface in range(roof.mesh.get_surface_count()):
   for local in roof.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]:
    var world=roof.global_transform*local
    if route.camera.is_position_behind(world):behind+=1
    var pixel=route.camera.unproject_position(world)
    minimum=minimum.min(pixel)
    maximum=maximum.max(pixel)
    vertices+=1
  var panel=route.command_panel.get_global_rect()
  var status_rect=route.status.get_global_rect()
  # This point lies at the centre of the saved near-side stone pier.
  var pier=route.camera.unproject_position(Vector3(-25.55,-.5,2.05))
  var visible=root.get_visible_rect().size
  var row={"requested_size":[resolution.x,resolution.y],"viewport":[visible.x,visible.y],"poses":poses,"roof_min":[minimum.x,minimum.y],"roof_max":[maximum.x,maximum.y],"roof_vertices":vertices,"behind_camera":behind,"panel_top":panel.position.y,"status_bottom":status_rect.end.y,"near_pier":[pier.x,pier.y]}
  var before=route.camera.transform
  route.execute_command("tea")
  var tea_ok=not route.travelling and route.room_id=="ouxiang_xie" and "not connected" in route.output_label.text and route.camera.transform.is_equal_approx(before)
  route.execute_command("look")
  var look_ok=route.output_label.text==route.ROOMS["ouxiang_xie"].text and route.camera.transform.is_equal_approx(before)
  row["tea_and_look_preserve_view"]=tea_ok and look_ok
  for frame in range(12):await process_frame
  await RenderingServer.frame_post_draw
  var image_path=destination+"/ouxiang-%dx%d.png"%[resolution.x,resolution.y]
  var error=root.get_texture().get_image().save_png(image_path)
  row["capture"]=image_path
  if error!=OK:report.failures.append("Capture failed: "+str(error))
  if not tea_ok or not look_ok:report.failures.append("Tea/look changed camera or room")
  if behind>0:report.failures.append("Roof behind camera")
  if resolution.x<resolution.y:
   if minimum.x<8 or maximum.x>visible.x-8:report.failures.append("Portrait roof clipped horizontally at "+str(resolution))
   if minimum.y<status_rect.end.y+8 or maximum.y>panel.position.y-8:report.failures.append("Portrait roof intersects interface at "+str(resolution))
   if pier.x<8 or pier.x>visible.x-8 or pier.y<status_rect.end.y+8 or pier.y>panel.position.y-8:report.failures.append("Near-side pier hidden by interface at "+str(resolution))
  report.views.append(row)
 report.status="passed" if report.failures.is_empty() else "failed"
 var file=FileAccess.open(destination+"/report.json",FileAccess.WRITE)
 file.store_string(JSON.stringify(report," ")+"\\n")
 file.close()
 if not report.failures.is_empty():
  print("OUXIANG_FRAMING_REJECTED: ",report.failures)
  quit(1)
 else:
  print("OUXIANG_FRAMING_PASS: two portrait sizes, desktop capture, roof/pier projection and tea/look")
  quit(0)
'''
path=root/'godot/tests/test_oux_portrait_framing.gd'
path.write_text(code)
shutil.copy2(path,fixture/'godot/tests'/path.name)
