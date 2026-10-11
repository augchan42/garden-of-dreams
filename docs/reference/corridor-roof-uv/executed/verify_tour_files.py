"""Verify actual full-tour traces and decode every captured original."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path('/tmp/garden-corridor-roof-full-20261011'));p.add_argument('--report',type=Path);a=p.parse_args();r=a.root
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
job=r/'tour-jobs.json'
if not job.exists() or json.loads(job.read_text()).get('status')!='both_native_full_tours_passed':raise RuntimeError('Tours incomplete; no tour pixels accepted')
j=json.loads(job.read_text());assert len(j['phases'])==2 and all(x['status']=='passed' and x['exit_code']==0 for x in j['phases'])
source=sha(r/'export/garden-of-dreams.glb');assert source==sha(r/'godot/assets/garden-of-dreams.glb')
runtime=sha(r/'godot/runtime/entry_route.gd');files={};shapes={};rooms=None
for shape in ['desktop','portrait']:
 folder=r/('lit-tour-'+shape);d=json.loads((folder/'report.json').read_text())
 assert d['status']=='passed' and not d['error'] and not d['floor_failures'] and len(d['legs'])==26 and len(d['settled_arrivals'])==26 and d['maximum_practicals']<=4
 assert d['source_glb_sha256']==source and d['route_sha256']==runtime and d['time_scale']==1 and d['physics_ticks_per_second']==60
 current=set(d['visited_rooms']);assert len(current)==14
 if rooms is not None:assert rooms==current
 rooms=current
 for leg in d['legs']:
  assert not leg['centre_ray_misses'] and leg['physics_frames']>0 and leg['supported_ray_samples']>0 and leg['grounded_ray_samples']>0
 assert len({x['file'] for x in d['captures']})==len(d['captures'])
 for x in d['captures']:
  path=folder/'captures'/x['file'];assert path.resolve().is_relative_to(folder.resolve());assert sha(path)==x['sha256'];assert x['active_practicals']<=4
  with Image.open(path) as im:im.load();assert im.format=='PNG' and list(im.size)==d['viewport']
  files[str(path.resolve().relative_to(r.resolve()))]={'sha256':x['sha256'],'size':d['viewport'],'room':x['room'],'phase':x['phase']}
 assert {x['room'] for x in d['captures']}==rooms
 shapes[shape]={'legs':26,'settled_arrivals':26,'captures':len(d['captures']),'maximum_practicals':d['maximum_practicals'],'supported_ray_samples':sum(x['supported_ray_samples'] for x in d['legs'])}
out=a.report or r/'tour-file-verification.json';assert not out.exists(),'Do not overwrite tour proof'
out.write_text(json.dumps({'status':'passed','source_glb_sha256':source,'runtime_sha256':runtime,'decoded_and_verified_png':len(files),'rooms':sorted(rooms),'tours':shapes,'files':files,'scope':'Actual desktop and portrait public-command tours, each fourteen rooms/twenty-six legs, normal physics and all recorded original pixels. Direct art review and current target-phone sustained acceptance remain separate.'},indent=2)+'\n')
print('CORRIDOR_ROOF_TOUR_FILES_PASS',len(files))
