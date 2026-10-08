"""Verify the tile-normal candidate export without accepting stale lighting."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
from verify_canopy_candidate import Document
from verify_mountain_export import Glb
ROOT=Path(__file__).resolve().parents[1]
TARGET='SITE_qinfang-ting_MAT_pavilion_atlas'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--candidate-root',type=Path,required=True)
parser.add_argument('--allow-ridge-shape-change',action='store_true')
args=parser.parse_args();candidate=args.candidate_root
old_path=ROOT/'export/garden-of-dreams.glb';new_path=candidate/'export/garden-of-dreams.glb'
a,b=Document(old_path),Document(new_path)
assert Counter(n['name'] for n in a.data['nodes'])==Counter(n['name'] for n in b.data['nodes'])
assert len(a.nodes)==len(a.data['nodes'])==717
for name in a.nodes:
 if name!=TARGET:assert a.node(name)==b.node(name),('Unrelated resolved GLB node changed',name)
old,new=a.node(TARGET),b.node(TARGET)
old_mesh,new_mesh=old.pop('mesh'),new.pop('mesh');assert old==new
assert len(old_mesh)==len(new_mesh)==1
assert old_mesh[0]['material']==new_mesh[0]['material']
assert old_mesh[0]['indices']['count']==new_mesh[0]['indices']['count']
assert old_mesh[0]['attributes']['NORMAL']!=new_mesh[0]['attributes']['NORMAL']
assert old_mesh[0]['attributes']['TEXCOORD_1']!=new_mesh[0]['attributes']['TEXCOORD_1']
sets=[];areas=[]
for path in [old_path,new_path]:
 glb=Glb(path);node=next(n for n in glb.doc['nodes'] if n.get('name')==TARGET);prim=glb.doc['meshes'][node['mesh']]['primitives'][0]
 p=glb.accessor(prim['attributes']['POSITION']);uv=glb.accessor(prim['attributes']['TEXCOORD_0'])
 sets.append({tuple(row) for row in np.round(np.concatenate([p,uv],axis=1),6)})
 tri=p[glb.accessor(prim['indices']).ravel().reshape(-1,3)]
 areas.append(float(np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1).sum()/2))
maximum_displacement=0.0
if args.allow_ridge_shape_change:
 source_record=json.loads((candidate/'source-preparation.json').read_text())
 assert source_record['source_authoring_sha256']==hashlib.sha256((ROOT/'blender/authoring.blend').read_bytes()).hexdigest()
 assert source_record['candidate_authoring_sha256']==hashlib.sha256((candidate/'blender/authoring.blend').read_bytes()).hexdigest()
 assert 0<len(source_record['ridge_profile']['changed_vertex_indices'])<=630
 groups={}
 for row in sets[0]:groups.setdefault(row[3:],[]).append(row[:3])
 for row in sets[1]-sets[0]:
  assert row[3:] in groups,'Primary UV ownership changed'
  displacement=float(np.linalg.norm(np.array(groups[row[3:]])-np.array(row[:3]),axis=1).min())
  maximum_displacement=max(maximum_displacement,displacement)
 assert maximum_displacement<.03,'Ridge profile moves outside its bounded relief'
 assert {row[3:] for row in sets[0]}=={row[3:] for row in sets[1]}
else:
 assert sets[0]==sets[1],'Positions/primary paint UV pairs changed'
 assert abs(areas[0]-areas[1])<1e-4,'Target surface area changed'
identical=[]
for path in sorted((ROOT/'export/sites').glob('SITE_*.glb')):
 if path.name=='SITE_qinfang-ting.glb':continue
 assert path.read_bytes()==(candidate/'export/sites'/path.name).read_bytes(),path.name
 identical.append(path.name)
assert len(identical)==14
report={'status':'scratch_export_preservation_passed','source_glb_sha256':hashlib.sha256(a.blob).hexdigest(),'candidate_glb_sha256':hashlib.sha256(b.blob).hexdigest(),'unchanged_resolved_node_contracts':716,'changed_mesh':TARGET,'positions_primary_uv_pairs_preserved':len(sets[0]),'target_surface_area':areas,'target_index_count':new_mesh[0]['indices']['count'],'byte_identical_other_site_exports':identical,'scope':'Native source preserves vertex positions/UV ownership and only reverses 336 inward ridge faces. Actual GLB preserves every other resolved node, embedded material/image, camera/collision/light and all fourteen other site exports. Target batch normals/tangents and freshly packed UV2 change; all matching lighting and actual engine art remain required before adoption.'}
if args.allow_ridge_shape_change:
 report.pop('positions_primary_uv_pairs_preserved')
 report['maximum_primary_uv_matched_vertex_displacement_metres']=maximum_displacement
 report['scope']='Separate shallow-cap export preserves all 716 other complete resolved nodes, embedded materials/images, cameras/collision/lights and fourteen other site exports. Native source guards allow only 630 tile-cap positions and 336 reversed faces; target primary UV coordinates remain within the recorded bounded displacement. Target normals/tangents/UV2 change. Fresh whole lighting and actual engine art remain required before adoption.'
(candidate/'export-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print('TILE_RIDGE_EXPORT_PRESERVATION_PASS',716,len(identical),len(sets[0]))
