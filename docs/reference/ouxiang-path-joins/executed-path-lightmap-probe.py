import hashlib,json,pathlib,struct,sys,zlib
import numpy as np
from PIL import Image
sys.path.insert(0,'/Users/auchan/projects/garden-of-dreams/scripts')
from verify_mountain_export import Glb
R=pathlib.Path('/Users/auchan/projects/garden-of-dreams')
probe=json.load(open('/tmp/garden-oux-visible-surface-probe.json'))
g=Glb(R/'godot/assets/garden-of-dreams.glb');name='SITE_stage_MAT_plaster_rock'
n=next(x for x in g.doc['nodes'] if x.get('name')==name)
p=g.doc['meshes'][n['mesh']]['primitives'][0]
pos=g.accessor(p['attributes']['POSITION']);idx=g.accessor(p['indices']).ravel().reshape(-1,3);tri=pos[idx].astype(float)
normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.linalg.norm(normal,axis=1)[:,None]
def decode_rgb16(path):
 b=path.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n'
 w,h,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',b[16:29]);assert (depth,color,compression,filtering,interlace)==(16,2,0,0,0)
 offset=8;packed=bytearray();crcs=0
 while offset<len(b):
  size=struct.unpack_from('>I',b,offset)[0];tag=b[offset+4:offset+8];chunk=b[offset+8:offset+8+size]
  assert zlib.crc32(tag+chunk)&0xffffffff==struct.unpack_from('>I',b,offset+8+size)[0]
  crcs+=1
  if tag==b'IDAT':packed.extend(chunk)
  offset+=12+size
 raw=zlib.decompress(packed);stride=w*6;assert len(raw)==h*(stride+1)
 image=np.empty((h,stride),dtype=np.uint8);counts={}
 for y in range(h):
  tag=raw[y*(stride+1)];counts[tag]=counts.get(tag,0)+1
  row=np.frombuffer(raw,dtype=np.uint8,count=stride,offset=y*(stride+1)+1).copy()
  previous=image[y-1] if y else np.zeros(stride,dtype=np.uint8)
  if tag==1:
   for c in range(6):row[c::6]=np.cumsum(row[c::6],dtype=np.uint32)%256
  elif tag==2:row=((row.astype(np.uint16)+previous)%256).astype(np.uint8)
  elif tag in (3,4):
   for x in range(stride):
    a=int(row[x-6]) if x>=6 else 0;b0=int(previous[x]);c=int(previous[x-6]) if x>=6 else 0
    if tag==3:prediction=(a+b0)//2
    else:
     predict=a+b0-c;pa,pb,pc=abs(predict-a),abs(predict-b0),abs(predict-c)
     prediction=a if pa<=pb and pa<=pc else b0 if pb<=pc else c
    row[x]=(int(row[x])+prediction)%256
  else:assert tag==0
  image[y]=row
 values=image.reshape(h,w,6).copy().view('>u2').reshape(h,w,3)
 # Pillow exposes high bytes for RGB16. Compare every channel to verify the
 # independently reconstructed raster without treating those bytes as precision.
 assert np.array_equal(values//256,np.asarray(Image.open(path)))
 return values,{'chunks_crc_verified':crcs,'filter_counts':counts,'pillow_high_bytes_all_channels_equal':True,'dimensions':[w,h],'bit_depth':16}
path=R/'export/lightmaps'/ (name+'.png');rgb,decode=decode_rgb16(path)
record=json.load(open(path.with_suffix('.json')));assert record['source_glb_sha256']==probe['source_glb_sha256']
assert path.read_bytes()==(R/'godot/lightmaps'/(name+'.png')).read_bytes()
for pixel in probe['pixels']:
 for hit in pixel['nearest_geometric_intersections']:
  if hit['node']!=name:continue
  i=hit['primitive_triangle'];uv=np.array(hit['uv2']);xy=uv*np.array([rgb.shape[1],rgb.shape[0]])-.5
  x,y=np.floor(xy).astype(int);fx,fy=xy-[x,y];x0,x1=np.clip([x,x+1],0,rgb.shape[1]-1);y0,y1=np.clip([y,y+1],0,rgb.shape[0]-1)
  sample=(rgb[y0,x0]*(1-fx)*(1-fy)+rgb[y0,x1]*fx*(1-fy)+rgb[y1,x0]*(1-fx)*fy+rgb[y1,x1]*fx*fy)/65535
  hit.update(geometric_normal_y_up=normal[i].tolist(),triangle_positions_y_up=tri[i].tolist(),
   sampled_source_rgb16_bilinear=sample.tolist(),sampling_scope='Uncompressed 1024px source PNG, not the compressed 256px native texture or complete shader response.')
 # Same height/distance with distinct triangle ownership is geometric overlap,
 # not a visual proof of which face wins native depth testing.
 if len(pixel['nearest_geometric_intersections'])>=2:
  a,b=pixel['nearest_geometric_intersections'][:2]
  pixel['two_nearest_coplanar_same_batch']=a['node']==b['node']==name and abs(a['distance']-b['distance'])<1e-7
probe['source_path_map']={'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_record':record,'decode':decode}
probe['camera_pose_verified_against_saved_native_report']=json.load(open(R/'docs/reference/ouxiang-portrait512/captures/report.json'))['views']['portrait-water']['camera_transform']
probe['status']='overlapping_paving_geometry_and_source_lightmap_samples_measured'
probe['scope']+=' Camera position, FOV/viewport and target match the saved native capture configuration. Source RGB16 PNG is decoded without an 8-bit conversion and checked against every Pillow high byte. Pixel geometry attribution still requires a native surface-ID/control render.'
pathlib.Path('/tmp/garden-oux-visible-surface-probe-with-lightmap.json').write_text(json.dumps(probe,indent=2)+'\n')
for x in probe['pixels']:
 print(x['pixel'],'overlap',x.get('two_nearest_coplanar_same_batch'),[(h['primitive_triangle'],h.get('sampled_source_rgb16_bilinear')) for h in x['nearest_geometric_intersections'][:2]])
