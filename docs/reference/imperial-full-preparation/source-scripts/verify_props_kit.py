"""Check actual prop geometry, PBR export, connector positions and collision parity."""
import json,struct,math
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];folder=R/'export/kits/props'
def read(path):
 blob=path.read_bytes();assert blob[:4]==b'glTF';size=struct.unpack_from('<I',blob,12)[0];return json.loads(blob[20:20+size])
def inspect(doc):
 tris=0;colliders=[];ports={}
 for node in doc['nodes']:
  name=node.get('name','')
  if name.startswith('PORT_'):
   key=name[5:].split('.')[0];ports[key]=node.get('translation',[0,0,0]);assert node['extras']['connection']=='prop_mount'
  if 'mesh' not in node:continue
  if name.startswith('COL_'):
   assert name.endswith('-colonly');assert node['extras']['collision_only'];colliders.append({k:node.get(k) for k in ['translation','rotation','scale']});continue
  for primitive in doc['meshes'][node['mesh']]['primitives']:
   assert 'TEXCOORD_0' in primitive['attributes'] and 'TEXCOORD_1' in primitive['attributes']
   tris+=doc['accessors'][primitive['indices']]['count']//3
   mat=doc['materials'][primitive['material']];assert mat.get('alphaMode','OPAQUE')=='OPAQUE'
   assert 'baseColorTexture' in mat['pbrMetallicRoughness'] and 'metallicRoughnessTexture' in mat['pbrMetallicRoughness'] and 'emissiveTexture' in mat
   assert not mat.get('doubleSided',False)
 return tris,colliders,ports
manifest=json.loads((folder/'manifest.json').read_text());assert set(manifest['variants'])=={'lantern_hanging','lantern_standing','brazier','stone_table','stone_stool','incense_burner','scroll','screen','folding_chair'}
report={}
for name,item in manifest['variants'].items():
 a,ca,pa=inspect(read(folder/f'KIT_props_{name}.glb'));b,cb,pb=inspect(read(folder/f'KIT_props_{name}_LOD1.glb'))
 assert ca==cb and pa==pb and len(ca)==item['colliders']
 assert 200<=a<=2000 and .35<=b/a<=.46,(name,a,b)
 assert (a,b)==(item['triangles_lod0'],item['triangles_lod1'])
 assert set(pa)==set(item['connectors'])
 for key,p in item['connectors'].items():
  expected=[p[0],p[2],-p[1]];assert all(abs(x-y)<1e-5 for x,y in zip(pa[key],expected))
 report[name]={'lod0':a,'lod1':b,'ratio':b/a,'colliders':len(ca),'ports':pa,'uv_channels':2,'pbr_maps':3}
for kind in ['basecolor','orm','emission']:assert Image.open(R/f'textures/kits/props/props-{kind}.png').size==(2048,2048)
(folder/'validation.json').write_text(json.dumps({'passed':True,'variants':report},indent=2)+'\n');print('PROPS_EXPORT_PASS',len(report),'variants')
