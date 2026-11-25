import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'));name='AOJING_ground_west_infill';obj=bpy.data.objects.get(name);errors=[];facts={}
if obj is None:errors.append('Missing west infill over exposed black base floor')
else:
 points=[obj.matrix_world@Vector(v) for v in obj.bound_box];lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)];facts={'bounds_min':lo,'bounds_max':hi,'material_names':[m.name for m in obj.data.materials],'collections':[c.name for c in obj.users_collection],'polygons':len(obj.data.polygons)}
 for a,b in zip(lo,[18,-21,-.63]):
  if abs(a-b)>1e-5:errors.append('West infill lower bound differs')
 for a,b in zip(hi,[20.2,-14,-.13]):
  if abs(a-b)>1e-5:errors.append('West infill upper bound differs')
 if facts['material_names']!=['MAT_stage_canvas'] or facts['collections']!=['SITE_stage'] or facts['polygons']!=6:errors.append('Infill must be one closed six-face canvas cube in stage collection')
 top=[p for p in obj.data.polygons if p.normal.z>.99]
 if len(top)!=1:errors.append('Infill must have one upward top face')
 # Positive XY overlap with ramp/pond/low hall surfaces is forbidden.
 for other in scene.objects:
  if other.type!='MESH' or other.name==name:continue
  if other.name not in ['AOJING_pond','AOJING_approach_ramp','AOJING_dry_ledge','AOJING_hall_floor']:continue
  p=[other.matrix_world@Vector(v) for v in other.bound_box];ol=[min(v[i] for v in p) for i in range(3)];oh=[max(v[i] for v in p) for i in range(3)]
  overlap=max(0,min(hi[0],oh[0])-max(lo[0],ol[0]))*max(0,min(hi[1],oh[1])-max(lo[1],ol[1]))
  if overlap>1e-5:errors.append('Infill overlaps authored Aojing footprint: '+other.name)
 # Clip each ramp-guard face to the infill XY rectangle and check its
 # actual Z clearance. An overhead rail may share the same XY footprint.
 def clip(poly,axis,bound,minimum):
  result=[]
  if not poly:return result
  previous=poly[-1];inside_previous=previous[axis]>=bound if minimum else previous[axis]<=bound
  for current in poly:
   inside_current=current[axis]>=bound if minimum else current[axis]<=bound
   if inside_previous!=inside_current:
    t=(bound-previous[axis])/(current[axis]-previous[axis]);result.append(previous.lerp(current,t))
   if inside_current:result.append(current)
   previous=current;inside_previous=inside_current
  return result
 clearances=[]
 for guard in scene.objects:
  if guard.type!='MESH' or not guard.name.startswith(('AOJING_approach_guard','COL_aojing_approach_guard')):continue
  clipped=[]
  for face in guard.data.polygons:
   polygon=[guard.matrix_world@guard.data.vertices[i].co for i in face.vertices]
   for axis,bound,minimum in [(0,lo[0],True),(0,hi[0],False),(1,lo[1],True),(1,hi[1],False)]:polygon=clip(polygon,axis,bound,minimum)
   clipped.extend(polygon)
  if clipped:
   clearance=min(p.z for p in clipped)-hi[2];clearances.append({'name':guard.name,'minimum_clearance_m':clearance})
   if clearance<=1e-5:errors.append('Ramp guard intersects infill height: '+guard.name)
 if len(clearances)!=2:errors.append('Both west-ramp guard render/collider clearances must be measured')
 facts['ramp_guard_clearances']=clearances
report={'status':'passed' if not errors else 'failed','source_authoring_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'facts':facts,'errors':errors,'scope':'Saved patch bounds/material/topology/collection and no positive area overlap with existing pond/ramp/ledge/hall floor footprints. Does not prove collision, native art, matching export/UV/lightmaps or final acceptance.'}
(R/'export/aojing-ground-contract.json').write_text(json.dumps(report,indent=2)+'\n');print('AOJING_GROUND_CONTRACT',len(errors),'errors');assert not errors,errors
