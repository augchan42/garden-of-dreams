"""Inspect saved culm topology independently of the geometry constructor."""
from math import isfinite

def inspect(mesh,variant):
 n={'bamboo_small':3,'bamboo_medium':5,'bamboo_large':7}[variant]
 uv=mesh.uv_layers['UVMap'];parent={}
 def find(a):
  parent.setdefault(a,a)
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 culm_faces=[]
 for p in mesh.polygons:
  coords=[uv.data[i].uv for i in p.loop_indices]
  if all(.75<u<1 and .5<v<.75 for u,v in coords):
   culm_faces.append(p)
   for v in p.vertices:parent[find(v)]=find(p.vertices[0])
 components={}
 for i in parent:components.setdefault(find(i),[]).append(mesh.vertices[i].co)
 spans=[{'height':max(p.z for p in points)-min(p.z for p in points),'vertices':len(points)} for points in components.values()]
 stems=[s for s in spans if s['height']>.2];collars=[s for s in spans if s['height']<=.2]
 height=max(v.co.z for v in mesh.vertices)-min(v.co.z for v in mesh.vertices)
 tris=sum(len(p.vertices)-2 for p in mesh.polygons)
 result={'variant':variant,'height_m':height,'triangles':tris,'continuous_culms':len(stems),'joint_collars':len(collars),'culm_components':spans,'uv_layers':[u.name for u in mesh.uv_layers]}
 assert len(stems)==n,('Disconnected internodes',result)
 assert len(collars)==3*n,('Missing joint collars',result)
 assert all(s['height']>1.9 for s in stems),('Short isolated stem',result)
 assert 2.5<=height<=4.5,('Clump height outside site spec',result)
 assert len(mesh.uv_layers)==2 and mesh.uv_layers[0].name=='UVMap'
 assert all(isfinite(c) for v in mesh.vertices for c in v.co)
 return result
