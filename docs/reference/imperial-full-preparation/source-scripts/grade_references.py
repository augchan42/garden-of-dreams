"""Apply the shipped 32-cube LUT with trilinear interpolation to display-referred PNGs."""
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
rows=[list(map(float,line.split())) for line in (R/'grade/tech-noir.cube').read_text().splitlines() if line and line[0].isdigit()]
lut=np.array(rows).reshape(32,32,32,3)
for path in (R/'docs/reference').glob('*-raw.png'):
 rgb=np.asarray(Image.open(path).convert('RGB'),dtype=float)/255*31
 lo=np.floor(rgb).astype(int);hi=np.minimum(lo+1,31);f=rgb-lo;out=np.zeros_like(rgb)
 for r in range(2):
  for g in range(2):
   for b in range(2):
    idx=[hi[:,:,k] if v else lo[:,:,k] for k,v in enumerate([r,g,b])]
    wt=np.prod([f[:,:,k] if v else 1-f[:,:,k] for k,v in enumerate([r,g,b])],axis=0)
    out+=lut[idx[2],idx[1],idx[0]]*wt[:,:,None]
 Image.fromarray(np.uint8(np.clip(out,0,1)*255)).save(path.with_name(path.name.replace('-raw','')))
print('Graded references with tech-noir.cube')
