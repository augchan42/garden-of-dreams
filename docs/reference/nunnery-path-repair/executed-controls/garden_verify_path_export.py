from pathlib import Path
import copy,hashlib,json,sys
import numpy as np
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path(json.load(open('/tmp/garden-nunnery-path-candidate.json'))['folder']);sys.path.insert(0,str(repo/'scripts'))
from verify_mountain_export import Glb
old=Glb(repo/'export/garden-of-dreams.glb');new=Glb(root/'export/garden-of-dreams.glb')
for key in ['asset','extensionsUsed','extensionsRequired','extensions','scene','scenes','cameras']:assert old.doc.get(key)==new.doc.get(key),key
assert len(old.doc['nodes'])==len(new.doc['nodes'])
changed=[];triangles=0
for a,b in zip(old.doc['nodes'],new.doc['nodes']):
 assert a==b,('Node/collision/camera/light/marker changed',a.get('name'))
 if 'mesh' not in a:continue
 ma=old.doc['meshes'][a['mesh']];mb=new.doc['meshes'][b['mesh']]
 assert {k:v for k,v in ma.items() if k!='primitives'}=={k:v for k,v in mb.items() if k!='primitives'}
 assert len(ma['primitives'])==len(mb['primitives'])
 for pa,pb in zip(ma['primitives'],mb['primitives']):
  assert {k:v for k,v in pa.items() if k not in ['attributes','indices']}=={k:v for k,v in pb.items() if k not in ['attributes','indices']}
  assert set(pa['attributes'])==set(pb['attributes'])
  ia=old.accessor(pa['indices']).ravel();ib=new.accessor(pb['indices']).ravel();assert len(ia)==len(ib);triangles+=len(ia)//3
  for attr in pa['attributes']:
   va=old.accessor(pa['attributes'][attr])[ia];vb=new.accessor(pb['attributes'][attr])[ib]
   if not np.array_equal(va,vb):
    assert a['name']=='SITE_stage_MAT_plaster_rock',('Unrelated expanded attribute changed',a['name'],attr)
    changed.append(attr)
    if attr=='POSITION':
     delta=np.abs(vb-va);assert np.count_nonzero(np.any(delta>1e-6,axis=1))==36,('Unexpected vertex changes',np.count_nonzero(np.any(delta>1e-6,axis=1)))
     assert np.max(delta[:,0])==0 and np.max(delta[:,1])==0 and np.max(delta[:,2])<1.80001
    else:assert attr in ['TEXCOORD_0','TEXCOORD_1'],attr
assert 'POSITION' in changed
om={m['name']:old.material(m) for m in old.doc['materials']};nm={m['name']:new.material(m) for m in new.doc['materials']};assert om==nm
assert {i['name']:old.image_hash(i) for i in old.doc['images']}=={i['name']:new.image_hash(i) for i in new.doc['images']}
report={'status':'path_export_preservation_passed','before_sha256':hashlib.sha256(old.bytes).hexdigest(),'after_sha256':hashlib.sha256(new.bytes).hexdigest(),'nodes_checked':len(old.doc['nodes']),'triangles_checked':triangles,'changed_node':'SITE_stage_MAT_plaster_rock','changed_attributes':changed,'materials_and_images_unchanged':True,'scope':'Expanded indexed attributes, node/marker/collision/camera/light contracts and all materials/images. Only two rendered slabs change; changed batch UVs require fresh lighting.'}
(root/'export-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print('PATH_EXPORT_PRESERVATION_PASS',report)
