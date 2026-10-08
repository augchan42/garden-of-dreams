"""Check deterministic renderer comparisons for actual reflected source geometry."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
p=root/'docs/reference'
a=np.array(Image.open(p/'pond-check-baseline.png')).astype(int)
region=json.loads((root/'godot/reflection-capture-region.json').read_text())
assert list(a.shape[1::-1])==region['viewport']
# Test pixel centers against the projected water quad, with a two-pixel edge
# allowance for rasterization. The HUD panel is translucent, so underlying pond
# changes can show through its background; text, buttons and input stay stable.
yy,xx=np.indices(a.shape[:2],dtype=float)
xx+=.5
yy+=.5
polygon=np.array(region['pond_polygon'])
cross=[]
for start,end in zip(polygon,np.roll(polygon,-1,axis=0)):
 edge=end-start
 cross.append((edge[0]*(yy-start[1])-edge[1]*(xx-start[0]))/np.linalg.norm(edge))
cross=np.stack(cross)
pond_mask=(cross.min(axis=0)>=-2)|(cross.max(axis=0)<=2)
controls_top=int(region['controls_top'])
buttons_top=int(region['buttons_top'])
hud_text=(np.max(a[:,:,:3],axis=2)>=100)&(yy>=controls_top)&(yy<buttons_top)
assert (pond_mask[:controls_top] if region['controls_visible'] else pond_mask).any()
report={}
for name in ['disabled','window-excluded','ripples']:
 b=np.array(Image.open(p/f'pond-check-{name}.png')).astype(int)
 d=np.max(abs(a[:,:,:3]-b[:,:,:3]),axis=2)
 y,x=np.where(d>3)
 report[name]={'changed_pixels_above_3':int(len(x)),'bounds':[int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None,'mean_difference':float(d.mean())}
 assert len(x)>100,report[name]
 # Fixed-camera capture changes must leave the hall itself and the controls untouched.
 assert np.max(d[~pond_mask])<=3,name
 if region['controls_visible']:
  assert np.max(d[buttons_top:,:])<=3,name
  assert np.max(d[hud_text])<=3,name
 else:
  left,top,width,height=map(int,region['return_button_rect'])
  assert np.max(d[top:top+height,left:left+width])<=3,name
(root/'godot/reflection-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
