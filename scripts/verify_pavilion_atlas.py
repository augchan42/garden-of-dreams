"""Check the actual glTF PBR bindings, embedded images and material-region UVs."""
from pathlib import Path
import json, struct, io
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--kit',default='pavilion',choices=['pavilion','corridor','wall','rockery']);kit=parser.parse_args().kit
atlas='wall' if kit=='wall' else 'pavilion'
config=json.loads((R/f'textures/atlases/{atlas}/atlas.json').read_text())
regions=[(x,1-y-h,w,h) for x,y,w,h in config['uv_regions'].values()]
report={}
for path in sorted((R/f'export/kits/{kit}').glob('*.glb')):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[28+n:]
 def accessor(index):
  a=d['accessors'][index];v=d['bufferViews'][a['bufferView']]
  dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']]
  width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
  offset=v.get('byteOffset',0)+a.get('byteOffset',0)
  return np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=offset,strides=(v.get('byteStride',np.dtype(dtype).itemsize*width),np.dtype(dtype).itemsize)).copy()
 assert len(d['materials'])==1,path
 mat=d['materials'][0];pbr=mat['pbrMetallicRoughness']
 for binding in [pbr['baseColorTexture'],pbr['metallicRoughnessTexture'],mat['normalTexture']]:
  assert binding.get('texCoord',0)==0,path
 assert len(d['images'])==3,path
 for image in d['images']:
  v=d['bufferViews'][image['bufferView']];start=v.get('byteOffset',0)
  decoded=Image.open(io.BytesIO(binary[start:start+v['byteLength']]))
  assert decoded.size==(2048,2048),(path,image)
  source=Image.open(R/f'textures/atlases/{atlas}'/f"{image['name']}.png")
  assert np.max(np.abs(np.asarray(decoded.convert('RGB'),dtype=int)-np.asarray(source.convert('RGB'),dtype=int)))<=1,(path,image['name'])
 triangles=0
 for node in d['nodes']:
  if 'mesh' not in node or node.get('name','').startswith('COL_'):continue
  primitives=d['meshes'][node['mesh']]['primitives'];assert len(primitives)==1,path
  prim=primitives[0];uv=accessor(prim['attributes']['TEXCOORD_0']);indices=accessor(prim['indices']).reshape(-1,3)
  assert 'TEXCOORD_1' in prim['attributes']
  for tri in indices:
   points=uv[tri]
   assert any(np.all(points[:,0]>=x-1e-5) and np.all(points[:,0]<=x+w+1e-5) and np.all(points[:,1]>=y-1e-5) and np.all(points[:,1]<=y+h+1e-5) for x,y,w,h in regions),(path,points)
  triangles+=len(indices)
 report[path.stem]={'materials':1,'images':3,'size':2048,'triangles_checked':triangles,'all_triangles_within_material_regions':True}
(R/f'export/kits/{kit}/atlas-validation.json').write_text(json.dumps(report,indent=2))
print(kit.upper()+'_ATLAS_PASS',len(report),'assets, PBR bindings, source pixels, UV regions and one render primitive')
