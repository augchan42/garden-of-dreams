"""Compare Godot's rendered LUT result with CPU trilinear interpolation."""
from pathlib import Path
import numpy as np,json
from PIL import Image
root=Path(__file__).resolve().parents[1]
source=np.asarray(Image.open(root/'docs/reference/grade-input.png').convert('RGB'),dtype=float)/255
actual=np.asarray(Image.open(root/'docs/reference/grade-output.png').convert('RGB'),dtype=float)/255
rows=[list(map(float,s.split())) for s in (root/'grade/tech-noir.cube').read_text().splitlines() if s and s[0].isdigit()]
lut=np.array(rows).reshape(32,32,32,3)
p=source*31;lo=np.floor(p).astype(int);hi=np.minimum(lo+1,31);f=p-lo;expected=np.zeros_like(source)
for r in range(2):
 for g in range(2):
  for b in range(2):
   idx=[hi[:,:,k] if v else lo[:,:,k] for k,v in enumerate([r,g,b])]
   w=np.prod([f[:,:,k] if v else 1-f[:,:,k] for k,v in enumerate([r,g,b])],axis=0)
   expected+=lut[idx[2],idx[1],idx[0]]*w[:,:,None]
mask=np.ones(source.shape[:2],dtype=bool);mask[:16,:16]=False
error=np.abs(actual-expected)[mask]*255
ui_error=np.abs(actual[:16,:16]-source[:16,:16]).max()*255
report={'samples':int(mask.sum()),'max_channel_error_255':float(error.max()),'mean_channel_error_255':float(error.mean()),'ui_marker_error_255':float(ui_error)}
print(report)
assert error.max()<=3,report
assert ui_error==0,report
(root/'godot/grade-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('ENGINE_GRADE_PASS')
