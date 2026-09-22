"""Generate a seamless wave normal map from periodic height derivatives."""
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
y,x=np.mgrid[0:256,0:256]/256
u=np.zeros_like(x);v=np.zeros_like(y)
for fx,fy,amp,phase in [(3,1,.35,0),(1,4,.22,.7),(7,-2,.12,1.3),(2,9,.06,2.1)]:
 wave=np.cos(2*np.pi*(fx*x+fy*y)+phase)*amp
 u+=wave*fx/4;v+=wave*fy/4
n=np.stack([-u,-v,np.ones_like(x)*2.5],axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
p=root/'godot/materials/water-normal.png';Image.fromarray(np.uint8((n*.5+.5)*255)).save(p)
print(p)
