from pathlib import Path
import json,sys,hashlib,numpy as np
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root']);out=w/'reeds';sys.path.insert(0,str(r/'scripts'));from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=Glb(w/'waterline/export/garden-of-dreams.glb');b=Glb(out/'export/garden-of-dreams.glb');review=json.loads((out/'reed-source-review.json').read_text());allowed={name+'.001' for name in review['changed_scene_objects']};assert allowed.issubset({node['name'] for node in a.doc['nodes']});changed=[];counts={};tris=0
assert len(a.doc['nodes'])==len(b.doc['nodes'])==717
for old,new in zip(a.doc['nodes'],b.doc['nodes']):
 assert old==new,('Unexpected node/collider/camera/light change',old['name'])
 if 'mesh' not in old:continue
 p,q=a.doc['meshes'][old['mesh']],b.doc['meshes'][new['mesh']];name=old['name'];assert len(p['primitives'])==len(q['primitives']);dif=[];ct=0
 for x,y in zip(p['primitives'],q['primitives']):
  assert {k:v for k,v in x.items() if k not in ['attributes','indices']}=={k:v for k,v in y.items() if k not in ['attributes','indices']};assert x['attributes'].keys()==y['attributes'].keys()
  ix=a.accessor(x['indices']).ravel();iy=b.accessor(y['indices']).ravel();tris+=len(iy)//3;ct+=len(iy)//3
  for attr in x['attributes']:
   if not np.array_equal(a.accessor(x['attributes'][attr])[ix],b.accessor(y['attributes'][attr])[iy]):dif.append(attr)
 if dif:assert name in allowed,name;changed.append({'name':name,'changed_attributes':sorted(set(dif))});counts[name]=ct
 else:assert p==q or {k:v for k,v in p.items() if k!='primitives'}=={k:v for k,v in q.items() if k!='primitives'},name
assert {v['name'] for v in changed}==allowed and all(v==1008 for v in counts.values())
for key in ['asset','extensionsUsed','extensionsRequired','extensions','scene','scenes','cameras','animations','skins','samplers']:assert a.doc.get(key)==b.doc.get(key),key
assert {m['name']:a.material(m) for m in a.doc['materials']}=={m['name']:b.material(m) for m in b.doc['materials']}
assert {m['name']:a.image_hash(m) for m in a.doc['images']}=={m['name']:b.image_hash(m) for m in b.doc['images']}
assert [a.texture(i) for i in range(len(a.doc['textures']))]==[b.texture(i) for i in range(len(b.doc['textures']))]
exact=[]
for p in sorted((out/'export/sites').glob('*.glb')):
 if p.name!='SITE_ziling-zhou.glb':assert p.read_bytes()==(w/'waterline/export/sites'/p.name).read_bytes(),p.name;exact.append(p.name)
for p in sorted((r/'export/kits/flora').glob('*.glb')):
 if p.name not in ['KIT_flora_reed.glb','KIT_flora_reed_LOD1.glb']:assert p.read_bytes()==(out/'export/kits/flora'/p.name).read_bytes(),p.name
assert sha(out/'export/kits/flora/flora-basecolor.png')==sha(r/'export/kits/flora/flora-basecolor.png')
(out/'export-preservation.json').write_text(json.dumps({'status':'controlled_reed_export_preserved','baseline_waterline_sha256':sha(w/'waterline/export/garden-of-dreams.glb'),'candidate_sha256':sha(out/'export/garden-of-dreams.glb'),'expanded_indexed_triangles':tris,'changed_meshes':changed,'reed_triangles_per_placement':counts,'unchanged_waterline_site_exports_byte_identical':exact,'unchanged_other_flora_glbs':14,'scope':'Exactly ten reed mesh POSITION/NORMAL/UV channels change. All717 node records/transforms, non-reed geometry, source materials/images/textures/lights/cameras/colliders unchanged from separate waterline candidate. Other14site exports and14non-reed flora GLBs byte-identical, original atlas bytes retained. Native/fresh lighting/physics/adoption pending.'},indent=2)+'\n');print('CONTROLLED_REED_EXPORT_PASS',len(changed),'reed meshes',tris,'indexed triangles',sha(out/'export/garden-of-dreams.glb'))
verify=(r/'scripts/verify_flora_kit.py').read_text().replace("R=Path(__file__).resolve().parents[1]",'R=Path('+repr(str(out))+')');executed=out/'executed-verify-flora.py';executed.write_text(verify);exec(compile(verify,str(executed),'exec'))
