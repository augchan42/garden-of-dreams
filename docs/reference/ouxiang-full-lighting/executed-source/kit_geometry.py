"""Small explicit mesh builder for shared-atlas stock libraries."""
import math,bpy,bmesh
from mathutils import Vector
class Geometry:
 def __init__(self,material,cells,quality=1):self.material=material;self.cells=cells;self.quality=quality;self.v=[];self.f=[];self.uv=[]
 def face(self,points,cell,uv=None):
  start=len(self.v);self.v.extend(points);self.f.append(tuple(range(start,start+len(points))))
  if uv is None:
   uv=[(0,0),(1,0),(1,1),(0,1)] if len(points)==4 else [(.5+.48*math.cos(i*math.tau/len(points)),.5+.48*math.sin(i*math.tau/len(points))) for i in range(len(points))]
  index=self.cells[cell];x=index%4;y=index//4
  self.uv.append([((x+.025+.95*u)/4,1-(y+.025+.95*(1-v))/4) for u,v in uv])
 def box(self,p,size,cell):
  p=Vector(p);x,y,z=(v/2 for v in size);v=[p+Vector(q) for q in [(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]]
  for ids in [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]:self.face([v[i] for i in ids],cell)
 def stem(self,a,b,r,cell,n=8):
  a=Vector(a);b=Vector(b);axis=(b-a).normalized();side=axis.cross(Vector((0,1,0)))
  if side.length<.01:side=axis.cross(Vector((1,0,0)))
  side.normalize();other=axis.cross(side)
  rings=[[p+r*(side*math.cos(i*math.tau/n)+other*math.sin(i*math.tau/n)) for i in range(n)] for p in [a,b]]
  for i in range(n):self.face([rings[0][i],rings[0][(i+1)%n],rings[1][(i+1)%n],rings[1][i]],cell)
  for ring,reverse in [(rings[0],True),(rings[1],False)]:
   for i in range(1,n-1):
    q=[ring[0],ring[i],ring[i+1]];self.face(list(reversed(q)) if reverse else q,cell)
 def case(self,p,size,cell,n=4):
  # Rounded XZ profile, bevelled front edge, solid back. Front faces -Y.
  p=Vector(p);x,y,z=(v/2 for v in size);r=min(x,z)*.18;rings=[]
  for yy,factor in [(-y,.92),(-y+.025,1),(y,1)]:
   ring=[]
   for cx,cz,start in [(x-r,z-r,0),(-x+r,z-r,90),(-x+r,-z+r,180),(x-r,-z+r,270)]:
    for j in range(n+1):
     a=math.radians(start+j*90/n);ring.append(p+Vector(((cx+r*math.cos(a))*factor,yy,(cz+r*math.sin(a))*factor)))
   rings.append(ring)
  count=len(rings[0])
  for k in range(2):
   for i in range(count):self.face([rings[k][i],rings[k][(i+1)%count],rings[k+1][(i+1)%count],rings[k+1][i]],cell)
  self.face(list(reversed(rings[0])),cell);self.face(rings[-1],cell)
 def object(self,name,col):
  data=bpy.data.meshes.new(name);data.from_pydata(self.v,[],self.f);data.update();data.materials.append(self.material)
  uv=data.uv_layers.new(name='UVMap')
  for poly,coords in zip(data.polygons,self.uv):
   for loop,co in zip(poly.loop_indices,coords):uv.data[loop].uv=co
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
  o=bpy.data.objects.new(name,data);col.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
  data.uv_layers.new(name='LightmapUV');data.uv_layers.active_index=1
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');data.uv_layers.active_index=0;o.select_set(False)
  return o
