"""Generate deterministic original PBR texture swatches, with no external source imagery."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
out=R/'textures/atlases/pavilion';out.mkdir(parents=True,exist_ok=True)
size=2048;tile=1024;rng=np.random.default_rng(7341)
color=np.zeros((size,size,3),dtype=np.uint8);orm=np.zeros_like(color);normal=np.zeros_like(color)
entries=[('MAT_lattice_wood',(0,0),(.045,.07,.025),.72,0),('MAT_rooftile',(1,0),(.025,.06,.035),.58,0),('MAT_plaster_rock',(0,1),(.15,.24,.12),.48,0),('MAT_bronze',(1,1),(.45,.23,.025),.4,.85)]
regions={}
for name,(cx,cy),base,rough,metal in entries:
 y,x=np.mgrid[0:tile,0:tile]/tile
 fine=rng.normal(0,1,(tile,tile))
 coarse=np.asarray(Image.fromarray(rng.integers(0,256,(32,32),dtype=np.uint8)).resize((tile,tile),Image.Resampling.BICUBIC),dtype=float)/255-.5
 if 'wood' in name:
  grain=np.sin(x*480+np.sin(y*11)*2+coarse*2)
  detail=grain*.045+coarse*.13+fine*.008
 elif 'rooftile' in name:
  detail=coarse*.2+fine*.017+np.sin(y*160)*.012
 elif 'rock' in name:
  detail=coarse*.25+fine*.035
 else:
  detail=coarse*.23+np.sin(x*900+y*20)*.022+fine*.012
 linear=np.clip(np.array(base)[None,None,:]*(1+detail[:,:,None]),0,1)
 srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
 # PNG rows are top-down; UV rectangles below describe Blender's bottom-up image convention.
 row=slice(cy*tile,(cy+1)*tile);col=slice(cx*tile,(cx+1)*tile)
 color[row,col]=np.rint(srgb*255).astype(np.uint8)
 orm[row,col,0]=255;orm[row,col,1]=np.clip((rough+detail*.2)*255,0,255).astype(np.uint8);orm[row,col,2]=int(metal*255)
 dy,dx=np.gradient(detail)
 n=np.stack((-dx*1.2,dy*1.2,np.ones_like(dx)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
 normal[row,col]=np.rint((n*.5+.5)*255).astype(np.uint8)
 pad=32/size
 regions[name]=[cx*.5+pad,(1-cy)*.5+pad,.5-2*pad,.5-2*pad]
for name,array in [('basecolor',color),('orm',orm),('normal',normal)]:Image.fromarray(array).save(out/f'pavilion_{name}.png')
manifest={'size':[size,size],'provenance':'Original deterministic procedural raster textures; no downloaded or generated source images. Seed 7341.','uv_regions':regions,'padding_pixels':32,'orm_channels':{'R':'constant unoccluded','G':'roughness','B':'metallic'},'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')}}
(out/'atlas.json').write_text(json.dumps(manifest,indent=2))
print('PAVILION_ATLAS_TEXTURES',json.dumps(manifest))
