from pathlib import Path
import hashlib,json,numpy as np
from PIL import Image
r=Path(__file__).resolve().parent;rows=[]
for mode in ['baseline','candidate']:
 report=json.loads((r/f'native-sv-{mode}.json').read_text());assert report['status']=='passed' and len(report['phases'])==2
 for phase in report['phases']:
  log=r/f'native-sv-{mode}-{phase["name"]}.log';assert phase['exit_code']==0 and hashlib.sha256(log.read_bytes()).hexdigest()==phase['log_sha256']
assert len(list((r/'native-sv-baseline').glob('*.png')))==8
assert len(list((r/'native-sv-candidate').glob('*.png')))==8
for a in sorted((r/'native-sv-baseline').glob('*.png')):
 b=r/'native-sv-candidate'/a.name
 with Image.open(a) as i,Image.open(b) as j:i.load();j.load();x=np.asarray(i);y=np.asarray(j);assert x.shape==y.shape
 changed=int(np.any(x!=y,axis=2).sum());exact=a.read_bytes()==b.read_bytes();assert changed==0 and exact,(a.name,changed,exact)
 rows.append({'file':a.name,'changed_pixels':changed,'byte_exact':exact,'size':list(x.shape[1::-1]),'baseline_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(b.read_bytes()).hexdigest()})
report={'status':'passed','clock':'stage fog timeline_time0','native_viewport':'SubViewport UPDATE_ALWAYS and force_draw; same geometry/cameras/materials as the gallery fixture','files':rows,'scope':'All eight native gallery originals remain pixel and byte exact. Direct raw default native imports separately verify2048paint bindings. Root-window signal waits retained and unaccepted; no actual phone/performance acceptance.'};(r/'native-fixed-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print('STAGE_NATIVE_FIXED_IMAGES_PASS',len(rows))
