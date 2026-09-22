"""Check deterministic renderer comparisons for actual reflected source geometry."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
p=root/'docs/reference'
a=np.array(Image.open(p/'pond-check-baseline.png')).astype(int)
report={}
for name in ['disabled','window-excluded','ripples']:
 b=np.array(Image.open(p/f'pond-check-{name}.png')).astype(int)
 d=np.max(abs(a[:,:,:3]-b[:,:,:3]),axis=2)
 y,x=np.where(d>3)
 report[name]={'changed_pixels_above_3':int(len(x)),'bounds':[int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None,'mean_difference':float(d.mean())}
 assert len(x)>100,report[name]
 # Fixed-camera capture changes must leave the hall itself and the controls untouched.
 assert np.max(d[:230,:])<=3 and np.max(d[430:,:])<=3,name
(root/'godot/reflection-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
