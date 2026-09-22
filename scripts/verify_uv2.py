"""Raster-check interior UV2 triangle overlap in the exported render meshes.

This detects overlaps at 512-square texel resolution; subtexel overlaps and gutter
quality still require visual review. Shared triangle edges are excluded.
"""
from pathlib import Path
import struct,json
import numpy as np
root=Path(__file__).resolve().parents[1]
data=(root/'export/garden-of-dreams.glb').read_bytes();length=struct.unpack_from('<I',data,12)[0]
doc=json.loads(data[20:20+length]);binary=data[28+length:]
types={5126:np.dtype('<f4'),5125:np.dtype('<u4'),5123:np.dtype('<u2'),5121:np.dtype('u1')}
def accessor(index):
 a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];dt=types[a['componentType']];columns={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
 return np.ndarray((a['count'],columns),dtype=dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*columns),dt.itemsize)).copy()
report={};resolution=512
for node in doc['nodes']:
 if 'mesh' not in node or node.get('name','').startswith('COL_'):continue
 mesh=doc['meshes'][node['mesh']];counts=np.zeros((resolution,resolution),dtype=np.uint16);triangles=0;degenerate=0
 for primitive in mesh['primitives']:
  uv=accessor(primitive['attributes']['TEXCOORD_1'])*resolution
  indices=accessor(primitive['indices']).ravel().reshape(-1,3)
  assert np.isfinite(uv).all() and uv.min()>=-.01 and uv.max()<=resolution+.01,node['name']
  for ids in indices:
   a,b,c=uv[ids].astype(float);ab=b-a;ac=c-a;det=ab[0]*ac[1]-ab[1]*ac[0];triangles+=1
   if abs(det)<1e-8:degenerate+=1;continue
   lo=np.maximum(np.floor(np.minimum(np.minimum(a,b),c)).astype(int),0);hi=np.minimum(np.ceil(np.maximum(np.maximum(a,b),c)).astype(int),resolution)
   if np.any(hi<=lo):continue
   yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];x=xx+.5-a[0];y=yy+.5-a[1]
   u=(x*ac[1]-y*ac[0])/det;v=(ab[0]*y-ab[1]*x)/det
   inside=(u>1e-6)&(v>1e-6)&(u+v<1-1e-6)
   counts[lo[1]:hi[1],lo[0]:hi[0]]+=inside.astype(np.uint16)
 report[node['name']]={'triangles':triangles,'degenerate_uv_triangles':degenerate,'covered_texels':int((counts>0).sum()),'overlapping_texels':int((counts>1).sum())}
(root/'export/uv2-validation.json').write_text(json.dumps({'resolution':resolution,'scope':'Interior overlap at sampled texel centres; not a gutter or subtexel proof.','meshes':report},indent=2)+'\n')
failures={name:r for name,r in report.items() if r['overlapping_texels']>0}
print('UV2_MESHES',len(report),'OVERLAPPING',failures)
assert not failures
