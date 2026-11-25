"""Decode exact native outputs and check their source, runtime, and public-camera identity."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path('/tmp/garden-aojing-ground-v2-20261011'));p.add_argument('--hall-directory',default='native-lit-corridor');p.add_argument('--report',type=Path);a=p.parse_args();root=a.root
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
validation=root/'lit-validation.json'
if not validation.exists() or json.loads(validation.read_text()).get('status')!='isolated_lit_views_and_resource_checks_passed_tours_and_direct_review_pending':raise RuntimeError('Native validation incomplete; no images accepted')
v=json.loads(validation.read_text());assert len(v['phases'])==17 and all(x['status']=='passed' and x['exit_code']==0 for x in v['phases'])
source=sha(root/'export/garden-of-dreams.glb');assert source==sha(root/'godot/assets/garden-of-dreams.glb')==v['source_glb_sha256']
runtime=sha(root/'godot/runtime/entry_route.gd');files={}
def decode(path,digest,size):
 path=Path(path);assert path.resolve().is_relative_to(root.resolve());assert sha(path)==digest
 with Image.open(path) as im:im.load();assert im.format=='PNG' and list(im.size)==size
 key=str(path.resolve().relative_to(root.resolve()));assert key not in files;files[key]={'sha256':digest,'size':size}
hall=json.loads((root/a.hall_directory/'report.json').read_text());assert hall['status']=='passed' and hall['source_glb_sha256']==source and hall['route_sha256']==runtime and hall['fixed_clock']==3
assert len(hall['captures'])==14
assert {(x['shape'],x['action']) for x in hall['captures']}=={(s,c) for s in ['desktop','portrait'] for c in ['arrival','table','water','north','south','east','west']}
for x in hall['captures']:
 assert x['site_bakes_enabled'] and x['room_id']=='qinfang_ting' and x['native_map_size']==[256,256]
 assert x['diagnostic_camera']==(x['action'] in ['north','south','east','west'])
 decode(x['path'],x['sha256'],x['size'])
for label,touch in [('normal',False),('touch',True)]:
 folder=root/('lit-framing-'+label);d=json.loads((folder/'report.json').read_text());assert d['status']=='qiushuang_framing_passed' and d['source_glb_sha256']==source and d['route_sha256']==runtime and not d['errors'] and d['touch']==touch and len(d['rows'])==18
 for x in d['rows']:assert not x['camera_transition_running'];decode(x['capture'],x['sha256'],x['pixels'])
rooms=set()
for label in ['desktop','portrait']:
 folder=root/('lit-arrivals-'+label);d=json.loads((folder/('route-'+label+'-report.json')).read_text());assert d['source_glb_sha256']==source and d['fixed_clock'] and len(d['captures'])==14
 current={x['room_id'] for x in d['captures'].values()};assert len(current)==14
 if rooms:assert current==rooms
 rooms=current
 for key,x in d['captures'].items():decode(folder/('route-'+key+'.png'),x['sha256'],x['image_size'])
ground=json.loads((root/'native-lit-ground/report.json').read_text());assert ground['status']=='passed' and ground['source_glb_sha256']==source and ground['route_sha256']==runtime and ground['fixed_clock']==3 and len(ground['captures'])==8
assert {(x['shape'],x['action']) for x in ground['captures']}=={(s,c) for s in ['desktop','portrait'] for c in ['arrival','doors','reflection','west_strip']}
for x in ground['captures']:
 assert x['site_bakes_enabled'] and x['room_id']=='aojing_guan' and x['diagnostic_camera']==(x['action']=='west_strip');decode(x['path'],x['sha256'],x['size'])
assert len(files)==86
out=a.report or root/'native-lit-file-verification.json';assert not out.exists(),'Do not overwrite native proof; inspect the prior report'
out.write_text(json.dumps({'status':'passed','source_glb_sha256':source,'runtime_sha256':runtime,'decoded_and_verified_png':86,'rooms':sorted(rooms),'files':files,'scope':'Exact decoded PNGs from seventeen successful native phases plus eight Aojing public/ground views, fourteen fixed-clock public/roof views, both public framing modes, and all fourteen arrivals at two sizes. Requires direct visual review and actual full tours; does not establish final art or device performance.'},indent=2)+'\n')
print('AOJING_GROUND_NATIVE_FILES_PASS',len(files))
