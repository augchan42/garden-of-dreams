from pathlib import Path
import hashlib,json,shutil
from PIL import Image
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path(json.loads(Path('/tmp/garden-hengwu-full-review.json').read_text())['folder']).resolve();dst=repo/'docs/reference/hengwu-camera-wait-review';dst.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files={};locations={}
def copy(p,name):
 target=dst/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);assert sha(target)==sha(p);files[str(target.relative_to(repo))]=sha(target);locations[str(name)]={'path':str(target.relative_to(repo)),'sha256':sha(target)}
first=json.loads((root/'first-review-pipeline.json').read_text());assert first['status']=='failed' and first['phases'][-1]['exit_code']==1
resumed=json.loads((root/'review-resume-pipeline.json').read_text());passed={p['name']:p for p in resumed['phases'] if p['status']=='passed'}
assert {'hengwu-lit-actions-completed','portrait-architecture-completed'}<=set(passed)
assert sha(root/'godot/runtime/entry_route.gd')==sha(repo/'godot/runtime/entry_route.gd')=='db32d9c058a732c330d9df910b22b961f755045c5904c47e8fde68fd3c056138'
copy(root/'first-review-pipeline.json',Path('first-review-pipeline.json'));copy(root/'first-lit-capture-pose-rejection.json',Path('first-lit-capture-pose-rejection.json'))
for p in (root/'first-attempt-tests').iterdir():copy(p,Path('first-test-inputs')/p.name)
for name in ['hengwu-lit-actions','portrait-architecture']:copy(root/'review-logs'/(name+'.log'),Path('first-logs')/(name+'.log'))
for name in ['hengwu-lit-actions-completed','portrait-architecture-completed']:
 phase=passed[name];assert sha(phase['log'])==phase['log_sha256'];copy(Path(phase['log']),Path('completed-logs')/(name+'.log'))
for prefix in ['review-captures','review-captures-completed-camera-waits']:
 for name in ['hengwu-lit-actions','portrait-architecture']:
  folder=root/prefix/name;d=json.loads((folder/'report.json').read_text());assert len(d['rows'])==(9 if name=='hengwu-lit-actions' else 15)
  if prefix.endswith('camera-waits'):
   assert all(not row['camera_transition_running'] for row in d['rows'])
   if name=='portrait-architecture':assert not d['errors'] and d['status']=='portrait_architecture_behavior_passed'
  for row in d['rows']:
   p=Path(row['capture']);assert sha(p)==row['sha256']
   with Image.open(p) as im:assert list(im.size)==row.get('actual_pixels',row.get('capture_pixels'))
   copy(p,Path(prefix)/name/p.name)
  copy(folder/'report.json',Path(prefix)/name/'report.json')
for name in ['test_portrait_architecture.gd','render_hengwu_lit_candidate.gd','portrait-architecture-contract.json']:
 copy(root/'godot/tests'/name,Path('completed-test-inputs')/name)
for p in [Path('/tmp/garden_resume_hengwu_full.py'),Path('/tmp/garden_build_hengwu_resume.py'),Path(__file__)]:copy(p,Path('executed-helpers')/p.name)
copy(root/'first-attempt-tests/test_portrait_architecture.gd',Path('preceding-production-test.gd'))
scope='Actual native RED five portrait errors and six incomplete Hengwu action poses, followed by completed camera-tween waits: nine exact action poses and fifteen zero-error portrait resize captures. Source26033 and runtime db32 unchanged; only camera-test waits corrected. Earlier outputs and all 48 original PNG hashes/dimensions retained. Full review/tours, adoption and final art remain separate.'
checkpoint={'status':'native_camera_wait_regression_passed_full_review_separate','scope':scope,'source_glb_sha256':first['source_glb_sha256'],'route_sha256':sha(repo/'godot/runtime/entry_route.gd'),'first_portrait_errors':5,'first_incomplete_action_poses':6,'completed_hengwu_captures':9,'completed_portrait_captures':15,'directly_viewed_completed_originals':['candidate-arrival-1410x600.png','candidate-rocks-390x844.png','candidate-read-1410x600.png'],'visual_limits':'Compact stone leaves more of the right court visible. Pierced close view and book remain readable; lower rock/roof clipping, wall cap, broad ceiling and facade/filtering/art quality remain open. Selected source-matched originals only, not final all-site acceptance.','artifact_locations':locations}
(dst/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
(dst/'README.md').write_text('''# Camera completion wait correction

The first native review captured six Hengwu actions before reaching their expected camera positions. Its portrait test reported five resize/framing errors while the detail and Look tweens were still running. Frame counts alone did not establish that the 1.4-second animations had finished. The source, project and runtime hashes matched the preceding reviewed versions.

The tests now wait for actual camera-tween completion, with a ten-second timeout. Completed Hengwu captures additionally check the expected public action positions. All nine arrival/rock/book captures match their completed poses; all fifteen portrait resize captures pass, with no moving camera at capture. The runtime is unchanged. First failures, incomplete frames, executed test versions and all 48 original PNGs are preserved with hashes and actual dimensions.

Three completed originals were directly inspected: desktop arrival, 390×844 pierced stone and desktop book. The compact stone opens more of the court edge; the table and holes remain readable. Rock close-up/roof clipping, wall cap, ceiling, facade filtering and other final art remain open. Complete tours, palette controls, final visual review and production adoption are separate. This is not physical-phone, sustained-performance, release or authenticated-service acceptance.
''')
for p in [dst/'checkpoint.json',dst/'README.md']:files[str(p.relative_to(repo))]=sha(p)
(repo/'export/hengwu-camera-wait-evidence.json').write_text(json.dumps({'status':checkpoint['status'],'scope':scope,'files':files},indent=2)+'\n')
print('HENGWU_CAMERA_WAIT_EVIDENCE_ARCHIVED',len(files),'unique files')
