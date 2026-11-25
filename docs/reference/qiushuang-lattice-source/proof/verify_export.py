"""Check one intended lattice batch and exact expanded data elsewhere."""
from pathlib import Path
import sys,json,hashlib,numpy as np
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path('/tmp/garden-qiushuang-lattice-20261010');sys.path.insert(0,str(repo/'scripts'))
from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=Glb(repo/'export/garden-of-dreams.glb');b=Glb(root/'export/garden-of-dreams.glb')
target='SITE_qiushuang-zhai_MAT_lattice_wood'
assert a.doc['nodes']==b.doc['nodes']
for key in ['asset','scene','scenes','cameras','extensions','extensionsUsed','extensionsRequired','samplers']:assert a.doc.get(key)==b.doc.get(key),key
assert {m['name']:a.material(m) for m in a.doc['materials']}=={m['name']:b.material(m) for m in b.doc['materials']}
assert {m['name']:a.image_hash(m) for m in a.doc['images']}=={m['name']:b.image_hash(m) for m in b.doc['images']}
changed=[];preserved=[];triangles=0
for previous,current in zip(a.doc['nodes'],b.doc['nodes']):
 if 'mesh' not in previous:continue
 old=a.doc['meshes'][previous['mesh']];new=b.doc['meshes'][current['mesh']];name=previous['name']
 assert {k:v for k,v in old.items() if k!='primitives'}=={k:v for k,v in new.items() if k!='primitives'},name
 assert len(old['primitives'])==len(new['primitives'])
 for x,y in zip(old['primitives'],new['primitives']):
  assert {k:v for k,v in x.items() if k not in ['indices','attributes']}=={k:v for k,v in y.items() if k not in ['indices','attributes']},name
  assert x['attributes'].keys()==y['attributes'].keys()
  ix=a.accessor(x['indices']).ravel();iy=b.accessor(y['indices']).ravel();assert len(ix)==len(iy),name
  if not name.startswith('COL_'):triangles+=len(iy)//3
  for attr in x['attributes']:
   av=a.accessor(x['attributes'][attr])[ix];bv=b.accessor(y['attributes'][attr])[iy]
   assert np.isfinite(bv).all(),(name,attr)
   if name!=target or attr not in ['POSITION','TEXCOORD_1']:assert np.array_equal(av,bv),(name,attr)
  if name==target:assert not np.array_equal(a.accessor(x['attributes']['POSITION'])[ix],b.accessor(y['attributes']['POSITION'])[iy])
 (changed if name==target else preserved).append(name)
assert changed==[target] and triangles==264973
unchanged_sites=[]
for path in (repo/'export/sites').glob('*.glb'):
 if path.stem!='SITE_qiushuang-zhai':
  assert path.read_bytes()==(root/'export/sites'/path.name).read_bytes(),path.name;unchanged_sites.append(path.name)
assert len(unchanged_sites)==14
report={'status':'lattice_export_preservation_passed','baseline_glb_sha256':sha(repo/'export/garden-of-dreams.glb'),'candidate_glb_sha256':sha(root/'export/garden-of-dreams.glb'),'changed_batches':changed,'unchanged_meshes':len(preserved),'unchanged_site_glbs':unchanged_sites,'triangles':triangles,'render_meshes':sum('mesh' in n and not n['name'].startswith('COL_') for n in b.doc['nodes']),'cameras':len(b.doc['cameras']),'colliders':sum(n['name'].startswith('COL_') for n in b.doc['nodes']),'markers':sum(n['name'].startswith('TRG_') for n in b.doc['nodes']),'scope':'Only Qiushuang lattice batch positions and freshly repacked UV2 may differ; all other expanded attributes, nodes, transforms, images and materials exact.'}
(root/'export-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print('QIUSHUANG_EXPORT_PRESERVATION_PASS',triangles,len(preserved),changed)
