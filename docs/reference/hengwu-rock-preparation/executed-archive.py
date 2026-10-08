import hashlib,json,shutil,struct
from pathlib import Path
repo=Path('/Users/auchan/projects/garden-of-dreams');work=Path(json.loads(Path('/tmp/garden-hengwu-compact-rock.json').read_text())['root']).resolve();a=repo/'docs/reference/hengwu-rock-preparation';a.mkdir(exist_ok=False);files={};paths={};locations={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(src,name):
 src=Path(src);h=sha(src)
 if h in paths:dest=paths[h]
 else:dest=a/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);paths[h]=dest;files[str(dest.relative_to(repo))]=h
 locations[name]={'original_path':str(src),'archive_path':str(dest.relative_to(repo)),'sha256':h}
# Existing immutable baseline evidence already retains the production source.
for index in ['neutral-atlas-full-lighting-evidence.json','neutral-atlas-native-review-evidence.json']:
 for path,h in json.loads((repo/'export'/index).read_text())['files'].items():
  if h in [sha(repo/'blender/authoring.blend'),sha(repo/'godot/assets/garden-of-dreams.glb')]:
   assert sha(repo/path)==h;paths[h]=repo/path;files[path]=h
add(repo/'blender/authoring.blend','baseline/authoring.blend');add(repo/'godot/assets/garden-of-dreams.glb','baseline/garden-of-dreams.glb')
add(work/'blender/authoring.blend','candidate/authoring.blend');add(work/'export/garden-of-dreams.glb','candidate/garden-of-dreams.glb');add(work/'export/sites/SITE_hengwu-yuan.glb','candidate/SITE_hengwu-yuan.glb')
for name in ['source-review.json','export-preservation.json','fixture-preparation.json','full-lighting-inputs.json']:add(work/name,name)
for folder in ['native-geometry-review','native-geometry-review-corrected','native-geometry-review-actions-settled','native-physics-review']:
 for p in sorted((work/folder).rglob('*')):
  if p.is_file():add(p,folder+'/'+p.name)
# Check original pixels/hash and actual completed public action poses.
for variant in ['baseline','candidate']:
 d=json.loads((work/'native-geometry-review-actions-settled'/(variant+'-report.json')).read_text());assert len(d['rows'])==9
 for row in d['rows']:
  p=Path(row['capture']);assert sha(p)==row['sha256'];assert list(struct.unpack('>II',p.read_bytes()[16:24]))==row['actual_pixels']
  expected={'arrival':[-17.5,2.6,-10.5],'rocks':[-15.6,1.6,-10.6],'read':[-18,1.8,-13.4]}[row['action']];assert max(abs(x-y) for x,y in zip(row['camera_position'],expected))<1e-4
for group in ['garden-hengwu-camera-review','garden-hengwu-camera-review-identity-corrected']:
 for p in sorted((Path('/tmp')/group).glob('*')):
  if p.is_file():add(p,group+'/'+p.name)
 add('/tmp/'+group+'.log',group+'/native.log')
d=json.loads(Path('/tmp/garden-hengwu-camera-review-identity-corrected/report.json').read_text());assert not d['errors'] and len(d['rows'])==19
for row in d['rows']:
 p=Path(row['capture']);assert sha(p)==row['sha256'];assert list(struct.unpack('>II',p.read_bytes()[16:24]))==row['actual_pixels']
for name in ['garden_hengwu_camera_review.gd','garden_hengwu_camera_review-first-graded-id.gd','garden_inspect_hengwu_foreground.py','garden_prepare_hengwu_compact_rock.py','garden_prepare_hengwu_compact_rock-first-collider-transform.py','garden_compare_hengwu_candidate.py','garden_compare_hengwu_candidate-first-node-transform.py','garden_check_hengwu_collider_anchor.py','garden_render_hengwu_rock_candidate.gd','garden_render_hengwu_rock_candidate-parse-failed.gd','garden_render_hengwu_rock_candidate-before-action-settling.gd','garden_run_hengwu_rock_candidate.py','garden_run_hengwu_rock_candidate-first.py','garden_run_hengwu_rock_candidate-before-action-settling.py','garden_test_hengwu_compact_collider.gd','garden_review_hengwu_compact_physics.py','garden_prepare_hengwu_full_lighting.py','garden-hengwu-saved-foreground.json','garden-hengwu-saved-foreground.log','garden-hengwu-collider-anchor-red.log','garden-hengwu-collider-anchor-green.log','garden-hengwu-compact-rock.log','garden-hengwu-compact-rock-corrected.log','garden-hengwu-export-preservation.log','garden-hengwu-camera-review-launch-failed.log']:
 add('/tmp/'+name,'executed-and-diagnostics/'+name)
old=Path(json.loads(Path('/tmp/garden-hengwu-compact-rock-first-collider-transform.json').read_text())['root']).resolve();add(old/'export/garden-of-dreams.glb','rejected-collider-transform/garden-of-dreams.glb');add(old/'source-review.json','rejected-collider-transform/source-review.json');add(old/'export-preservation.json','rejected-collider-transform/export-preservation.json')
# Running state is a timestamped checkpoint, not a completed-bake claim.
add(work/'lighting-preparation.json','lighting-preparation-at-checkpoint.json');add(work/'export/full-lighting-refresh.json','full-lighting-refresh-at-checkpoint.json')
for p in sorted((work/'lighting-preparation-logs').glob('*.log')):
 if p.name!='full-lighting.log':add(p,'lighting-preparation/'+p.name)
summary={'status':'isolated_compact_hengwu_rock_verified_fresh_lighting_running','root':str(work),'production_source_sha256':sha(repo/'godot/assets/garden-of-dreams.glb'),'candidate_source_sha256':sha(work/'export/garden-of-dreams.glb'),'candidate_authoring_sha256':sha(work/'blender/authoring.blend'),'changed_native_objects':['HENGWU_perforated_rock','COL_hengwu_rock'],'other_site_glbs_byte_identical':14,'expanded_candidate_indexed_triangles':247190,'completed_public_action_captures':18,'surface_identity_comparison_captures':19,'physics_checks_passed':3,'scope':'Saved isolated native candidate/export preservation, controlled native pixel identity, unbaked comparisons and adjacent physics. Fifteen libraries and portable master prepared and retained in local source folder with frozen hashes. Complete six-phase lighting currently running; no production adoption or final visual/whole-goal acceptance.'}
(a/'review-summary.json').write_text(json.dumps(summary,indent=2)+'\n');files[str((a/'review-summary.json').relative_to(repo))]=sha(a/'review-summary.json')
(a/'artifact-locations.json').write_text(json.dumps(locations,indent=2)+'\n');files[str((a/'artifact-locations.json').relative_to(repo))]=sha(a/'artifact-locations.json')
shutil.copyfile('/tmp/archive_hengwu_rock_preparation.py',a/'executed-archive.py');files[str((a/'executed-archive.py').relative_to(repo))]=sha(a/'executed-archive.py')
(repo/'export/hengwu-rock-preparation-evidence.json').write_text(json.dumps({'status':summary['status'],'scope':summary['scope'],'files':files},indent=2)+'\n')
for path,h in files.items():assert sha(repo/path)==h
print('HENGWU_PREPARATION_ARCHIVE_PASS',len(files),'unique files',len(locations),'logical artifacts');print(json.dumps(summary,indent=2))
