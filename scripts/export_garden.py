import bpy, bmesh, json, math, hashlib, collections
from pathlib import Path
from mathutils import Vector
R=Path('/Users/auchan/projects/garden-of-dreams')
s=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
bpy.context.window.scene=s
# Use Blender's dynamic export-format callback to query valid values.
import io_scene_gltf2
items=io_scene_gltf2.get_format_items(None,bpy.context)
fmt=next(i[0] for i in items if i[0]=='GLB')
report={'engine':'Godot','sites':{},'warnings':['Reference assets, not yet profiled on mobile.','Lightmap bake remains unfinished; engine import evidence is recorded separately in godot/import-validation.json.']}
def export_file(path):
 bpy.ops.export_scene.gltf(filepath=str(path),export_format=fmt,use_active_scene=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=True,export_lights=True,export_animations=False,export_draco_mesh_compression_enable=False,export_loglevel=-1)
# Batch static stock meshes by site and material; retain names of hero and trigger assets.
export_scene=bpy.data.scenes.new('Garden Godot export');bpy.context.window.scene=export_scene;export_scene.world=s.world
export_scene.render.resolution_x=s.render.resolution_x;export_scene.render.resolution_y=s.render.resolution_y
for source in list(s.collection.children):
 slug=source.name.removeprefix('SITE_');dest=bpy.data.collections.new('EXPORT_'+slug);export_scene.collection.children.link(dest)
 for obj in source.objects:
  if obj.name.startswith('CAM_rail_'):continue
  o=obj.copy()
  if obj.type in ['MESH','FONT']:o.data=obj.data.copy()
  dest.objects.link(o);o.hide_viewport=False;o.hide_render=False;o.hide_set(False)
  if obj.name.startswith('COL_'):o.name=obj.name+'-colonly';o['collision_only']=True
 groups=collections.defaultdict(list)
 for o in list(dest.objects):
  if o.type=='FONT':
   bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
  if o.type=='MESH' and not o.name.startswith(('COL_','HERO_')):
   mats=tuple(m.name for m in o.data.materials if m);groups[mats].append(o)
 for materials,objs in groups.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.select_set(True)
  bpy.context.view_layer.objects.active=objs[0]
  if len(objs)>1:bpy.ops.object.join()
  o=bpy.context.view_layer.objects.active;o.name='SITE_'+slug+'_'+('_'.join(materials) or 'geometry')
  if slug in ['rockery-gate','daguan-lou']:
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  # Secondary UVs allocated for engine bake. Smart projection has no overlaps per mesh.
  if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
  o.data.uv_layers.new(name='LightmapUV');o.data.uv_layers.active_index=len(o.data.uv_layers)-1
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(30) if slug in ["rockery-gate","daguan-lou"] else math.radians(66),island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 # Hero meshes also need a second UV channel for the Cycles lightmap pass.
 for o in dest.objects:
  if o.type=='MESH' and o.name.startswith('HERO_'):
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
   if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
   if len(o.data.uv_layers)<2:o.data.uv_layers.new(name='LightmapUV')
   o.data.uv_layers.active_index=1
   bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in dest.objects if o.type=='MESH' and not o.name.startswith('COL_'))
 # Export only this collection without altering the accumulated scene.
 bpy.ops.object.select_all(action='DESELECT')
 for o in dest.objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(R/'export/sites'/('SITE_'+slug+'.glb')),export_format=fmt,use_selection=True,use_active_scene=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=True,export_lights=True,export_animations=False,export_draco_mesh_compression_enable=False,export_loglevel=-1)
 report['sites'][slug]={'objects':len(dest.objects),'triangles':tris,'render_meshes':sum(o.type=='MESH' and not o.name.startswith('COL_') for o in dest.objects),'colliders':sum(o.name.startswith('COL_') for o in dest.objects),'triggers':sum(o.name.startswith('TRG_') for o in dest.objects)}
export_scene.camera=next(o for o in export_scene.objects if o.type=='CAMERA' and o.name.startswith('CAM_stage_wide'))
export_file(R/'export/garden-of-dreams.glb')
report['total_triangles']=sum(q['triangles'] for q in report['sites'].values());report['total_render_meshes']=sum(q['render_meshes'] for q in report['sites'].values())
(R/'export/manifest.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
