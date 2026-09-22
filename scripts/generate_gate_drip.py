"""Original procedural mineral/water streaks; no external image sources."""
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(2319)
n=512;y,x=np.mgrid[0:1:complex(n),0:1:complex(n)];mask=np.zeros((n,n))
for i in range(19):
 cx=rng.uniform(.12,.88);end=rng.uniform(.35,.93);width=rng.uniform(.004,.025)
 center=cx+.008*np.sin(y*18+i)+.004*np.sin(y*43+i)
 fade=np.clip((end-y)*30,0,1)*np.clip((y-.04)*15,0,1)
 streak=np.exp(-((x-center)/width)**2)*fade
 mask=np.maximum(mask,streak*rng.uniform(.3,.85))
mask*=np.clip((1-y)*12,0,1)*np.clip(y*12,0,1)
noise=rng.uniform(.75,1,(n,n));alpha=(mask*noise*210).astype('uint8')
rgba=np.zeros((n,n,4),dtype='uint8');rgba[:,:,:3]=[48,48,29];rgba[:,:,3]=alpha
p=R/'textures/decals/gate-water-drips.png';Image.fromarray(rgba).save(p)
print(p)
