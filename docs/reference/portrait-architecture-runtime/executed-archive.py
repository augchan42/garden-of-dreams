import hashlib,json,re,shutil,struct
from pathlib import Path
root=Path('/Users/auchan/projects/garden-of-dreams')
archive=root/'docs/reference/portrait-architecture-runtime'
archive.mkdir(exist_ok=False)
locations={};hash_paths={};files={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(src,logical):
 src=Path(src);h=sha(src)
 if h in hash_paths:
  dest=hash_paths[h]
 else:
  dest=archive/logical;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);hash_paths[h]=dest;files[str(dest.relative_to(root))]=h
 locations[logical]={'original_path':str(src),'archive_path':str(dest.relative_to(root)),'sha256':h}
 return dest
frozen=json.loads(Path('/tmp/garden-portrait-architecture-review/frozen-inputs.json').read_text())
for name,h in frozen.items():
 assert sha(root/name)==h,name
 add(root/name,'executed-final/'+name)
add('/tmp/garden-portrait-architecture-review/frozen-inputs.json','frozen-inputs.json')
for src,name in [('entry_route-before.gd','executed-before/entry_route.gd'),('entry_route-angle0-passed.gd','executed-angle0/entry_route.gd'),('test_portrait_architecture.gd','executed-before/test_portrait_architecture.gd'),('portrait-architecture-contract.json','executed-before/portrait-architecture-contract.json')]:add('/tmp/garden-portrait-architecture-runtime/'+src,name)
for group in ['red','green','selected']:
 folder=Path('/tmp/garden-portrait-architecture-'+group)
 report=json.loads((folder/'report.json').read_text())
 assert len(report['rows'])==15
 assert len(report['errors'])==(13 if group=='red' else 0)
 if group=='selected':
  assert report['route_sha256']==frozen['godot/runtime/entry_route.gd']
  assert report['test_sha256']==frozen['godot/tests/test_portrait_architecture.gd']
 for row in report['rows']:
  p=Path(row['capture']);assert sha(p)==row['sha256'];pixels=list(struct.unpack('>II',p.read_bytes()[16:24]));assert pixels==row['capture_pixels'];add(p,group+'/'+p.name)
 add(folder/'report.json',group+'/report.json');add('/tmp/garden-portrait-architecture-'+group+'.log',group+'/native.log')
angles=Path('/tmp/garden-longcui-portrait-angle-review');angle_report=json.loads((angles/'report.json').read_text());assert len(angle_report['rows'])==12
for row in angle_report['rows']:
 p=Path(row['capture']);assert sha(p)==row['sha256'];add(p,'angles/'+p.name)
add(angles/'report.json','angles/report.json');add('/tmp/garden-longcui-portrait-angle-review.log','angles/native.log');add('/tmp/garden_compare_longcui_portrait_angles.gd','angles/executed-comparison.gd');add('/tmp/garden-portrait-framing-selected.json','angles/selection-before-runtime-review.json')
review=Path('/tmp/garden-portrait-architecture-review');r=json.loads((review/'report.json').read_text());assert r['status']=='seven_regressions_and_both_full_native_tours_passed';assert len(r['phases'])==9
for phase in r['phases']:
 assert phase['exit_code']==0
 add(phase['log'],'regressions/'+Path(phase['log']).name)
add(review/'report.json','regressions/report.json');add('/tmp/garden_review_portrait_architecture.py','executed-review-runner.py')
tour_summary={}
for mode in ['desktop','portrait']:
 d=json.loads((review/(mode+'-tour.json')).read_text());assert d['route_sha256']==frozen['godot/runtime/entry_route.gd'];assert d['status']=='passed';assert len(d['legs'])==26;assert len(d['captures'])==139;assert len(set(d['visited_rooms']))==14;assert not d['floor_failures'];assert d['time_scale']==1;assert d['maximum_practicals']<=4
 count=0;grounded=0;supported=0
 for leg in d['legs']:
  grounded+=leg['grounded_ray_samples'];supported+=leg['supported_ray_samples'];assert not leg['centre_ray_misses'];assert leg['supported_ray_samples']==leg['grounded_ray_samples']
 for row in d['captures']:
  p=review/('tour-'+mode)/row['file'];assert sha(p)==row['sha256'];pixels=list(struct.unpack('>II',p.read_bytes()[16:24]));assert pixels==d['viewport']
  if row['phase']=='settled':add(p,'tour-'+mode+'/'+p.name);count+=1
 assert count==26
 add(review/(mode+'-tour.json'),'regressions/'+mode+'-tour.json')
 tour_summary[mode]={'rooms':14,'legs':26,'all_original_hashes_verified':139,'settled_originals_archived':count,'actual_capture_pixels':d['viewport'],'grounded_ray_samples':grounded,'supported_ray_samples':supported,'floor_misses':0}
log=Path('/tmp/garden-portrait-architecture-import.log');assert not re.search(r'ERROR:|SCRIPT ERROR:',log.read_text());add(log,'production-import.log')
summary={'status':'three_portrait_overviews_and_camera_behavior_verified','source_glb_sha256':sha(root/'godot/assets/garden-of-dreams.glb'),'route_sha256':frozen['godot/runtime/entry_route.gd'],'red_failures':13,'final_behavior_captures':15,'regression_phases':9,'tours':tour_summary,'archive_scope':'All red, intermediate, selected and angle originals; all reports and logs; all 26 settled originals per walk. All 139 originals per walk verified; transient travel originals remain in the recorded local review folder. Runtime cameras only; final art, device budgets and services remain open.'}
(archive/'review-summary.json').write_text(json.dumps(summary,indent=2)+'\n');files[str((archive/'review-summary.json').relative_to(root))]=sha(archive/'review-summary.json')
(archive/'artifact-locations.json').write_text(json.dumps(locations,indent=2)+'\n');files[str((archive/'artifact-locations.json').relative_to(root))]=sha(archive/'artifact-locations.json')
index={'status':summary['status'],'scope':summary['archive_scope'],'files':files}
(root/'export/portrait-architecture-runtime-evidence.json').write_text(json.dumps(index,indent=2)+'\n')
for name,h in files.items():assert sha(root/name)==h
print('PORTRAIT_ARCHIVE_PASS',len(files),'unique files',len(locations),'logical artifacts');print(json.dumps(summary,indent=2))
