from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
repo=Path('/Users/auchan/projects/garden-of-dreams');sys.path.insert(0,str(repo/'scripts'))
from verify_mountain_export import Glb
work=Path(json.loads(Path('/tmp/garden-hengwu-compact-rock.json').read_text())['root']).resolve()
a=Glb(repo/'godot/assets/garden-of-dreams.glb');b=Glb(work/'export/garden-of-dreams.glb')
allowed_mesh={'SITE_hengwu-yuan_MAT_plaster_rock','COL_hengwu_rock-colonly'}
allowed_node={'COL_hengwu_rock-colonly'}
assert len(a.doc['nodes'])==len(b.doc['nodes'])
changed_nodes=[];changed_meshes=[];triangles=0
for old,new in zip(a.doc['nodes'],b.doc['nodes']):
 assert old['name']==new['name']
 if old!=new:
  assert old['name'] in allowed_node,(old['name'],'Unexpected node change');assert {k:v for k,v in old.items() if k not in ['translation','scale']}=={k:v for k,v in new.items() if k not in ['translation','scale']};changed_nodes.append({'name':old['name'],'before':old,'after':new})
 if 'mesh' not in old:continue
 x=a.doc['meshes'][old['mesh']];y=b.doc['meshes'][new['mesh']];name=old['name']
 assert {k:v for k,v in x.items() if k!='primitives'}=={k:v for k,v in y.items() if k!='primitives'}
 assert len(x['primitives'])==len(y['primitives'])
 differences=[]
 for p,q in zip(x['primitives'],y['primitives']):
  assert {k:v for k,v in p.items() if k not in ['attributes','indices']}=={k:v for k,v in q.items() if k not in ['attributes','indices']},(name,'Binding change')
  assert p['attributes'].keys()==q['attributes'].keys()
  ix=a.accessor(p['indices']).ravel();iy=b.accessor(q['indices']).ravel();triangles+=len(iy)//3
  for attr in p['attributes']:
   equal=np.array_equal(a.accessor(p['attributes'][attr])[ix],b.accessor(q['attributes'][attr])[iy])
   if not equal:assert name in allowed_mesh,(name,attr);differences.append(attr)
 if differences:changed_meshes.append({'name':name,'changed_attributes':sorted(set(differences))})
for key in ['asset','extensionsUsed','extensionsRequired','extensions','scene','scenes','cameras','animations','skins','samplers']:
 assert a.doc.get(key)==b.doc.get(key),key
assert {m['name']:a.material(m) for m in a.doc['materials']}=={m['name']:b.material(m) for m in b.doc['materials']}
assert {m['name']:a.image_hash(m) for m in a.doc['images']}=={m['name']:b.image_hash(m) for m in b.doc['images']}
assert [a.texture(i) for i in range(len(a.doc['textures']))]==[b.texture(i) for i in range(len(b.doc['textures']))]
assert {x['name'] for x in changed_meshes}=={'SITE_hengwu-yuan_MAT_plaster_rock'}
assert len(changed_nodes)==1
unchanged=[]
for path in (work/'export/sites').glob('*.glb'):
 previous=repo/'export/sites'/path.name
 if path.name!='SITE_hengwu-yuan.glb':assert previous.read_bytes()==path.read_bytes(),path.name;unchanged.append(path.name)
assert len(unchanged)==14
report={'status':'controlled_hengwu_rock_export_preserved','source_sha256':hashlib.sha256(a.bytes).hexdigest(),'candidate_sha256':hashlib.sha256(b.bytes).hexdigest(),'expanded_indexed_triangles':triangles,'changed_nodes':changed_nodes,'changed_meshes':changed_meshes,'unchanged_site_exports_byte_identical':unchanged,'scope':'Only Hengwu plaster batch geometry/normals/UV2 and first rock collider transform differ. Other node/camera/light/material/image/texture and expanded geometry contracts retained. Fresh lighting, native visual/physics acceptance and adoption remain pending.'}
(work/'export-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
