"""Read saved PNGs at native precision through Blender, without an 8-bit conversion."""
import bpy,json,hashlib
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]
report={}
for path in sorted((root/'export/lightmaps').glob('*.png')):
 image=bpy.data.images.load(str(path),check_existing=False)
 image.colorspace_settings.name='Non-Color'
 pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(-1,4)
 report[path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'max_value':float(pixels[:,:3].max()),'nonzero_fraction':float((pixels[:,:3].max(axis=1)>0).mean()),'finite':bool(np.isfinite(pixels).all())}
 bpy.data.images.remove(image)
(root/'export/lightmap-pixels.json').write_text(json.dumps(report,indent=2)+'\n')
print('LIGHTMAP_PIXEL_REPORT',len(report),report.get('SITE_stage_MAT_painted_mountains_0.png'))
