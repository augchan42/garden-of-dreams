"""Verify the scratch imperial export changes only target UV2 ownership."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path('/Users/auchan/projects/garden-of-dreams')
sys.path.insert(0,str(ROOT/'scripts'))
from verify_canopy_candidate import Document
from verify_mountain_export import Glb
folder=Path(json.loads(Path('/tmp/garden-imperial-roof-probe.json').read_text())['folder'])
target='SITE_daguan-lou_MAT_rooftile'
paths=[ROOT/'export/garden-of-dreams.glb',folder/'export/garden-of-dreams.glb']
a,b=[Document(path) for path in paths]
assert set(a.nodes)==set(b.nodes) and len(a.nodes)==717
for name in a.nodes:
    if name!=target:assert a.node(name)==b.node(name),('Unrelated node differs',name)
old,new=a.node(target),b.node(target)
ma,mb=old.pop('mesh'),new.pop('mesh')
assert old==new and len(ma)==len(mb)==1
assert ma[0]['material']==mb[0]['material']
assert ma[0]['attributes']['TEXCOORD_1']!=mb[0]['attributes']['TEXCOORD_1']
triangles=[];sampling=[]
for path in paths:
    glb=Glb(path)
    node=next(n for n in glb.doc['nodes'] if n.get('name')==target)
    prim=glb.doc['meshes'][node['mesh']]['primitives'][0]
    indices=glb.accessor(prim['indices']).ravel().reshape(-1,3)
    names=sorted(k for k in prim['attributes'] if k!='TEXCOORD_1')
    values=np.concatenate([glb.accessor(prim['attributes'][k]) for k in names],axis=1)
    triangles.append(Counter(tuple(tuple(row) for row in tri) for tri in values[indices]))
    uv=glb.accessor(prim['attributes']['TEXCOORD_1'])[indices]*1024
    edge=uv[:,1]-uv[:,0];other=uv[:,2]-uv[:,0]
    area=abs(edge[:,0]*other[:,1]-edge[:,1]*other[:,0])
    longest=np.maximum.reduce([np.linalg.norm(edge,axis=1),np.linalg.norm(other,axis=1),np.linalg.norm(uv[:,2]-uv[:,1],axis=1)])
    altitude=area/longest
    sampling.append({'triangles':len(indices),'minimum_altitude_source_pixel_quantiles':np.quantile(altitude,[0,.25,.5,.75,1]).tolist(),'triangles_under_one_source_pixel':int((altitude<1).sum())})
assert triangles[0]==triangles[1],'Positions, normals, primary UVs or triangle orientation changed'
identical=[]
for path in sorted((ROOT/'export/sites').glob('SITE_*.glb')):
    if path.name=='SITE_daguan-lou.glb':continue
    assert path.read_bytes()==(folder/'export/sites'/path.name).read_bytes(),path.name
    identical.append(path.name)
assert len(identical)==14
source=json.loads((folder/'source-geometry.json').read_text())
assert source['source_authoring_sha256']==hashlib.sha256((ROOT/'blender/authoring.blend').read_bytes()).hexdigest()
report={'status':'scratch_imperial_uv_only_export_verified','source_glb_sha256':hashlib.sha256(a.blob).hexdigest(),
        'candidate_glb_sha256':hashlib.sha256(b.blob).hexdigest(),'unchanged_resolved_nodes':716,
        'unchanged_other_site_export_names':identical,'target_triangles_preserved':sum(triangles[0].values()),
        'source_chart_sampling':sampling[0],'candidate_chart_sampling':sampling[1],
        'scope':'Exact expanded non-UV2 attribute triangle multisets preserve all target geometry, normals, primary UVs and orientation; all 716 other resolved node contracts and 14 other site GLBs unchanged. Native bake, filtering and art acceptance pending. Production unchanged.'}
(folder/'export-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print('IMPERIAL_UV_ONLY_EXPORT_PRESERVATION_PASS',json.dumps(report['candidate_chart_sampling']))
