"""Measure actual source lattice occlusion of the CRT phosphor quads."""
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def inspect():
 site=bpy.data.collections['SITE_qiushuang-zhai']
 bars=sorted([o for o in site.objects if o.type=='MESH' and 'lattice' in o.name.lower()],key=lambda o:o.name)
 banks=sorted([o for o in site.objects if o.get('tech_variant')=='monitor_bank'],key=lambda o:o.location.x)
 assert len(bars)==42 and len(banks)==3
 vertices=[];faces=[];owners=[]
 for o in bars:
  start=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
  for p in o.data.polygons:faces.append([start+i for i in p.vertices]);owners.append(o.name)
 tree=BVHTree.FromPolygons(vertices,faces,all_triangles=False)
 rows=[]
 for bank in banks:
  points=[];uv=bank.data.uv_layers[0]
  for p in bank.data.polygons:
   coords=[uv.data[i].uv for i in p.loop_indices]
   center=sum(coords,Vector((0.,0.)))/len(coords)
   if .006<center.x<.244 and .506<center.y<.744:
    points.append(bank.matrix_world@p.center)
  # Exactly four 8 by 6 CRT phosphor grids, not the bezel/status cells.
  assert len(points)==192,(bank.name,len(points))
  for pose,height in [('authored',1.65),('runtime',1.7)]:
   origin=Vector((bank.location.x,12.7,height))
   blocked=[]
   for index,target in enumerate(points):
    direction=target-origin
    hit,normal,face,distance=tree.ray_cast(origin,direction.normalized(),direction.length-1e-5)
    if hit is not None:blocked.append({'sample':index,'bar':owners[face],'target':list(target),'hit':list(hit)})
   rows.append({'bank':bank.name,'pose':pose,'origin':list(origin),'samples':len(points),'blocked':blocked})
 return {'status':'passed' if all(not r['blocked'] for r in rows) else 'failed_lattice_crosses_screen',
         'lattice_objects':len(bars),'banks':rows,'total_samples':sum(r['samples'] for r in rows),
         'blocked_samples':sum(len(r['blocked']) for r in rows),
         'scope':'Rays from authored and runtime bank close-up positions to all 576 actual phosphor quad centres each. This is geometry evidence, not text legibility or final lighting acceptance.'}
