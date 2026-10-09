from pathlib import Path
import sys,json,hashlib,numpy as np
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root'])/'waterline';sys.path.insert(0,str(r/'scripts'));from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=Glb(r/'export/garden-of-dreams.glb');b=Glb(w/'export/garden-of-dreams.glb');assert len(a.doc['nodes'])==len(b.doc['nodes'])==717
allowed={'SITE_qinfang-ting_MAT_water','SITE_ouxiang-xie_MAT_foliage_card','SITE_ziling-zhou_MAT_foliage_card'};changed=[];tris=0
for x,y in zip(a.doc['nodes'],b.doc['nodes']):
 assert x['name']==y['name']
 if x!=y:
  assert x['name'] in allowed,x['name'];assert {k:v for k,v in x.items() if k!='translation'}=={k:v for k,v in y.items() if k!='translation'}
  delta=np.array(y.get('translation',[0,0,0]))-np.array(x.get('translation',[0,0,0]));assert np.allclose(delta,[0,.7,0],atol=1e-6);changed.append({'name':x['name'],'translation_delta_y_up':delta.tolist()})
 if 'mesh' not in x:continue
 p,q=a.doc['meshes'][x['mesh']],b.doc['meshes'][y['mesh']];assert {k:v for k,v in p.items() if k!='primitives'}=={k:v for k,v in q.items() if k!='primitives'};assert len(p['primitives'])==len(q['primitives'])
 for u,v in zip(p['primitives'],q['primitives']):
  assert {k:t for k,t in u.items() if k not in ['attributes','indices']}=={k:t for k,t in v.items() if k not in ['attributes','indices']};assert u['attributes'].keys()==v['attributes'].keys()
  ix=a.accessor(u['indices']).ravel();iy=b.accessor(v['indices']).ravel();assert len(ix)==len(iy);tris+=len(iy)//3
  for attr in u['attributes']:assert np.array_equal(a.accessor(u['attributes'][attr])[ix],b.accessor(v['attributes'][attr])[iy]),(x['name'],attr)
assert {v['name'] for v in changed}==allowed
ma={m['name']:a.material(m) for m in a.doc['materials']};mb={m['name']:b.material(m) for m in b.doc['materials']};assert ma.keys()==mb.keys();colorchanges=[]
for name in ma:
 if ma[name]!=mb[name]:
  assert name in ['MAT_water','MAT_aojing_water'];old=ma[name]['pbrMetallicRoughness']['baseColorFactor'];new=mb[name]['pbrMetallicRoughness']['baseColorFactor'];check=json.loads(json.dumps(mb[name]));check['pbrMetallicRoughness']['baseColorFactor']=old;assert check==ma[name];colorchanges.append({'name':name,'before':old,'after':new})
assert len(colorchanges)==2
for key in ['asset','extensionsUsed','extensionsRequired','extensions','scene','scenes','cameras','animations','skins','samplers']:assert a.doc.get(key)==b.doc.get(key),key
assert {m['name']:a.image_hash(m) for m in a.doc['images']}=={m['name']:b.image_hash(m) for m in b.doc['images']}
assert [a.texture(i) for i in range(len(a.doc['textures']))]==[b.texture(i) for i in range(len(b.doc['textures']))]
unchanged=[]
for p in sorted((w/'export/sites').glob('*.glb')):
 old=r/'export/sites'/p.name
 if p.name not in ['SITE_qinfang-ting.glb','SITE_ouxiang-xie.glb','SITE_ziling-zhou.glb','SITE_aojing-guan.glb']:assert old.read_bytes()==p.read_bytes(),p.name;unchanged.append(p.name)
assert len(unchanged)==11
(w/'export-preservation.json').write_text(json.dumps({'status':'controlled_stream_waterline_export_preserved','baseline_sha256':sha(r/'export/garden-of-dreams.glb'),'candidate_sha256':sha(w/'export/garden-of-dreams.glb'),'expanded_indexed_triangles':tris,'changed_nodes':changed,'changed_materials':colorchanges,'unchanged_site_exports_byte_identical':unchanged,'scope':'All717 node identities, geometry/normal/UV channels, images/textures, camera/light/marker/collider contracts retained. Exactly stream and two combined lotus-batch transforms move0.7m up; two water base colors change. Eleven site exports byte-identical. Native unbaked comparison and fresh matching lighting pending; not production acceptance.'},indent=2)+'\n')
print('CONTROLLED_WATERLINE_EXPORT_PASS',tris,'indexed triangles',len(changed),'node transforms',len(colorchanges),'colors',len(unchanged),'exact site exports',sha(w/'export/garden-of-dreams.glb'))
