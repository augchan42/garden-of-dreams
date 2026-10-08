from pathlib import Path
import json,sys,hashlib,numpy as np
from collections import Counter
sys.path.insert(0,'/Users/auchan/projects/garden-of-dreams/scripts')
from verify_canopy_candidate import Document
from verify_mountain_export import Glb
w=Path(json.load(open('/tmp/garden-tile-ridge-candidate.json'))['folder']);old=Path(json.load(open('/tmp/garden-shallow-tile-candidate.json'))['folder'])
paths=[old/'export/garden-of-dreams.glb',w/'export/garden-of-dreams.glb'];docs=[Document(p) for p in paths];target='SITE_qinfang-ting_MAT_pavilion_atlas'
for name in docs[0].nodes:
 if name!=target:assert docs[0].node(name)==docs[1].node(name),name
triangles=[];attributes=None
for path in paths:
 g=Glb(path);node=next(n for n in g.doc['nodes'] if n.get('name')==target);prim=g.doc['meshes'][node['mesh']]['primitives'][0]
 current=sorted(k for k in prim['attributes'] if k!='TEXCOORD_1')
 if attributes is None:attributes=current
 assert attributes==current
 keys=np.concatenate([g.accessor(prim['attributes'][k]) for k in attributes],axis=1)
 tri=g.accessor(prim['indices']).reshape(-1,3)
 triangles.append(Counter(tuple(sorted(tuple(v) for v in keys[row])) for row in tri))
assert triangles[0]==triangles[1],'Non-UV2 triangle data changed'
record={'status':'uv2_only_delta_passed','previous_glb_sha256':hashlib.sha256(paths[0].read_bytes()).hexdigest(),'candidate_glb_sha256':hashlib.sha256(paths[1].read_bytes()).hexdigest(),'other_resolved_nodes':716,'target_triangles_preserving_non_uv2_attributes':sum(triangles[0].values()),'preserved_attributes':attributes,'scope':'Exact unordered triangle vertex contracts against preceding shallow-cap export. Target UV2 is sole intended delta; no lighting or art acceptance.'}
(w/'uv2-only-preservation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
