"""Create an isolated Ouxiang UV2 proposal without changing physical attributes."""
from pathlib import Path
from collections import Counter
import copy,hashlib,json,struct,sys
import numpy as np

REPO=Path('/Users/auchan/projects/garden-of-dreams')
sys.path.insert(0,str(REPO/'scripts'))
from verify_mountain_export import Glb
ROOT=Path(json.loads(Path('/tmp/garden-oux-roof-probe.json').read_text())['folder'])
SOURCE=Path(json.loads(Path('/tmp/garden-imperial-full-source.json').read_text())['folder'])/'export/garden-of-dreams.glb'
g=Glb(SOURCE)
before_hash=hashlib.sha256(g.bytes).hexdigest()
assert before_hash=='361a67c759974e4fb5897a15d5a7354076ef30392b7a6ed988cca6029f198611'
diagnosis=json.loads((ROOT/'export-component-sampling.json').read_text())
name=diagnosis['mesh'];node=next(n for n in g.doc['nodes'] if n.get('name')==name)
assert not any(k in node for k in ['translation','rotation','scale','matrix'])
p=g.doc['meshes'][node['mesh']]['primitives'][0]
attrs={k:g.accessor(v) for k,v in p['attributes'].items()}
indices=g.accessor(p['indices']).ravel().reshape(-1,3)
assert len(indices)==diagnosis['export_triangles']==4730
pos=attrs['POSITION'].astype(float)
unique,inverse=np.unique(np.round(pos,6),axis=0,return_inverse=True)
tri_ids=inverse[indices]
old=Glb(REPO/'export/garden-of-dreams.glb')
oldnode=next(n for n in old.doc['nodes'] if n.get('name')==name)
oldp=old.doc['meshes'][oldnode['mesh']]['primitives'][0]
oi=old.accessor(oldp['indices']).ravel()
assert set(oldp['attributes'])==set(p['attributes'])
for k,v in attrs.items():
 assert np.array_equal(old.accessor(oldp['attributes'][k])[oi],v[indices.ravel()]),('Ouxiang source changed',k)
uv=np.zeros((len(indices),3,2),dtype=float);assigned=np.zeros(len(indices),dtype=bool)
cylinders=[r for r in diagnosis['components'] if r['kind']=='closed_eight_sided_cylinder']
others=[r for r in diagnosis['components'] if r['kind']!='closed_eight_sided_cylinder']
assert len(cylinders)==168 and len(others)==1 and others[0]['triangles']==26
layout=[]
for i,row in enumerate(cylinders):
 faces=row['triangle_indices'];vertices=np.unique(tri_ids[faces]);points=unique[vertices];center=points.mean(axis=0)
 delta=points-center;_,vectors=np.linalg.eigh(delta.T@delta);axis=vectors[:,-1];along=delta@axis;rings=along>0
 assert rings.sum()==8 and np.ptp(along[rings])<1e-5 and np.ptp(along[~rings])<1e-5
 radial=delta-along[:,None]*axis
 basis=radial[0]/np.linalg.norm(radial[0]);second=np.cross(axis,basis)
 angles=np.mod(np.arctan2(radial@second,radial@basis),2*np.pi)
 sectors=np.mod(np.rint(angles/(np.pi/4)).astype(int),8)
 error=np.abs(np.angle(np.exp(1j*(angles-sectors*np.pi/4))))
 assert error.max()<.001,('Not a regular octagonal cylinder',error.max())
 lookup={int(v):(int(s),bool(r),float(a),float(b)) for v,s,r,a,b in zip(vertices,sectors,rings,radial@basis,radial@second)}
 origin=np.asarray([(i%14)*64,(i//14)*64])
 counts=Counter()
 for f in faces:
  assert not assigned[f];assigned[f]=True
  values=[lookup[int(v)] for v in tri_ids[f]]
  cap=len({r for s,r,a,b in values})==1
  if cap:
   disk=origin+np.asarray([52,44 if values[0][1] else 16])
   uv[f]=[disk+8*np.asarray([a,b])/row['radius_metres'] for s,r,a,b in values]
   counts['caps']+=1
  else:
   sectors=[s for s,r,a,b in values]
   wrap=max(sectors)-min(sectors)>1
   assert len(set(sectors))==2
   assert (set(sectors)=={0,7}) if wrap else max(sectors)-min(sectors)==1
   uv[f]=[origin+np.asarray([8+4*(8 if wrap and s==0 else s),8+48*int(r)]) for s,r,a,b in values]
   counts['sides']+=1
 assert counts=={'caps':12,'sides':16}
 layout.append({'export_component':row['export_component'],'cell_origin_source_pixels':origin.tolist(),'cell_size':64,'side_chart_pixels':[32,48],'cap_radius_pixels':8,'minimum_rectangular_chart_gap_pixels':4})
shell=others[0]['triangle_indices'];points=pos[indices[shell]]
xmin,zmin=points[:,:,[0,2]].reshape(-1,2).min(axis=0);xmax,zmax=points[:,:,[0,2]].reshape(-1,2).max(axis=0)
assert xmax>xmin and zmax>zmin
for f in shell:
 assert not assigned[f];assigned[f]=True
 xy=pos[indices[f]][:,[0,2]]
 uv[f]=np.asarray([8,776])+(xy-np.asarray([xmin,zmin]))/np.asarray([xmax-xmin,zmax-zmin])*np.asarray([1008,240])
assert assigned.all() and uv.min()>=0 and uv.max()<=1024

# Check geometric triangle overlap within each separate component's charts.
def cross2(a,b):return float(a[0]*b[1]-a[1]*b[0])
def overlap(a,b):
 if np.any(a.max(axis=0)<=b.min(axis=0)+1e-7) or np.any(b.max(axis=0)<=a.min(axis=0)+1e-7):return 0.
 polygon=[x.copy() for x in a]
 if cross2(b[1]-b[0],b[2]-b[0])<0:b=b[::-1]
 for s,e in zip(b,np.roll(b,-1,axis=0)):
  clipped=[]
  for u,v in zip(polygon,polygon[1:]+polygon[:1]):
   du=cross2(e-s,u-s);dv=cross2(e-s,v-s)
   if du>=-1e-9:clipped.append(u)
   if (du>=-1e-9)!=(dv>=-1e-9):clipped.append(u+(v-u)*(du/(du-dv)))
  polygon=clipped
  if not polygon:return 0.
 return abs(sum(cross2(a,b) for a,b in zip(polygon,polygon[1:]+polygon[:1])))*.5
overlaps=[]
for row in diagnosis['components']:
 faces=row['triangle_indices']
 for i,a in enumerate(faces):
  for b in faces[i+1:]:
   area=overlap(uv[a],uv[b])
   if area>1e-5:overlaps.append([a,b,area])
assert not overlaps,('Proposed chart overlap',overlaps[:5])

# Duplicate only vertices that require a distinct UV2 seam. Original physical,
# normal, primary UV and other attributes stay bit-identical per triangle.
lookup={};source_indices=[];new_uv=[];new_indices=[]
for face_index,face in enumerate(indices):
 for corner,original in enumerate(face):
  coordinate=tuple((uv[face_index,corner]/1024).astype(np.float32))
  key=(int(original),coordinate)
  if key not in lookup:
   lookup[key]=len(source_indices);source_indices.append(int(original));new_uv.append(coordinate)
  new_indices.append(lookup[key])
source_indices=np.asarray(source_indices)
arrays={k:(np.asarray(new_uv,dtype='<f4') if k=='TEXCOORD_1' else v[source_indices]) for k,v in attrs.items()}
new_indices=np.asarray(new_indices,dtype='<u4')
doc=copy.deepcopy(g.doc);binary=bytearray(g.binary)
def append_accessor(array,previous):
 while len(binary)%4:binary.append(0)
 view={'buffer':0,'byteOffset':len(binary),'byteLength':array.nbytes}
 binary.extend(array.tobytes());doc['bufferViews'].append(view)
 accessor=copy.deepcopy(previous);accessor.update(bufferView=len(doc['bufferViews'])-1,byteOffset=0,count=len(array))
 doc['accessors'].append(accessor);return len(doc['accessors'])-1
target=doc['meshes'][node['mesh']]['primitives'][0]
target['attributes']={k:append_accessor(v,g.doc['accessors'][p['attributes'][k]]) for k,v in arrays.items()}
target['indices']=append_accessor(new_indices,{'componentType':5125,'type':'SCALAR'})
while len(binary)%4:binary.append(0)
doc['buffers'][0]['byteLength']=len(binary)
payload=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode()
payload+=b' '*((-len(payload))%4)
data=struct.pack('<III',0x46546c67,2,28+len(payload)+len(binary))+struct.pack('<II',len(payload),0x4e4f534a)+payload+struct.pack('<II',len(binary),0x004e4942)+binary
out=ROOT/'garden-oux-uv-proposal.glb';out.write_bytes(data)
candidate=Glb(out)
# Independent re-opened semantic comparison of all nodes and all attributes.
assert candidate.doc['nodes']==g.doc['nodes'] and candidate.doc['materials']==g.doc['materials']
preserved=0
for n in g.doc['nodes']:
 if 'mesh' not in n:continue
 before=g.doc['meshes'][n['mesh']];after=candidate.doc['meshes'][n['mesh']]
 assert {k:v for k,v in before.items() if k!='primitives'}=={k:v for k,v in after.items() if k!='primitives'}
 for a,b in zip(before['primitives'],after['primitives']):
  assert {k:v for k,v in a.items() if k not in ('indices','attributes')}=={k:v for k,v in b.items() if k not in ('indices','attributes')}
  assert a['attributes'].keys()==b['attributes'].keys()
  ia=g.accessor(a['indices']).ravel();ib=candidate.accessor(b['indices']).ravel();assert len(ia)==len(ib)
  for key in a['attributes']:
   oldvalues=g.accessor(a['attributes'][key])[ia];newvalues=candidate.accessor(b['attributes'][key])[ib]
   if n.get('name')==name and key=='TEXCOORD_1':assert not np.array_equal(oldvalues,newvalues)
   else:assert np.array_equal(oldvalues,newvalues),('Physical/export contract changed',n.get('name'),key)
 preserved+=len(ia)//3
for key in ['asset','extensions','extensionsUsed','extensionsRequired','scene','scenes','cameras','images','textures','samplers']:
 assert candidate.doc.get(key)==g.doc.get(key),key
for image in g.doc['images']:assert g.image_hash(image)==candidate.image_hash(image)
decoded=candidate.accessor(candidate.doc['meshes'][node['mesh']]['primitives'][0]['attributes']['TEXCOORD_1'])[new_indices].reshape(-1,3,2)*1024
edges=np.stack([decoded[:,1]-decoded[:,0],decoded[:,2]-decoded[:,1],decoded[:,0]-decoded[:,2]],axis=1)
alt=abs(edges[:,0,0]*(-edges[:,2,1])-edges[:,0,1]*(-edges[:,2,0]))/np.linalg.norm(edges,axis=2).max(axis=1)
assert alt.min()>=1,'Still subpixel at source size'
report={'status':'isolated_cpu_uv_proposal_geometry_preserved','before_sha256':before_hash,'candidate_sha256':hashlib.sha256(data).hexdigest(),'target_mesh':name,'unchanged_authoring_sha256':hashlib.sha256((REPO/'blender/authoring.blend').read_bytes()).hexdigest(),'matched_export_cylinders':len(cylinders),'target_triangles':len(indices),'all_expanded_triangles_checked':preserved,'target_uv2_minimum_altitude_at_1024':float(alt.min()),'target_uv2_minimum_altitude_at_512':float(alt.min()/2),'geometric_chart_overlaps':len(overlaps),'cylinder_layout':layout,'roof_projection_bounds_source_pixels':[8,776,1016,1016],'scope':'CPU UV2 proposal only. Saved Blender ownership/default exporter equivalence, actual native lighting, PNG gutters/filtering, rendering, allocation and device acceptance remain pending. No old lightmaps installed, canonical source change or production adoption.'}
(ROOT/'uv-proposal.json').write_text(json.dumps(report,indent=2)+'\n')
print('OUX_UV_PROPOSAL_GEOMETRY_PRESERVED',report['candidate_sha256'],report['target_uv2_minimum_altitude_at_1024'],preserved)
