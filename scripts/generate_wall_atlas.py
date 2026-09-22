"""Reuse architectural wood/tile swatches and add original limewash plaster."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1]
source=R/'textures/atlases/pavilion'
out=R/'textures/atlases/wall';out.mkdir(parents=True,exist_ok=True)
config=json.loads((source/'atlas.json').read_text())
arrays={key:np.array(Image.open(source/f'pavilion_{key}.png').convert('RGB')) for key in ['basecolor','normal','orm']}
rng=np.random.default_rng(8173);tile=1024
y,x=np.mgrid[0:tile,0:tile]/tile
coarse=np.asarray(Image.fromarray(rng.integers(0,256,(24,24),dtype=np.uint8)).resize((tile,tile),Image.Resampling.BICUBIC),dtype=float)/255-.5
fine=rng.normal(0,1,(tile,tile))
# Broad brush/trowel variation and fine plaster grain, without painted shadows.
detail=coarse*.16+np.sin(y*90+np.sin(x*13)*2)*.012+fine*.012
linear=np.clip(np.array([.3,.39,.23])[None,None,:]*(1+detail[:,:,None]),0,1)
srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
arrays['basecolor'][1024:,:1024]=np.rint(srgb*255).astype(np.uint8)
dy,dx=np.gradient(detail)
norm=np.stack((-dx,dy,np.ones_like(dx)),axis=-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
arrays['normal'][1024:,:1024]=np.rint((norm*.5+.5)*255).astype(np.uint8)
arrays['orm'][1024:,:1024,0]=255
arrays['orm'][1024:,:1024,1]=np.clip((.88+detail*.15)*255,0,255).astype(np.uint8)
arrays['orm'][1024:,:1024,2]=0
for key,array in arrays.items():Image.fromarray(array).save(out/f'wall_{key}.png')
regions=config['uv_regions']
regions['MAT_whitewash']=regions.pop('MAT_plaster_rock')
regions.pop('MAT_bronze')
manifest={'size':[2048,2048],'provenance':'Original deterministic limewash texture, seed 8173. Wood and tile swatches copied from the original pavilion atlas, seed 7341. No external imagery.','uv_regions':regions,'padding_pixels':32,'orm_channels':config['orm_channels'],'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')}}
(out/'atlas.json').write_text(json.dumps(manifest,indent=2))
print('WALL_ATLAS_TEXTURES',json.dumps(manifest))
