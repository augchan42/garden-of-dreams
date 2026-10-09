from pathlib import Path
import json,hashlib,shutil
r=Path('/Users/auchan/projects/garden-of-dreams');p=Path(json.loads(Path('/tmp/garden-ziling-framing.json').read_text())['folder']);sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
for n in ['runtime/entry_route.gd','garden_preview.tscn','materials/water.tres','shaders/pond_reflection.gdshader']:
 shutil.copyfile(r/'godot'/n,p/'godot'/n);assert sha(r/'godot'/n)==sha(p/'godot'/n)
s=(r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-framing-comparison/third-executed-probe.gd').read_text()
s=s.replace('create_timer(150)','create_timer(180)')
s=s.replace('subjects.bridge=vertices(route.find_child("SITE_ziling-zhou_MAT_pavilion_atlas",true,false))','subjects.bridge=vertices(route.find_child("SITE_ziling-zhou_MAT_pavilion_atlas",true,false))\n subjects.pavilion_roof=vertices(route.find_child("SITE_ouxiang-xie_MAT_rooftile",true,false))')
s=s.replace('route.player.position=Vector3(-35.4,.03,0)','''route.player.position=Vector3(-35.4,.03,0)
 for node in route.find_children("*","MeshInstance3D",true,false):
  for i in range(node.mesh.get_surface_count()):
   var active=node.get_active_material(i)
   if active is ShaderMaterial and active.shader.resource_path in ["res://shaders/water.gdshader","res://shaders/floor_fog.gdshader"]:active.set_shader_parameter("timeline_time",10.0)
 route.get_node("PondReflection").material.set_shader_parameter("timeline_time",10.0)''')
start=s.index('   for position in [');end=s.index('   if best.is_empty():',start)
s=s[:start]+'''   for position in [Vector3(-40,3.2,6),Vector3(-41,3.2,6),Vector3(-42,3.2,7),Vector3(-43,3.2,8),Vector3(-44,3.2,9),Vector3(-45,3.2,10),Vector3(-40,4.2,6),Vector3(-42,4.2,8),Vector3(-44,4.2,10),Vector3(-42,5.2,8),Vector3(-44,5.2,10),Vector3(-46,4.2,12)]:
    for x in [-33.0,-32.0,-31.0,-30.0,-29.0,-28.0]:
     for y in [-6.0,-5.0,-4.0,-3.0,-2.0,-1.0,0.0]:
      for fov in [50.0,55.0,60.0,65.0,70.0,75.0]:
       var target:=Vector3(x,y,0)
       route.camera.keep_aspect=Camera3D.KEEP_WIDTH;route.camera.fov=fov;route._camera_to(position,target,true)
       var island:=measure(bounds.island);var bridge:=measure(bounds.bridge);var reeds:=measure(bounds.reeds);var roof:=measure(bounds.pavilion_roof)
       # Search uses conservative boxes; final originals measure full actual vertices.
       if island.fits and bridge.fits and reeds.fits and roof.fits and roof.high[1]<island.low[1]-8:
        var value:float=island.width_fraction+.4*(island.high[1]-island.low[1])/root.get_visible_rect().size.y+.3*(reeds.high[1]-reeds.low[1])/root.get_visible_rect().size.y+.12*roof.width_fraction
        if value>score:score=value;best={"position":[position.x,position.y,position.z],"target":[target.x,target.y,target.z],"fov":fov}
''' +s[end:]
s=s.replace('res://tests/compare_ziling.gd','res://tests/compare_ziling_roof.gd').replace('Candidate projection does not prove occlusion or final art','Entire Ouxiang roof also required with a vertical gap above the island. Actual installed neutral palette and attached fixed clocks. Candidate projection does not prove occlusion or final art')
(p/'godot/tests/compare_ziling_roof.gd').write_text(s)
folder=p/'roof-comparison';assert not folder.exists();folder.mkdir()
cmd=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(p/'godot'),'--windowed','--resolution','390x844','--script','res://tests/compare_ziling_roof.gd','--','--output='+str(folder)]
(p/'roof-command.json').write_text(json.dumps({'status':'prepared','command':cmd,'source_glb_sha256':sha(p/'godot/assets/garden-of-dreams.glb'),'route_sha256':sha(p/'godot/runtime/entry_route.gd'),'probe_sha256':sha(p/'godot/tests/compare_ziling_roof.gd')},indent=2)+'\n')
print('ZILING_ROOF_PROBE_PREPARED',p)
