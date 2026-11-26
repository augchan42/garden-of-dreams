from pathlib import Path
import json,struct,math,hashlib
repo=Path('/Users/auchan/projects/garden-of-dreams');work=Path(__file__).resolve().parent
raw=(repo/'export/garden-of-dreams.glb').read_bytes();assert hashlib.sha256(raw).hexdigest()=='c9d4fb308730733af2175c424449f8a63b731674d2527df2168a260cc0f5013e'
length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);binary=raw[28+length:]
parents={child:i for i,n in enumerate(doc['nodes']) for child in n.get('children',[])}
def sub(a,b):return [a[i]-b[i] for i in range(3)]
def add(a,b):return [a[i]+b[i] for i in range(3)]
def mul(a,t):return [x*t for x in a]
def dot(a,b):return sum(a[i]*b[i] for i in range(3))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(v):return mul(v,1/math.sqrt(dot(v,v)))
def transform(p,index):
 n=doc['nodes'][index]
 if 'matrix' in n:
  m=n['matrix'];p=[sum(m[j*4+i]*p[j] for j in range(3))+m[12+i] for i in range(3)]
 else:
  p=[p[i]*n.get('scale',[1,1,1])[i] for i in range(3)];q=n.get('rotation',[0,0,0,1]);u=q[:3];p=add(p,add(mul(cross(u,p),2*q[3]),mul(cross(u,cross(u,p)),2)));p=add(p,n.get('translation',[0,0,0]))
 return transform(p,parents[index]) if index in parents else p
def vertices(name,local_filter=None):
 index=next(i for i,n in enumerate(doc['nodes']) if n.get('name')==name);node=doc['nodes'][index];result=[]
 for prim in doc['meshes'][node['mesh']]['primitives']:
  a=doc['accessors'][prim['attributes']['POSITION']];view=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3'
  for i in range(a['count']):
   p=struct.unpack_from('<fff',binary,view.get('byteOffset',0)+a.get('byteOffset',0)+i*view.get('byteStride',12))
   if local_filter is None or local_filter(p):result.append(transform(p,index))
 return result
def measure(points,position,target,fov,size):
 fwd=norm(sub(target,position));right=norm(cross(fwd,[0,1,0]));up=cross(right,fwd);focal=size[0]/(2*math.tan(math.radians(fov)/2));xs=[];ys=[]
 for p in points:
  delta=sub(p,position);depth=dot(fwd,delta);assert depth>0
  xs.append(size[0]/2+focal*dot(right,delta)/depth);ys.append(size[1]/2-focal*dot(up,delta)/depth)
 return {'low':[min(xs),min(ys)],'high':[max(xs),max(ys)],'width_fraction':(max(xs)-min(xs))/size[0]}
hall=sum([vertices('SITE_yihong-yuan_MAT_'+name) for name in ['rooftile','yihong_lacquer','lattice_wood','crt_amber']],[])
doors=vertices('SITE_yihong-yuan_MAT_yihong_lacquer',lambda p:abs(p[0])<=.946 and .099<=p[1]<=2.101 and .089<=p[2]<=.231)
leaves=vertices('HERO_flora_yihong_yuan_4.001');assert len(hall)==2744 and len(doors)==48
baseline=json.loads((work/'baseline-positioned/report.json').read_text())
row=next(x for x in baseline['rows'] if x['phase']=='arrival-portrait');prediction=measure(hall,row['camera_position'],[24.3,1.25,1],55,[390,844]);actual=row['measurement']
assert max(abs(prediction[k][i]-actual[k][i]) for k in ['low','high'] for i in range(2))<.01
print('CPU_PROJECTION_REPRODUCES_NATIVE',prediction)
proposals={
 'arrival':(hall,[16.8,3.45,5.75],[24.3,-2.4,1],62),
 'doors':(doors,[22.2,1.65,1],[25,-.1,1],58),
 'leaves':(leaves,[19.35,2.9,2.45],[23.65,-.8,-1.45],55)}
output={'status':'cpu_geometry_projection_proposals_native_review_required','baseline_prediction':prediction,'proposals':{}}
for action,(points,position,target,fov) in proposals.items():
 output['proposals'][action]={'position':position,'target':target,'fov':fov,'measurements':{}}
 for size in [[390,844],[360,800]]:
  d=measure(points,position,target,fov,size);output['proposals'][action]['measurements'][str(size)]=d;print(action,size,d)
(work/'projection-proposals.json').write_text(json.dumps(output,indent=2)+'\n')
