"""Verify each exported wall variant's actual geometry, LOD and connectors."""
from pathlib import Path
import json, struct
R=Path(__file__).resolve().parents[1]
expected={v:({'front':(0,0,.5),'back':(0,0,-.5)} if v in ['moon_gate','vase_gate'] else {}) for v in ['bay','moon_gate','vase_gate','window_square','window_diamond','window_ice','window_hex','roof_cap']}
report={}
for variant,ports in expected.items():
 totals=[];collisions=[]
 for suffix in ['', '_LOD1']:
  p=R/'export/kits/wall'/f'KIT_wall_{variant}{suffix}.glb'
  b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);tris=0;cols=[];collision_tris=0
  for node in d['nodes']:
   name=node.get('name','')
   if name.startswith('PORT_'):
    key=next((k for k in ports if name.startswith('PORT_'+k)),None);assert key,(p,name)
    assert all(abs(x-y)<1e-5 for x,y in zip(node.get('translation',[0,0,0]),ports[key])),(p,node)
    assert node.get('extras',{}).get('connection')=='wall_gate'
   if name.startswith('COL_'):
    assert '-colonly' in name,(p,name)
    collision_tris+=sum(d['accessors'][prim['indices']]['count']//3 for prim in d['meshes'][node['mesh']]['primitives'])
    cols.append((name.split('-colonly')[0].split('.')[0],node.get('translation'),node.get('rotation')))
   elif 'mesh' in node:
    for prim in d['meshes'][node['mesh']]['primitives']:
     assert 'TEXCOORD_0' in prim['attributes'] and 'TEXCOORD_1' in prim['attributes']
     tris+=d['accessors'][prim['indices']]['count']//3
  assert len([x for x in d['nodes'] if x.get('name','').startswith('PORT_')])==len(ports)
  assert len(cols)==1,(p,len(cols))
  totals.append(tris);collisions.append(cols)
 assert 200<=totals[0]<=2000,(variant,totals)
 assert .38<=totals[1]/totals[0]<=.42,(variant,totals)
 assert sorted(map(str,collisions[0]))==sorted(map(str,collisions[1])),variant
 report[variant]={'lod0_triangles':totals[0],'lod1_triangles':totals[1],'ratio':totals[1]/totals[0],'colliders':len(collisions[0]),'collision_triangles':collision_tris,'ports':ports}
(R/'export/kits/wall/validation.json').write_text(json.dumps(report,indent=2))
print('WALL_EXPORT_PASS',json.dumps(report))
