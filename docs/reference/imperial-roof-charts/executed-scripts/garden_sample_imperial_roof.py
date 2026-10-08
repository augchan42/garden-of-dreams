"""Join actual exported triangles to saved roof objects and sample RGB16 maps."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
import numpy as np
ROOT=Path('/Users/auchan/projects/garden-of-dreams')
sys.path.insert(0,str(ROOT/'scripts'))
from verify_mountain_export import Glb
parser=argparse.ArgumentParser()
parser.add_argument('--source',type=Path,default=ROOT/'export/garden-of-dreams.glb')
parser.add_argument('--maps',type=Path,default=ROOT/'export/lightmaps')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
folder=Path(json.loads(Path('/tmp/garden-imperial-roof-probe.json').read_text())['folder'])
source=json.loads((folder/'source-geometry.json').read_text())
assert source['source_authoring_sha256']==hashlib.sha256((ROOT/'blender/authoring.blend').read_bytes()).hexdigest()
grid={}
for row in source['objects']:
    for i,(x,y,z) in enumerate(row['world_positions_z_up']):
        p=np.asarray([x,z,-y])
        key=tuple(np.floor(p/.001).astype(int))
        grid.setdefault(key,[]).append((row['name'],i,p))
glb=Glb(args.source)
name='SITE_daguan-lou_MAT_rooftile'
node=next(n for n in glb.doc['nodes'] if n.get('name')==name)
assert not any(k in node for k in ['translation','rotation','scale','matrix'])
primitives=glb.doc['meshes'][node['mesh']]['primitives']
assert len(primitives)==1
primitive=primitives[0]
positions=glb.accessor(primitive['attributes']['POSITION'])
owners=[]
for p in positions:
    key=np.floor(p/.001).astype(int)
    found={}
    for delta in itertools.product([-1,0,1],repeat=3):
        for obj,i,q in grid.get(tuple(key+delta),[]):
            if np.linalg.norm(p-q)<3e-5:found.setdefault(obj,set()).add(i)
    assert found,'Export vertex does not match saved source'
    owners.append(found)
indices=glb.accessor(primitive['indices']).ravel().reshape(-1,3)
uv=glb.accessor(primitive['attributes']['TEXCOORD_1'])[indices]
tri=positions[indices]
cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
normals=cross/np.linalg.norm(cross,axis=1)[:,None]
groups=[];objects=set()
for a,b,c in indices:
    common=set(owners[a])&set(owners[b])&set(owners[c])
    assert len(common)==1,'Source triangle ownership ambiguous'
    obj=next(iter(common));objects.add(obj)
    rings=set(i//8 for v in [a,b,c] for i in owners[v][obj])
    groups.append('shell' if not obj.startswith('DAGUAN_tile_strip') else 'cylinder_caps' if len(rings)==1 else 'cylinder_sides')
assert len(objects)==578
record=json.loads((args.maps/(name+'.json')).read_text())
digest=hashlib.sha256(glb.bytes).hexdigest()
assert record['source_glb_sha256']==digest and record['uv_channel']==1
path=args.maps/record['texture']
width,height,depth,color,_,_,interlace=struct.unpack('>IIBBBBB',path.read_bytes()[16:29])
assert depth==16 and color==2 and interlace==0 and width==height==record['size']
raw=subprocess.run(['ffmpeg','-v','error','-threads','1','-i',str(path),'-f','rawvideo','-pix_fmt','rgb48le','-'],check=True,capture_output=True).stdout
image=np.frombuffer(raw,dtype='<u2').reshape(height,width,3).astype(float)/65535
centers=uv.mean(axis=1)
# Native PNG rows correspond to glTF V, as in the existing roof diagnostic.
xy=np.clip((centers*width).astype(int),0,width-1)
light=image[xy[:,1],xy[:,0]]*record['scale']
edges=np.stack([uv[:,1]-uv[:,0],uv[:,2]-uv[:,1],uv[:,0]-uv[:,2]],axis=1)*width
longest=np.linalg.norm(edges,axis=2).max(axis=1)
twice_area=abs(edges[:,0,0]*(-edges[:,2,1])-edges[:,0,1]*(-edges[:,2,0]))
altitude=twice_area/longest
groups=np.asarray(groups)
report={'status':'source_owned_imperial_roof_sampled','source_authoring_sha256':source['source_authoring_sha256'],
        'source_glb_sha256':digest,'source_map_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'source_map_size':width,'matched_saved_objects':len(objects),'groups':{},
        'scope':'Exact saved-object ownership of all exported roof triangles; UV2 source-pixel altitudes and RGB16 triangle-centroid irradiance. Does not prove camera visibility, filtered native appearance or final art acceptance.'}
for label in ['shell','cylinder_sides','cylinder_caps']:
    for suffix,normal_mask in [('all',np.ones(len(indices),dtype=bool)),('upward',normals[:,1]>.25)]:
        mask=(groups==label)&normal_mask
        report['groups'][label+'_'+suffix]={'triangles':int(mask.sum()),
            'altitude_source_pixels_quantiles':np.quantile(altitude[mask],[0,.25,.5,.75,1]).tolist(),
            'triangles_under_one_source_pixel_altitude':int((altitude[mask]<1).sum()),
            'zero_irradiance_centroids':int((light[mask].max(axis=1)==0).sum()),
            'irradiance_luminance_quantiles':np.quantile(light[mask]@np.asarray([.2126,.7152,.0722]),[0,.25,.5,.75,1]).tolist()}
assert report['groups']['shell_all']['triangles']==52
assert report['groups']['cylinder_sides_all']['triangles']==9216
assert report['groups']['cylinder_caps_all']['triangles']==6912
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('IMPERIAL_SOURCE_OWNED_SAMPLING_PASS',json.dumps(report['groups']))
