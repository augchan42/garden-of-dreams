"""Inspect exported Ouxiang roof components and matching RGB16 irradiance.

This does not infer saved Blender object names or replace native visual review.
"""
from collections import Counter,defaultdict
from pathlib import Path
import argparse,hashlib,json,struct,subprocess,sys
import numpy as np

ROOT=Path('/Users/auchan/projects/garden-of-dreams')
sys.path.insert(0,str(ROOT/'scripts'))
from verify_mountain_export import Glb

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=ROOT/'export/garden-of-dreams.glb')
parser.add_argument('--maps',type=Path,default=ROOT/'export/lightmaps')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
name='SITE_ouxiang-xie_MAT_rooftile'
g=Glb(args.source);digest=hashlib.sha256(g.bytes).hexdigest()
record=json.loads((args.maps/(name+'.json')).read_text())
assert record['source_glb_sha256']==digest and record['uv_channel']==1,'Source/map identity mismatch'
index=next(i for i,n in enumerate(g.doc['nodes']) if n.get('name')==name)
node=g.doc['nodes'][index]
parents={child:i for i,n in enumerate(g.doc['nodes']) for child in n.get('children',[])}
i=index
while True:
 n=g.doc['nodes'][i]
 assert not any(k in n for k in ['translation','rotation','scale','matrix']),'World-space identity transform required'
 if i not in parents:break
 i=parents[i]
primitives=g.doc['meshes'][node['mesh']]['primitives'];assert len(primitives)==1
p=primitives[0];assert p.get('mode',4)==4
pos=g.accessor(p['attributes']['POSITION']).astype(float)
indices=g.accessor(p['indices']).ravel().reshape(-1,3)
uv=g.accessor(p['attributes']['TEXCOORD_1'])[indices].astype(float)
# Position weld removes hard-normal/UV splits. It is export connectivity,
# not proof of original object ownership. Keep the tolerance explicit.
unique,inverse=np.unique(np.round(pos,6),axis=0,return_inverse=True)
tri_ids=inverse[indices];parent=np.arange(len(unique))
def find(i):
 while parent[i]!=i:
  parent[i]=parent[parent[i]];i=parent[i]
 return int(i)
for a,b,c in tri_ids:
 for u,v in [(a,b),(b,c)]:parent[find(u)]=find(v)
components=defaultdict(list)
for i,tri in enumerate(tri_ids):components[find(tri[0])].append(i)
groups=np.full(len(indices),'other',dtype=object);component_rows=[]
tri=pos[indices];cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.linalg.norm(cross,axis=1)
assert np.all(norm>1e-10),'Degenerate physical triangle'
normals=cross/norm[:,None]
for component,faces in components.items():
 vertices=np.unique(tri_ids[faces]);points=unique[vertices];center=points.mean(axis=0)
 edges=Counter(tuple(sorted((int(a),int(b)))) for face in tri_ids[faces] for a,b in [(face[0],face[1]),(face[1],face[2]),(face[2],face[0])])
 row={'export_component':component,'vertices':len(vertices),'triangles':len(faces),'closed_edges':all(count==2 for count in edges.values()),'world_positions_y_up':points.tolist(),'triangle_indices':faces}
 row['outward_geometric_normal_dot_min']=float(np.min(np.einsum('ij,ij->i',normals[faces],tri[faces].mean(axis=1)-center)))
 if len(vertices)==16 and len(faces)==28 and row['closed_edges']:
  delta=points-center;_,vectors=np.linalg.eigh(delta.T@delta);axis=vectors[:,-1];along=delta@axis
  rings=along>0
  if rings.sum()==8 and np.ptp(along[rings])<1e-5 and np.ptp(along[~rings])<1e-5:
   radii=np.linalg.norm(delta-along[:,None]*axis,axis=1)
   if np.ptp(radii)<1e-5 and radii.mean()>.001:
    ring_by_vertex={int(v):bool(r) for v,r in zip(vertices,rings)}
    for f in faces:groups[f]='cylinder_caps' if len({ring_by_vertex[int(v)] for v in tri_ids[f]})==1 else 'cylinder_sides'
    row.update(kind='closed_eight_sided_cylinder',radius_metres=float(radii.mean()),axis_length_metres=float(along[rings].mean()-along[~rings].mean()))
 if 'kind' not in row:row['kind']='other_export_component'
 component_rows.append(row)
path=args.maps/record['texture'];data=path.read_bytes()
w,h,depth,color,_,_,interlace=struct.unpack('>IIBBBBB',data[16:29])
assert depth==16 and color==2 and interlace==0 and w==h==record['size']
raw=subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(path),'-f','rawvideo','-pix_fmt','rgb48le','-'],capture_output=True,check=True).stdout
image=np.frombuffer(raw,dtype='<u2').reshape(h,w,3).astype(float)/65535
xy=np.clip((uv.mean(axis=1)*w).astype(int),0,w-1);light=image[xy[:,1],xy[:,0]]*record['scale']
e=np.stack([uv[:,1]-uv[:,0],uv[:,2]-uv[:,1],uv[:,0]-uv[:,2]],axis=1)*w
area=abs(e[:,0,0]*(-e[:,2,1])-e[:,0,1]*(-e[:,2,0]));longest=np.linalg.norm(e,axis=2).max(axis=1)
altitude=np.divide(area,longest,out=np.zeros_like(area),where=longest>0)
bins={}
for label in ['cylinder_sides','cylinder_caps','other']:
 for suffix,normal_mask in [('all',np.ones(len(indices),dtype=bool)),('upward',normals[:,1]>.25)]:
  mask=(groups==label)&normal_mask
  bins[label+'_'+suffix]={'triangles':int(mask.sum())}
  if mask.any():bins[label+'_'+suffix].update(altitude_source_pixels_quantiles=np.quantile(altitude[mask],[0,.25,.5,.75,1]).tolist(),triangles_under_one_source_pixel_altitude=int((altitude[mask]<1).sum()),zero_irradiance_centroids=int((light[mask].max(axis=1)==0).sum()),irradiance_luminance_quantiles=np.quantile(light[mask]@np.asarray([.2126,.7152,.0722]),[0,.25,.5,.75,1]).tolist())
assert sum(v['triangles'] for k,v in bins.items() if k.endswith('_all'))==len(indices)
report={'status':'export_components_and_matching_rgb16_centroids_measured','source_glb_sha256':digest,'source_map_sha256':hashlib.sha256(data).hexdigest(),'source_record_sha256':hashlib.sha256((args.maps/(name+'.json')).read_bytes()).hexdigest(),'source_map_size':w,'position_weld_decimals':6,'mesh':name,'export_triangles':len(indices),'component_kinds':dict(Counter(r['kind'] for r in component_rows)),'components':component_rows,'groups':bins,'scope':'Export-space connectivity and analytic cylinder classification only; not saved Blender object ownership. Source-matched RGB16 triangle-centroid samples and UV2 altitudes exclude visible-pixel coverage, lightmap filtering, camera visibility, source corrections and final art acceptance.'}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('OUX_EXPORT_COMPONENT_DIAGNOSIS',json.dumps({'components':report['component_kinds'],'groups':bins}))
