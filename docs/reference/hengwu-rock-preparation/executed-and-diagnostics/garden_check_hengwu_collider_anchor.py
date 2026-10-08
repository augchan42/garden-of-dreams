import sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/Users/auchan/projects/garden-of-dreams/scripts');from verify_mountain_export import Glb
work=Path(json.loads(Path(sys.argv[1]).read_text())['root']);g=Glb(work/'export/garden-of-dreams.glb');node=next(n for n in g.doc['nodes'] if n.get('name')=='COL_hengwu_rock-colonly');prim=g.doc['meshes'][node['mesh']]['primitives'][0];v=g.accessor(prim['attributes']['POSITION']);v=v*np.array(node.get('scale',[1,1,1]))+np.array(node.get('translation',[0,0,0]));low=v.min(axis=0);high=v.max(axis=0);center=(low+high)*.5;dimensions=high-low
print('COLLIDER_WORLD_BOUNDS',low.tolist(),high.tolist());assert np.allclose(center,[-15.4,1.05,-12.5],atol=1e-5),('Moved collider anchor',center.tolist());assert np.allclose(dimensions,[1.995*.8,2.8*.75,1.15],atol=1e-5),('Wrong collider dimensions',dimensions.tolist());print('HENGWU_COLLIDER_ANCHOR_PASS')
