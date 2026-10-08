import hashlib,json,pathlib,sys
import numpy as np
sys.path.insert(0,'/Users/auchan/projects/garden-of-dreams/scripts')
from verify_mountain_export import Glb
R=pathlib.Path('/Users/auchan/projects/garden-of-dreams')
g=Glb(R/'godot/assets/garden-of-dreams.glb')
parents={c:i for i,n in enumerate(g.doc['nodes']) for c in n.get('children',[])}
def matrix(n):
 if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
 x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4)
 m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                    [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                    [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]))
 m[:3,3]=n.get('translation',[0,0,0]);return m
world={}
def wm(i):
 if i not in world:world[i]=(wm(parents[i]) if i in parents else np.eye(4))@matrix(g.doc['nodes'][i])
 return world[i]
triangles=[];labels=[];uvs=[]
for ni,n in enumerate(g.doc['nodes']):
 if 'mesh' not in n:continue
 for p in g.doc['meshes'][n['mesh']]['primitives']:
  if 'material' not in p or p.get('mode',4)!=4:continue
  m=g.doc['materials'][p['material']]
  if m.get('alphaMode')=='BLEND' or 'fog' in m['name'].lower():continue
  if n['name'].startswith('HERO_table_line_') and '_broken' in n['name']:continue
  pos=g.accessor(p['attributes']['POSITION']).astype(float)
  pos=(np.c_[pos,np.ones(len(pos))]@wm(ni).T)[:,:3]
  idx=g.accessor(p['indices']).ravel().reshape(-1,3)
  triangles.append(pos[idx]);labels.extend([(n['name'],m['name'],j) for j in range(len(idx))])
  uvs.append(g.accessor(p['attributes']['TEXCOORD_1'])[idx] if 'TEXCOORD_1' in p['attributes'] else np.full((len(idx),3,2),np.nan))
tri=np.concatenate(triangles);uv=np.concatenate(uvs)
eye=np.array([-7.,9.5,20.]);target=np.array([-23.,.5,0.])
forward=target-eye;forward/=np.linalg.norm(forward)
right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right)
up=np.cross(right,forward);tangent=np.tan(np.deg2rad(55)/2)
e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];delta=eye-tri[:,0]
rows=[]
for x,y in [(34,468),(193,512),(12,485),(83,493),(100,484),(280,517),(190,491),(120,502)]:
 ray=forward+right*((2*(x+.5)/390-1)*390/844*tangent)+up*((1-2*(y+.5)/844)*tangent);ray/=np.linalg.norm(ray)
 h=np.cross(np.broadcast_to(ray,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h)
 good=np.abs(a)>1e-9;f=np.divide(1,a,out=np.zeros_like(a),where=good)
 u=f*np.einsum('ij,ij->i',delta,h);q=np.cross(delta,e1);v=f*(q@ray);distance=f*np.einsum('ij,ij->i',e2,q)
 hits=np.where(good&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)&(distance>.01))[0]
 hits=hits[np.argsort(distance[hits])]
 nearest=[]
 for i in hits[:5]:
  nearest.append({'node':labels[i][0],'material':labels[i][1],'primitive_triangle':labels[i][2],
   'distance':float(distance[i]),'world_y_up':(eye+ray*distance[i]).tolist(),
   'uv2':((1-u[i]-v[i])*uv[i,0]+u[i]*uv[i,1]+v[i]*uv[i,2]).tolist()})
 rows.append({'pixel':[x,y],'nearest_geometric_intersections':nearest})
report={'scope':'CPU ray/triangle geometry attribution at chosen pixels of the existing 390x844 Ouxiang portrait. Transparent blends/fog are excluded; material shading, GPU visibility/culling and exact runtime view must be confirmed natively. No production edits.',
 'source_glb_sha256':hashlib.sha256(g.bytes).hexdigest(),
 'reference_png':'docs/reference/ouxiang-portrait512/captures/portrait-water-candidate-import512.png',
 'reference_png_sha256':hashlib.sha256((R/'docs/reference/ouxiang-portrait512/captures/portrait-water-candidate-import512.png').read_bytes()).hexdigest(),
 'camera_assumption':{'position':eye.tolist(),'target':target.tolist(),'fov':55,'keep_aspect':'KEEP_HEIGHT','viewport':[390,844]},
 'triangles_checked':len(tri),'pixels':rows}
p=pathlib.Path('/tmp/garden-oux-visible-surface-probe.json');p.write_text(json.dumps(report,indent=2)+'\n')
for row in rows:print(row['pixel'],[(h['node'],h['world_y_up']) for h in row['nearest_geometric_intersections'][:2]])
