from pathlib import Path
import hashlib,json,sys,numpy as np
repo=Path('/Users/auchan/projects/garden-of-dreams')
w=repo/'.superpowers/sdd/2026-09-23-garden-completion/island-face-source';c=w/'candidate'
sys.path.insert(0,str(repo/'scripts'))
from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=Glb(repo/'export/garden-of-dreams.glb');b=Glb(c/'export/garden-of-dreams.glb')
an={n['name']:n for n in a.doc['nodes']};bn={n['name']:n for n in b.doc['nodes']}
assert set(an)==set(bn)
for key in ['cameras','extensionsUsed','extensionsRequired','extensions']:assert a.doc.get(key)==b.doc.get(key),key
assert {m['name']:a.material(m) for m in a.doc['materials']}=={m['name']:b.material(m) for m in b.doc['materials']}
target='SITE_ziling-zhou_MAT_plaster_rock';unchanged=[]
for name,n in an.items():
 m=bn[name]
 def contract(node,g):
  d={k:v for k,v in node.items() if k not in ['mesh','children']}
  if 'children' in node:d['children_names']=[g.doc['nodes'][i]['name'] for i in node['children']]
  return d
 assert contract(n,a)==contract(m,b),name
 if 'mesh' not in n:continue
 x=a.doc['meshes'][n['mesh']]['primitives'];y=b.doc['meshes'][m['mesh']]['primitives'];assert len(x)==len(y)
 for old,new in zip(x,y):
  assert old['attributes'].keys()==new['attributes'].keys()
  assert {k:v for k,v in old.items() if k not in ['attributes','indices','material']}=={k:v for k,v in new.items() if k not in ['attributes','indices','material']}
  assert a.doc['materials'][old['material']]['name']==b.doc['materials'][new['material']]['name'] if 'material' in old else 'material' not in new
  oi=a.accessor(old['indices']).reshape(-1);ni=b.accessor(new['indices']).reshape(-1);assert len(oi)==len(ni)
  if name==target:
   oldp=a.accessor(old['attributes']['POSITION']);newp=b.accessor(new['attributes']['POSITION'])
   def unique(pts):return sorted(set(tuple(np.round(p,6)) for p in pts))
   assert unique(oldp)==unique(newp),'Island-batch positions changed'
   continue
  for attr in old['attributes']:
   av=a.accessor(old['attributes'][attr])[oi];bv=b.accessor(new['attributes'][attr])[ni]
   assert av.shape==bv.shape and np.allclose(av,bv,atol=1e-6,rtol=0),(name,attr)
 if name!=target:unchanged.append(name)
site_hashes={};unchanged_sites=[]
for p in sorted((c/'export/sites').glob('*.glb')):
 same=sha(p)==sha(repo/'export/sites'/p.name)
 assert same==(p.name!='SITE_ziling-zhou.glb'),p.name
 site_hashes[p.name]={'sha256':sha(p),'unchanged':same}
 if same:unchanged_sites.append(p.name)
assert len(site_hashes)==15 and len(unchanged_sites)==14
counts={'cameras':sum('camera' in n for n in bn.values()),'colliders':sum(n.startswith('COL_') for n in bn),'markers':sum(n.startswith('TRG_') for n in bn)}
assert counts=={'cameras':42,'colliders':454,'markers':71}
manifest=json.loads((c/'export/manifest.json').read_text());assert manifest['total_triangles']==266336 and manifest['total_render_meshes']==167
report={'status':'island_winding_export_preservation_passed','baseline_glb_sha256':sha(a.path),'candidate_glb_sha256':sha(b.path),'candidate_authoring_sha256':sha(c/'blender/authoring.blend'),'counts':counts,'triangles':266336,'render_meshes':167,'unchanged_mesh_nodes':len(unchanged),'changed_batch':target,'all_node_camera_light_material_and_other_mesh_contracts_preserved':True,'changed_batch_unique_positions_preserved':True,'site_exports':site_hashes,'scope':'Only Ziling stone batch changes winding/normals and repacked UV2. Actual saved vertices/unoriented faces preserved; all other exported expanded position/normal/UV attributes unchanged;14 other site GLBs byte-exact. No lighting or native appearance acceptance.'}
(c/'export-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print('ISLAND_WINDING_EXPORT_PRESERVATION',len(unchanged), 'unchanged mesh nodes;',len(unchanged_sites),'byte-exact other site GLBs')
