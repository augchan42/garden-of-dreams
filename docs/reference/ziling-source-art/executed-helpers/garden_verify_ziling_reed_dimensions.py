"""Measure actual exported full-detail plants and their installed lower-detail kit."""
from pathlib import Path
import json,sys,hashlib,datetime,numpy as np
from scipy.spatial import cKDTree
r=Path('/Users/auchan/projects/garden-of-dreams')
w=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-source-art'
sys.path.insert(0,str(r/'scripts'))
from verify_mountain_export import Glb
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=Glb(w/'reeds-volume/export/garden-of-dreams.glb')
kits=[Glb(w/'reeds-volume/export/kits/flora'/('KIT_flora_reed'+suffix+'.glb')) for suffix in ['', '_LOD1']]
def vertices(glb,mesh):
 return np.concatenate([glb.accessor(p['attributes']['POSITION']) for p in mesh['primitives']])
def world(node,points):
 x,y,z,a=node.get('rotation',[0,0,0,1])
 rotation=np.array([[1-2*(y*y+z*z),2*(x*y-z*a),2*(x*z+y*a)],[2*(x*y+z*a),1-2*(x*x+z*z),2*(y*z-x*a)],[2*(x*z-y*a),2*(y*z+x*a),1-2*(x*x+y*y)]])
 assert 'matrix' not in node
 return (points*np.array(node.get('scale',[1,1,1])))@rotation.T+np.array(node.get('translation',[0,0,0]))
rows=[]
for i,node in enumerate(source.doc['nodes']):
 if not node.get('name','').startswith('HERO_flora_ziling_zhou_'):continue
 assert i in source.doc['scenes'][source.doc['scene']]['nodes']
 assert not any(i in p.get('children',[]) for p in source.doc['nodes'])
 actual=vertices(source,source.doc['meshes'][node['mesh']]);base=vertices(kits[0],kits[0].doc['meshes'][0])
 # Both directions establish the same point set, independent of UV-seam duplication.
 error=max(float(cKDTree(actual).query(base)[0].max()),float(cKDTree(base).query(actual)[0].max()))
 assert error<=1e-6,(node['name'],error)
 for lod,kit in enumerate(kits):
  local=actual if lod==0 else vertices(kit,kit.doc['meshes'][0]);points=world(node,local)
  height=float(np.ptp(points[:,1]));assert .8<=height<=1.6,(node['name'],lod,height)
  rows.append({'node':node['name'],'lod':lod,'height_m':height,'world_min':points.min(axis=0).tolist(),'world_max':points.max(axis=0).tolist(),'full_source_to_kit_point_set_max_error':error})
assert len(rows)==20
report={'status':'all_ten_reed_placements_both_details_within_spec_height','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':sha(source.path),'kit_sha256':[sha(k.path) for k in kits],'site_sheet_sha256':sha(r/'docs/sites/ziling-zhou.md'),'requirement':'Reeds 0.8–1.6 metres, from docs/sites/ziling-zhou.md.','rows':rows,'scope':'Actual assembly base meshes and current lower-detail kit measured in each exported plant transform. All root nodes and full/kit point sets checked. Does not establish native LOD switching, final botanical appearance, lighting, walking clearance or phone budgets.'}
(w/'reed-dimension-contract.json').write_text(json.dumps(report,indent=2)+'\n')
print('REED_DIMENSION_CONTRACT_PASS_20',min(x['height_m'] for x in rows),max(x['height_m'] for x in rows))
