from pathlib import Path
import json,struct,hashlib
import numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation

repo=Path('/Users/auchan/projects/garden-of-dreams')
work=Path(json.loads(Path('/tmp/garden-qiushuang-framing.json').read_text())['folder'])
source=repo/'godot/assets/garden-of-dreams.glb';raw=source.read_bytes();length=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+length]);binary=raw[28+length:]
parents={child:index for index,node in enumerate(gltf['nodes']) for child in node.get('children',[])}
cache={}
def matrix(index):
    if index in cache:return cache[index]
    node=gltf['nodes'][index]
    if 'matrix' in node:local=np.array(node['matrix']).reshape((4,4),order='F')
    else:
        local=np.eye(4);local[:3,:3]=Rotation.from_quat(node.get('rotation',[0,0,0,1])).as_matrix()@np.diag(node.get('scale',[1,1,1]));local[:3,3]=node.get('translation',[0,0,0])
    result=matrix(parents[index])@local if index in parents else local;cache[index]=result;return result
points=[];records=[]
names=['SITE_qiushuang-zhai_MAT_rooftile','SITE_qiushuang-zhai_MAT_whitewash','SITE_qiushuang-zhai_MAT_tech_atlas']
for index,node in enumerate(gltf['nodes']):
    if node.get('name') not in names:continue
    count=0
    for primitive in gltf['meshes'][node['mesh']]['primitives']:
        accessor=gltf['accessors'][primitive['attributes']['POSITION']];view=gltf['bufferViews'][accessor['bufferView']]
        assert accessor['componentType']==5126 and accessor['type']=='VEC3' and view['buffer']==0
        local=np.ndarray((accessor['count'],3),dtype='<f4',buffer=binary,offset=view.get('byteOffset',0)+accessor.get('byteOffset',0),strides=(view.get('byteStride',12),4)).astype(np.float64)
        world=np.column_stack((local,np.ones(len(local))))@matrix(index).T
        points.append(world[:,:3]);count+=len(local)
    records.append({'node':node['name'],'vertices':count,'world_matrix':matrix(index).tolist()})
assert len(records)==3
cloud=np.vstack(points);hull=ConvexHull(cloud)
violations=cloud@hull.equations[:,:3].T+hull.equations[:,3]
maximum=float(violations.max());assert maximum<1e-4
report={'status':'exact_exported_vertex_hull_checked','source_glb_sha256':hashlib.sha256(raw).hexdigest(),'original_vertex_count':len(cloud),'hull_vertex_count':len(hull.vertices),'maximum_halfspace_violation_metres':maximum,'nodes':records,'hall_hull':cloud[hull.vertices].tolist(),'scope':'Convex hull of all current exported roof/wall/tech vertices after their actual glTF hierarchy transforms. All original vertices verified inside its halfspaces. Native projected extrema must still be compared with the imported vertices; not visual or device acceptance.'}
(work/'godot/tests/qiushuang-hull.json').write_text(json.dumps(report,indent=2)+'\n');(work/'hull-report.json').write_text(json.dumps(report,indent=2)+'\n');print('QIUSHUANG_HULL',len(cloud),len(hull.vertices),maximum)
