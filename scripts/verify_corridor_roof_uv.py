"""Check source raster area for every actual Qinfang corridor roof triangle.

This checks finite UVs and geometry coverage, not lighting, gutters or final art.
"""
from pathlib import Path
import argparse,json,struct
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=ROOT/'export/garden-of-dreams.glb')
parser.add_argument('--output',type=Path,default=ROOT/'export/corridor-roof-uv-validation.json')
args=parser.parse_args()
data=args.source.read_bytes();length=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+length]);binary=data[28+length:]
def accessor(index):
 a=doc['accessors'][index];view=doc['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
 return np.ndarray((a['count'],cols),dtype=dt,buffer=binary,offset=view.get('byteOffset',0)+a.get('byteOffset',0),strides=(view.get('byteStride',dt.itemsize*cols),dt.itemsize)).copy()
node_index,node=next((i,n) for i,n in enumerate(doc['nodes']) if n.get('name')=='SITE_qinfang-ting_MAT_pavilion_atlas')
assert all(node_index not in n.get('children',[]) for n in doc['nodes']),'Unexpected parent transform'
primitive=doc['meshes'][node['mesh']]['primitives'][0];position=accessor(primitive['attributes']['POSITION']);primary=accessor(primitive['attributes']['TEXCOORD_0']);uv2=accessor(primitive['attributes']['TEXCOORD_1']);indices=accessor(primitive['indices']).ravel().reshape(-1,3)
assert np.isfinite(uv2).all() and uv2.min()>=0 and uv2.max()<=1
if 'matrix' in node:matrix=np.array(node['matrix']).reshape(4,4).T
else:
 q=np.array(node.get('rotation',[0,0,0,1]));xyz=q[:3];w=q[3];rotation=(w*w-xyz@xyz)*np.eye(3)+2*np.outer(xyz,xyz)+2*w*np.array([[0,-xyz[2],xyz[1]],[xyz[2],0,-xyz[0]],[-xyz[1],xyz[0],0]]);matrix=np.eye(4);matrix[:3,:3]=rotation@np.diag(node.get('scale',[1,1,1]));matrix[:3,3]=node.get('translation',[0,0,0])
world=position@matrix[:3,:3].T+matrix[:3,3];rows=[]
for i,tri in enumerate(indices):
 points=world[tri];uv=primary[tri];center=points.mean(axis=0)
 if not (points[:,1]>2.79).all():continue
 if not ((uv[:,0]>.515624)&(uv[:,0]<.984376)&(uv[:,1]>.015624)&(uv[:,1]<.484376)).all():continue
 if abs(center[0])<1.21 and 6.84<abs(center[2])<19.16:direction='north' if center[2]<0 else 'south'
 elif abs(center[2])<1.21 and 6.84<abs(center[0])<19.16:direction='east' if center[0]>0 else 'west'
 else:continue
 chart=uv2[tri]*256;ab=chart[1]-chart[0];ac=chart[2]-chart[0];area=float(abs(ab[0]*ac[1]-ab[1]*ac[0])/2);rows.append({'triangle_index':i,'direction':direction,'area_texels256':area})
assert len(rows)==784,('Unexpected actual roof coverage',len(rows))
failures=[row for row in rows if row['area_texels256']<=1]
report={'status':'failed' if failures else 'passed','source':str(args.source),'roof_triangles':len(rows),'minimum_triangle_area_texels256':min(r['area_texels256'] for r in rows),'subtexel_triangle_count':len(failures),'rows':rows,'scope':'Actual source geometry-classified roof triangles and UV2 raster area at256. Every triangle must exceed one texel. No light/gutter/compression/final art acceptance.'}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
assert not failures,('Subtexel corridor roof charts',len(failures),report['minimum_triangle_area_texels256'])
print('CORRIDOR_ROOF_UV_PASS',len(rows),report['minimum_triangle_area_texels256'])
