from pathlib import Path
import json,hashlib
from PIL import Image
root=Path('/tmp/garden-qiushuang-lattice-20261010');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((root/'native-unbaked-baseline/report.json').read_text());b=json.loads((root/'native-unbaked-candidate/report.json').read_text())
assert a['status']==b['status']=='passed'
assert a['route_sha256']==b['route_sha256']==sha(root/'godot/runtime/entry_route.gd')
assert a['source_glb_sha256']==sha(root/'baseline-godot/assets/garden-of-dreams.glb')
assert b['source_glb_sha256']==sha(root/'export/garden-of-dreams.glb')==sha(root/'godot/assets/garden-of-dreams.glb')
assert len(a['captures'])==len(b['captures'])==8
rows=[]
for x,y in zip(a['captures'],b['captures']):
 for key in ['shape','action','size','camera_transform','camera_fov','camera_aspect','tech_batch_triangles','site_bakes_enabled']:assert x[key]==y[key],(key,x['shape'],x['action'])
 assert x['site_bakes_enabled'] is False
 for capture in [x,y]:
  p=Path(capture['path']);assert sha(p)==capture['sha256']
  with Image.open(p) as im:im.load();assert list(im.size)==capture['size']
 rows.append({'shape':y['shape'],'action':y['action'],'baseline_sha256':x['sha256'],'candidate_sha256':y['sha256'],'camera_parameters_exact':True,'tech_triangles':y['tech_batch_triangles']})
for name in ['native-unbaked-baseline','native-unbaked-candidate']:
 log=(root/(name+'.log')).read_text()
 assert 'QIUSHUANG_LATTICE_NATIVE_PASS' in log and not any(s in log for s in ['SCRIPT ERROR:','ERROR:','Assertion failed'])
report={'status':'native_unbaked_lattice_comparison_passed','captures_decoded':16,'view_pairs':rows,'scope':'Eight exact camera/view/UI pairs in normal route, all site bakes disabled equally. Candidate originals directly viewed; phosphor lettering clears lattice. Current-source lighting, all-site regression and production adoption still pending.'}
(root/'native-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print('QIUSHUANG_NATIVE_COMPARISON_PASS',len(rows),'pairs, 16 PNG decoded')
