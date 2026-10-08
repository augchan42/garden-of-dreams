import bpy,pathlib,json,sys,collections
from mathutils import Vector
root=pathlib.Path('/Users/auchan/projects/garden-of-dreams');sys.path.insert(0,str(root/'scripts'))
from pavilion_roof_geometry import components
w=pathlib.Path(json.load(open('/tmp/garden-tile-ridge-candidate.json'))['folder']);results=[]
for source in [root/'blender/authoring.blend',w/'blender/authoring.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(source));scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));bpy.context.window.scene=scene;bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();roof=bpy.data.objects['QINFANG_kit_roof_hex']
 ridges=[faces for vertices,faces in components(roof.data) if len(vertices)==15 and len(faces)==8];faces=[p for fs in ridges for p in fs];record={'source':str(source),'tile_faces':len(faces),'suns':{}}
 for light in [o for o in scene.objects if o.type=='LIGHT' and o.data.type=='SUN']:
  direction=light.matrix_world.to_quaternion()@Vector((0,0,1));direction.normalize();bins=collections.Counter();blockers=collections.Counter();dots=[]
  for face in faces:
   point=roof.matrix_world@face.center;normal=roof.matrix_world.to_3x3().inverted().transposed()@face.normal;normal.normalize();dot=normal.dot(direction);dots.append(dot)
   if dot<=0:bins['backfacing']+=1;continue
   origin=point+normal*.0001
   for attempt in range(30):
    hit,position,n,index,obj,matrix=scene.ray_cast(graph,origin,direction,distance=100)
    if not hit:bins['unoccluded']+=1;break
    if obj.hide_render or obj.name.startswith('COL_') or not obj.visible_shadow:origin=position+direction*.001;continue
    bins['occluded']+=1;blockers[obj.name]+=1;break
   else:bins['skip_limit']+=1
  record['suns'][light.name]={'energy':light.data.energy,'direction_to_light':list(direction),'normal_dot_range':[min(dots),max(dots)],'counts':dict(bins),'blockers':dict(blockers)}
 results.append(record)
(w/'tile-light-visibility.json').write_text(json.dumps({'scope':'Saved-source geometric ray visibility at ridge face centres; skips non-rendering/collision/no-shadow objects. Does not evaluate Cycles light linking, diffuse/normal mapping, UV filtering or full radiometry. No art acceptance.','sources':results},indent=2)+'\n')
print('TILE_LIGHT_VISIBILITY_PASS',json.dumps(results),flush=True)
