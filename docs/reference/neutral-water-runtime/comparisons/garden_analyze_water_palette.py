from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion
p=Path(json.loads(Path('/tmp/garden-ziling-framing.json').read_text())['folder']);d=json.loads((p/'water-palette/report.json').read_text());rows=d['rows'];result={'scope':'Encoded RGB pixel statistics inside visible-water magenta controls, excluding UI and eroding edges; not linear radiometry or final art/phone acceptance.','source_glb_sha256':d['source_glb_sha256'],'views':{},'input_reports_sha256':hashlib.sha256((p/'water-palette/report.json').read_bytes()).hexdigest()}
for room in ['qinfang_ting','ouxiang_xie','ziling_zhou','aojing_guan']:
 for aspect in ['desktop','portrait']:
  group=[r for r in rows if r['room']==room and r['aspect']==aspect];control=next(r for r in group if r['variant']=='visible-water-control');a=np.array(Image.open(control['capture']).convert('RGB'),dtype=np.int16)
  mask=(a[:,:,0]>a[:,:,1]+40)&(a[:,:,2]>a[:,:,1]+25)&(a[:,:,0]>90);mask[int(control['panel_top']):]=False;mask[:45]=False;mask=binary_erosion(mask,iterations=2)
  stats={'visible_water_pixels':int(mask.sum()),'screen_fraction':float(mask.mean()),'variants':{}}
  for row in group:
   if row['variant']=='visible-water-control':continue
   image=np.array(Image.open(row['capture']).convert('RGB'),dtype=float);v=image[mask];mean=v.mean(axis=0) if len(v) else np.zeros(3);l=v@np.array([.2126,.7152,.0722]) if len(v) else np.zeros(1)
   baseline=np.array(Image.open(next(x['capture'] for x in group if x['variant']=='baseline')).convert('RGB'),dtype=float)
   ui=np.max(np.abs(image[int(row['panel_top']):]-baseline[int(row['panel_top']):]))
   stats['variants'][row['variant']]={'mean_rgb_encoded':mean.tolist(),'green_excess_encoded':float(mean[1]-(mean[0]+mean[2])/2),'mean_luma_encoded':float(l.mean()),'p95_luma_encoded':float(np.percentile(l,95)),'max_ui_pixel_delta':float(ui)}
  result['views'][room+'-'+aspect]=stats
  print(room,aspect,'water pixels',stats['visible_water_pixels'],'baseline',stats['variants']['baseline'],'slate',stats['variants']['slate-combined'])
(p/'water-palette/pixel-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print('WATER_PALETTE_PIXEL_ANALYSIS_SAVED')
