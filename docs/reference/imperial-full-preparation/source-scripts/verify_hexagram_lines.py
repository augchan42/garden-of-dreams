"""Verify both real mesh variants of every table slot in the exported garden."""
from pathlib import Path
import json,struct
import numpy as np
R=Path(__file__).resolve().parents[1]
b=(R/'export/garden-of-dreams.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);binary=b[28+n:]
def accessor(index):
 a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]);cols={'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']]
 return np.ndarray((a['count'],cols),dtype=dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*cols),dt.itemsize)).copy()
nodes=[n for n in doc['nodes'] if n.get('name','').startswith('HERO_table_line_')];assert len(nodes)==12
for i in range(1,7):
 for variant in ['solid','broken']:
  matches=[n for n in nodes if n['name'].split('.')[0]==f'HERO_table_line_{i}_{variant}'];assert len(matches)==1,(i,variant)
  node=matches[0];assert node['extras']['line_index']==i and node['extras']['variant']==variant
  primitives=doc['meshes'][node['mesh']]['primitives'];assert len(primitives)==1
  p=primitives[0];pos=accessor(p['attributes']['POSITION']);ids=accessor(p['indices']).reshape(-1,3)
  assert len(ids)==(12 if variant=='solid' else 24)
  assert all(k in p['attributes'] for k in ['TEXCOORD_0','TEXCOORD_1'])
  assert np.allclose([pos[:,0].min(),pos[:,0].max()],[-.325,.325],atol=1e-5)
  assert np.allclose([pos[:,1].min(),pos[:,1].max()],[.901,.919],atol=1e-5)
  assert abs(float(pos[:,2].mean())-(.35-(i-1)*.14))<1e-5
  if variant=='broken':
   assert np.all(np.abs(pos[:,0])>=.11-1e-5)
   assert all(np.all(pos[tri,0]<0) or np.all(pos[tri,0]>0) for tri in ids)
print('HEXAGRAM_EXPORT_PASS: twelve bronze meshes, six ordered slots, identical outer bounds and open broken-line gaps')
