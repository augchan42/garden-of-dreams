"""Check stage exports, PBR/alpha modes, anchors and exact collider parity."""
import json,struct,math
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];folder=R/'export/kits/stage'
def read(path):
 data=path.read_bytes();assert data[:4]==b'glTF';size=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+size])
def inspect(doc,variant):
 triangles=0;colliders=[];ports={};surfaces=0
 for node in doc['nodes']:
  name=node.get('name','')
  if name.startswith('PORT_'):
   ports[name[5:].split('.')[0]]=node.get('translation',[0,0,0]);assert node['extras']['connection']=='stage_mount'
  if 'mesh' not in node:continue
  if name.startswith('COL_'):
   assert name.endswith('-colonly') and node['extras']['collision_only'];colliders.append({k:node.get(k) for k in ['translation','rotation','scale']});continue
  for primitive in doc['meshes'][node['mesh']]['primitives']:
   surfaces+=1;attrs=primitive['attributes'];assert 'TEXCOORD_0' in attrs and 'TEXCOORD_1' in attrs
   triangles+=doc['accessors'][primitive['indices']]['count']//3
   mat=doc['materials'][primitive['material']];m=mat['name'].split('.')[0];mode=mat.get('alphaMode','OPAQUE')
   if m in ['MAT_stage_fog','MAT_stage_gel']:assert mode=='BLEND' and mat.get('doubleSided',False)
   else:assert mode=='OPAQUE' and not mat.get('doubleSided',False)
   if m=='MAT_stage_atlas':assert 'baseColorTexture' in mat['pbrMetallicRoughness'] and 'metallicRoughnessTexture' in mat['pbrMetallicRoughness']
   if m.startswith('MAT_stage_cyclorama_'):
    assert 'emissiveTexture' in mat
    assert all(abs(v-.6)<1e-5 for v in mat['emissiveFactor'])
   if m=='MAT_stage_backstage':assert mat['pbrMetallicRoughness']['baseColorFactor'][:3]==[0,0,0]
 return triangles,colliders,ports,surfaces
manifest=json.loads((folder/'manifest.json').read_text());expected={'cyclorama_moonlit','cyclorama_dusk','cyclorama_mist','studio_wall','floor_boards','fog_plane','gel_frame'};assert set(manifest['variants'])==expected
report={}
for name,item in manifest['variants'].items():
 a,ca,pa,sa=inspect(read(folder/f'KIT_stage_{name}.glb'),name);b,cb,pb,sb=inspect(read(folder/f'KIT_stage_{name}_LOD1.glb'),name)
 assert ca==cb and pa==pb and sa==sb==item['surfaces']
 assert len(ca)==item['colliders'];assert 200<=a<=2000 and .35<=b/a<=.46,(name,a,b)
 assert (a,b)==(item['triangles_lod0'],item['triangles_lod1'])
 for key,p in item['connectors'].items():assert all(abs(x-y)<1e-5 for x,y in zip(pa[key],[p[0],p[2],-p[1]]))
 report[name]={'lod0':a,'lod1':b,'ratio':b/a,'colliders':len(ca),'surfaces':sa,'connectors':pa}
for name in ['moonlit','dusk','mist']:assert Image.open(R/f'textures/kits/stage/cyclorama-{name}.png').size==(4096,4096)
for name in ['basecolor','orm']:assert Image.open(R/f'textures/kits/stage/stage-{name}.png').size==(2048,2048)
(folder/'validation.json').write_text(json.dumps({'passed':True,'variants':report},indent=2)+'\n');print('STAGE_EXPORT_PASS',len(report),'variants')
