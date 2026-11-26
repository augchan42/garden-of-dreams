"""Adopt the reviewed Aojing ground with exact reversible backups and stage guards."""
from pathlib import Path
import argparse,json,hashlib,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
r=Path(__file__).resolve().parent;repo=Path('/Users/auchan/projects/garden-of-dreams');backup=repo/'.superpowers/sdd/2026-09-23-garden-completion/aojing-ground-adoption-20261013';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected='09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290'
def gate(n,status):
 d=json.loads((r/n).read_text());assert d.get('status')==status,(n,d.get('status'));return d
baseline=gate('adoption-baseline.json','prepared_current_stage_branch')
assert not backup.exists(),'Inspect existing backup rather than repeat adoption'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==baseline['head']
assert not subprocess.check_output(['git','diff','--name-only'],cwd=repo,text=True).strip()
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo,text=True).strip()
for n,status in [('isolated-pipeline.json','isolated_source_native_tours_complete_direct_review_adoption_pending'),('export/full-lighting-refresh.json','source_complete'),('lit-validation.json','isolated_lit_views_and_resource_checks_passed_tours_and_direct_review_pending'),('native-lit-file-verification.json','passed'),('tour-jobs.json','both_native_full_tours_passed'),('tour-file-verification.json','passed')]:
 d=gate(n,status)
 if 'source_glb_sha256' in d:assert d['source_glb_sha256']==expected
 if 'phases' in d:assert all(x.get('status')=='passed' and x.get('exit_code')==0 for x in d['phases'])
assert len(json.loads((r/'export/full-lighting-refresh.json').read_text())['phases'])==6
assert len(json.loads((r/'lit-validation.json').read_text())['phases'])==17
review=gate('direct-lit-review.json','bounded_ground_infill_accepted_final_art_pending');native=gate('native-lit-file-verification.json','passed');tour=gate('tour-file-verification.json','passed')
required={n for n in native['files'] if n.startswith(('native-lit-ground/','native-lit-corridor/','lit-arrivals-'))};assert len(required)==50 and set(review['files'])==required and review['direct_originals_reviewed']==50
assert native['decoded_and_verified_png']==86 and tour['decoded_and_verified_png']==278
for n,d in {**native['files'],**tour['files']}.items():assert sha(r/n)==d['sha256'],n
for n,h in review['files'].items():assert h==sha(r/n)==native['files'][n]['sha256'],n
for shape in ['desktop','portrait']:
 d=json.loads((r/f'lit-tour-{shape}/report.json').read_text());assert d['status']=='passed' and d['source_glb_sha256']==expected and len(d['legs'])==26 and len(d['visited_rooms'])==14 and len(d['settled_arrivals'])==26 and not d['floor_failures']
assert gate('canonical-replay.json','canonical_replay_16_glbs_byte_exact')['source_glb_sha256']==expected
preserve=gate('export/export-preservation.json','ground_export_preservation_passed');assert preserve['before_sha256']=='7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b' and preserve['after_sha256']==expected and preserve['original_triangles_preserved']==277543 and preserve['added_triangle_count']==12 and preserve['exact_nodes_materials_cameras_colliders'] and preserve['embedded_images_exact']
ground=gate('export/ground-native-green.json','passed');assert ground['facts']['source_glb_sha256']==expected and ground['facts']['added_box_triangles']==ground['facts']['clockwise_outward_faces_checked']==12
for n,h in json.loads((r/'full-lighting-inputs.json').read_text())['files'].items():assert sha(r/n)==h,n
for n,h in baseline['files'].items():assert (sha(repo/n) if (repo/n).exists() else None)==h,('Production changed',n)
for n,h in baseline['candidate_files'].items():assert sha(r/n)==h,('Candidate changed',n)
for n,h in baseline['protected_files'].items():assert sha(repo/n)==h,('Protected input changed',n)
for n,params in baseline['protected_import_parameters'].items():assert (repo/n).read_text().split('[params]',1)[1]==params,n
assert sha(r/'export/garden-of-dreams.glb')==expected
if a.check:print('AOJING_GROUND_ADOPTION_PREFLIGHT_PASS',len(baseline['files']));raise SystemExit(0)
assert subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()=='codex/aojing-ground-infill'
for n,h in baseline['files'].items():
 if h:
  out=backup/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/n,out);assert sha(out)==h
backup.mkdir(parents=True,exist_ok=True);(backup/'backup-manifest.json').write_text(json.dumps(baseline,indent=2)+'\n')
for n,h in baseline['candidate_files'].items():
 out=repo/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,out);assert sha(out)==h
for n,h in baseline['protected_files'].items():assert sha(repo/n)==h,n
for n,params in baseline['protected_import_parameters'].items():assert (repo/n).read_text().split('[params]',1)[1]==params,n
(r/'adoption.json').write_text(json.dumps({'status':'ground_source_engine_adopted_installed_checks_pending','source_glb_sha256':expected,'branch':'codex/aojing-ground-infill','backup':str(backup),'copied_files':baseline['candidate_files'],'protected_stage_kit_and_runtime_files':len(baseline['protected_files']),'protected_import_parameters':len(baseline['protected_import_parameters']),'scope':'Exact reviewed ground source, canonical exports, fresh bakes and pin fixtures copied. Current stage-kit input bytes preserved. No editor reload, device or final art acceptance.'},indent=2)+'\n');print('AOJING_GROUND_ADOPTION_PASS',len(baseline['files']))
