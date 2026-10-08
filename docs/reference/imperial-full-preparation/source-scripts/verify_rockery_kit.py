"""Check exported rockery geometry, collision identity, LOD ratios and ports."""
from pathlib import Path
import json,struct
R=Path(__file__).resolve().parents[1];report={}
for variant in ['small','medium','large','arch','tunnel','cliff']:
 totals=[];collisions=[]
 for suffix in ['', '_LOD1']:
  path=R/f'export/kits/rockery/KIT_rockery_{variant}{suffix}.glb'
  b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[28+n:]
  def raw(index):
   a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];start=v.get('byteOffset',0)
   return binary[start:start+v['byteLength']]
  render=[node for node in d['nodes'] if 'mesh' in node and not node.get('name','').startswith('COL_')]
  cols=[node for node in d['nodes'] if node.get('name','').startswith('COL_')]
  assert len(render)==1 and len(cols)==1,path
  assert '-colonly' in cols[0]['name'],path
  prim=d['meshes'][render[0]['mesh']]['primitives'];assert len(prim)==1,path
  assert all(k in prim[0]['attributes'] for k in ['TEXCOORD_0','TEXCOORD_1']),path
  totals.append(d['accessors'][prim[0]['indices']]['count']//3)
  cp=d['meshes'][cols[0]['mesh']]['primitives'][0]
  collisions.append((raw(cp['indices']),raw(cp['attributes']['POSITION']),cols[0].get('translation'),cols[0].get('rotation')))
  ports=[node for node in d['nodes'] if node.get('name','').startswith('PORT_')]
  assert len(ports)==(2 if variant in ['arch','tunnel'] else 0),path
  if ports:
   half=.7 if variant=='arch' else 2
   for port in ports:
    expected=[0,0,half if port['name'].startswith('PORT_front') else -half]
    assert all(abs(a-b)<1e-5 for a,b in zip(port.get('translation',[0,0,0]),expected)),(path,port)
 assert 200<=totals[0]<=2000 and .38<=totals[1]/totals[0]<=.42,(variant,totals)
 assert collisions[0]==collisions[1],(variant,'collision changed with LOD')
 report[variant]={'triangles':totals,'lod_ratio':totals[1]/totals[0],'collision_identical':True,'ports_verified':True}
(R/'export/kits/rockery/validation.json').write_text(json.dumps(report,indent=2))
print('ROCKERY_EXPORT_PASS',json.dumps(report))
