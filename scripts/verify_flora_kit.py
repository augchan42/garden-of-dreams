"""Check exported geometry, alpha masking, atlas size, anchors and collider parity."""
import json,struct
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];out=R/'export/kits/flora'
def read(path):
 data=path.read_bytes();assert data[:4]==b'glTF';size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 return json.loads(data[20:20+size])
def stats(doc):
 tris=0;colliders=[]
 for node in doc['nodes']:
  if 'mesh' not in node:continue
  if node['name'].startswith('COL_'):
   colliders.append({k:node.get(k) for k in ('name','translation','rotation','scale')});continue
  for primitive in doc['meshes'][node['mesh']]['primitives']:
   assert 'TEXCOORD_0' in primitive['attributes'] and 'TEXCOORD_1' in primitive['attributes']
   tris+=doc['accessors'][primitive['indices']]['count']//3
   material=doc['materials'][primitive['material']]
   assert material['alphaMode']=='MASK' and material['doubleSided']
   assert abs(material['alphaCutoff']-.45)<1e-6
 assert any(n['name'].startswith('PORT_ground') and n.get('translation',[0,0,0])==[0,0,0] for n in doc['nodes'])
 return tris,colliders
manifest=json.loads((out/'manifest.json').read_text());assert len(manifest['variants'])==8
report={}
for name,item in manifest['variants'].items():
 base,collision0=stats(read(out/f'KIT_flora_{name}.glb'));lod,collision1=stats(read(out/f'KIT_flora_{name}_LOD1.glb'))
 # Blender duplicates may suffix object names, so compare collision transforms only.
 for c in collision0+collision1:c.pop('name')
 assert collision0==collision1 and len(collision0)==item['colliders']
 assert 200<=base<=2000 and .32<=lod/base<=.48
 assert (base,lod)==(item['triangles_lod0'],item['triangles_lod1'])
 report[name]={'lod0':base,'lod1':lod,'ratio':lod/base,'colliders':len(collision0),'alpha_mask':True,'uv_channels':2}
image=Image.open(out/'flora-basecolor.png');assert image.size==(2048,2048) and image.mode=='RGBA'
assert image.getextrema()[3]==(0,255)
(out/'validation.json').write_text(json.dumps({'passed':True,'atlas_size':list(image.size),'variants':report},indent=2)+'\n')
print('FLORA_EXPORT_PASS',len(report),'variants')
