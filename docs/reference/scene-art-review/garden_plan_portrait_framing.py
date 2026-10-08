"""Compute camera proposals from actual exported vertices; no native renderer."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

REPO=Path('/Users/auchan/projects/garden-of-dreams')
sys.path.insert(0,str(REPO/'scripts'))
from verify_mountain_export import Glb
from build_godot_import_contract import local_matrix
source=Path(json.loads(Path('/tmp/garden-neutral-atlas-full-source.json').read_text())['folder'])/'export/garden-of-dreams.glb'
glb=Glb(source)
nodes=glb.doc['nodes']
parents={child:index for index,node in enumerate(nodes) for child in node.get('children',[])}
def world(index):
    transform=local_matrix(nodes[index])
    return world(parents[index])@transform if index in parents else transform
def vertices(names):
    rows=[]
    for index,node in enumerate(nodes):
        if node.get('name') not in names:continue
        transform=world(index)
        for primitive in glb.doc['meshes'][node['mesh']]['primitives']:
            points=glb.accessor(primitive['attributes']['POSITION'])
            rows.append((transform@np.column_stack([points,np.ones(len(points))]).T).T[:,:3])
    assert len(rows)>=len(names),names
    return np.concatenate(rows)
def project(points,position,target,size):
    z=(position-target);z/=np.linalg.norm(z)
    x=np.cross([0.,1.,0.],z);x/=np.linalg.norm(x)
    y=np.cross(z,x)
    local=(points-position)@np.column_stack([x,y,z])
    depth=-local[:,2]
    if depth.min()<=.06:return None
    focal=size[0]/(2*np.tan(np.radians(55/2)))
    pixels=np.column_stack([size[0]/2+focal*local[:,0]/depth,size[1]/2-focal*local[:,1]/depth])
    return [pixels.min(axis=0).tolist(),pixels.max(axis=0).tolist()]
poses=json.loads((REPO/'docs/reference/neutral-path-native-review/native-captures/framing/report.json').read_text())['views'][0]['poses']
profiles={
    'daoxiang_cun':('daoxiang-cun',['MAT_thatch','MAT_whitewash','MAT_crt_amber'],[-34,1.7,-22]),
    'daguan_lou':('daguan-lou',['MAT_rooftile','MAT_daguan_lacquer','MAT_crt_amber'],[0,2.7,-23]),
    'longcui_an':('longcui-an',['MAT_rooftile','MAT_whitewash','MAT_lattice_wood'],[-25,1.45,12.2]),
}
report={'status':'cpu_camera_proposals_native_render_pending','source_glb_sha256':hashlib.sha256(glb.bytes).hexdigest(),
        'scope':'Actual vertex projections constrain three portrait arrival proposals. No source/runtime changes, occlusion proof, rendered quality or camera acceptance.',
        'rooms':{}}
for room,(slug,materials,old_target) in profiles.items():
    names=['SITE_'+slug+'_'+m for m in materials]
    points=vertices(names)
    old=np.asarray(poses[room]['position'],dtype=float)
    old_target=np.asarray(old_target,dtype=float)
    baseline={str(size):project(points,old,old_target,size) for size in [(390,844),(360,800)]}
    from itertools import product
    envelope=np.asarray(list(product(*zip(points.min(axis=0),points.max(axis=0)))))
    best=None
    centered_target=old_target.copy()
    for axis in [0,2]:centered_target[axis]=(points[:,axis].min()+points[:,axis].max())/2
    for factor in np.linspace(.62,1.6,80):
        # Retain the horizontal view direction; lower the camera with its offset.
        for aim in np.linspace(-.8,3.0,80):
            target=centered_target.copy();target[1]=aim
            position=target+(old-old_target)*factor
            position[1]={'daoxiang_cun':1.9,'daguan_lou':2.0,'longcui_an':1.65}[room]
            bounds={str(size):project(envelope,position,target,size) for size in [(390,844),(360,800)]}
            valid=True;score=0
            for size,key in [((390,844),str((390,844))),((360,800),str((360,800)))]:
                bounds_row=bounds[key]
                if bounds_row is None:valid=False;break
                low,high=np.asarray(bounds_row)
                # Conservative fixed inset above the room's actual panel top.
                panel_top=520 if size[1]==844 else 476
                if low[0]<12 or high[0]>size[0]-12 or low[1]<50 or high[1]>panel_top-12:
                    valid=False;break
                area=np.prod(high-low)
                score+=area-300*abs((low[1]+high[1])/2-(50+panel_top-12)/2)
            if valid and (best is None or score>best[0]):best=(score,position.copy(),target.copy(),bounds)
    if best is None:
        print('NO_CPU_CAMERA_FIT',room,baseline,flush=True)
        report['rooms'][room]={'status':'no_fit','baseline_bounds':baseline}
        continue
    _,position,target,bounds=best
    bounds={str(size):project(points,position,target,size) for size in [(390,844),(360,800)]}
    assert position[1]>=1.4
    report['rooms'][room]={'meshes':names,'vertices':len(points),'baseline_position':old.tolist(),
                          'baseline_target':old_target.tolist(),'baseline_bounds':baseline,
                          'candidate_position':position.tolist(),'candidate_target':target.tolist(),
                          'candidate_fov':55,'keep_aspect':'KEEP_WIDTH','candidate_bounds':bounds}
output=Path('/tmp/garden-portrait-framing-proposals.json')
output.write_text(json.dumps(report,indent=2)+'\n')
print('PORTRAIT_CPU_PROPOSALS_READY',output)
for room,row in report['rooms'].items():print(room,row['candidate_position'],row['candidate_target'],row['candidate_bounds'])
