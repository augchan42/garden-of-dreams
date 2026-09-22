"""Compare isolated, fixed-clock renders from Godot's render_surfaces.gd."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
refs=root/'docs/reference'
baseline=np.asarray(Image.open(refs/'surfaces-baseline.png')).astype(float)
report={}
for name in ['water','fog']:
 frame=np.asarray(Image.open(refs/f'surfaces-{name}.png')).astype(float)
 delta=np.abs(baseline-frame)
 report[name]={'mean_channel_delta':float(delta.mean()),'changed_pixel_fraction':float((delta.max(axis=2)>2).mean())}
 assert report[name]['changed_pixel_fraction']>.001,(name,report[name])
(root/'godot/surface-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('SURFACE_ANIMATION_PASS',report)
