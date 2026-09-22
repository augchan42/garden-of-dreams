"""Derive tangent-space recess normals from decal alpha; preserve original RGBA art."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np
R=Path(__file__).resolve().parents[1]
im=Image.open(R/'textures/decals/gate-inscription.png')
a=np.asarray(im.getchannel('A').filter(ImageFilter.GaussianBlur(2.5)),dtype=np.float32)/255
# Height is negative inside the lettering. Image Y points down, tangent V points up.
h=-a;dy,dx=np.gradient(h);normal=np.stack((-dx*12,dy*12,np.ones_like(a)),axis=-1)
normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255))).save(R/'textures/decals/gate-inscription-normal.png')
print('INSCRIPTION_NORMAL_SAVED',im.size)
