"""Preserve native review/adoption bytes, reusing only independently checked hashes."""
from pathlib import Path
import json,hashlib,shutil,datetime
repo=Path('/Users/auchan/projects/garden-of-dreams')
root=Path(json.load(open('/tmp/garden-hengwu-full-review.json'))['folder']).resolve()
work=Path(json.load(open('/tmp/garden-hengwu-adoption.json'))['work'])
dst=repo/'docs/reference/hengwu-native-review';dst.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
files={};locations={};cache={}
for index in (repo/'export').glob('*evidence.json'):
 try:j=json.load(open(index))
 except (ValueError,OSError):continue
 for rel,digest in j.get('files',{}).items():
  if isinstance(digest,str) and len(digest)==64 and (repo/rel).is_file():cache.setdefault(digest,repo/rel)
def keep(p,name):
 p=Path(p);digest=sha(p);name=str(name)
 previous=cache.get(digest)
 if previous is not None and sha(previous)==digest:out=previous
 else:
  out=dst/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);assert sha(out)==digest;cache[digest]=out
 rel=str(out.relative_to(repo));files[rel]=digest;locations[name]={'path':rel,'sha256':digest}
accepted=json.load(open(root/'accepted-working-review.json'));app=json.load(open(work/'application.json'))
assert app['status']=='working_scene_adopted_checks_passed' and len(app['checks'])==11
assert accepted['source_glb_sha256']==app['source_glb_sha256']=='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'
for name in ['review-pipeline.json','first-review-pipeline.json','review-resume-pipeline.json','accepted-working-review.json','first-lit-capture-pose-rejection.json']:
 keep(root/name,Path('reports')/name)
for phase in json.load(open(root/'review-pipeline.json'))['phases']+json.load(open(root/'review-resume-pipeline.json'))['phases']:
 assert sha(phase['log'])==phase['log_sha256'];keep(phase['log'],Path('logs')/(phase['name']+'.log'))
for rel,digest in accepted['runtime_inputs_sha256'].items():
 assert sha(root/'godot'/rel)==digest;keep(root/'godot'/rel,Path('executed-runtime')/rel)
for rel in ['godot/tests/source-contract.json','godot/tests/garden-palette-contract.json','godot/tests/portrait-architecture-contract.json','godot/tests/moon-paint-atlas.json','godot/assets/garden-source.json']:
 keep(root/rel,Path('review-contracts')/Path(rel).name)
for p in sorted((root/'export').glob('*.json')):keep(p,Path('review-export-reports')/p.name)
for p in sorted(root.glob('*.json')):
 if p.name not in ['accepted-working-review.json','review-pipeline.json','review-resume-pipeline.json','first-review-pipeline.json','first-lit-capture-pose-rejection.json']:keep(p,Path('review-reports')/p.name)
for p in sorted((root/'scripts').glob('*.py')):keep(p,Path('executed-scripts')/p.name)
for p in sorted((root/'review-captures-completed-camera-waits').rglob('*')):
 if p.is_file() and p.suffix in ('.png','.json'):keep(p,Path('completed-captures')/p.relative_to(root/'review-captures-completed-camera-waits'))
verified=Path(accepted['verified_root'])
for name in ['saved-source-verification.json','verification.json']:keep(verified/name,Path('saved-default-reexport')/name)
for rel,digest in accepted['default_export_equality'].items():
 assert sha(verified/'export'/rel)==digest;keep(verified/'export'/rel,Path('saved-default-reexport/export')/rel)
for name in ['plan.json','application.json','production-import.json','production-palette-normal.json','production-palette-demo.json']:keep(work/name,Path('adoption')/name)
for phase in app['checks']:
 assert phase['status']=='passed' and phase['exit_code']==0 and sha(phase['log'])==phase['log_sha256'];keep(phase['log'],Path('adoption/logs')/Path(phase['log']).name)
for p in sorted((work/'production-portrait-architecture').rglob('*')):
 if p.is_file() and p.suffix in ('.png','.json'):keep(p,Path('adoption/portrait-architecture')/p.name)
for name in ['garden_prepare_hengwu_adoption.py','garden_apply_hengwu_adoption.py','garden_apply_hengwu_adoption-preflight-syntax-error.py','garden_prepare_hengwu_review.py','garden_review_hengwu_full.py','garden_resume_hengwu_full.py','garden_build_hengwu_resume.py']:
 keep(Path('/tmp')/name,Path('executed-helpers')/name)
keep(Path(__file__),Path('executed-helpers')/Path(__file__).name)
scope='Compact Hengwu stone and anchored collider adopted with matching freshly baked lighting. Completed desktop and portrait walks, original captures, seven intended rejection controls, canonical default reexport and eleven checks on installed production files. Final art/framing, phone/sustained budgets, remaining references and services remain open.'
checkpoint={'status':'working_scene_adopted_checks_passed','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':scope,'source_glb_sha256':app['source_glb_sha256'],'authoring_sha256':app['authoring_sha256'],'review_checks':47,'expected_rejection_controls':7,'source_phases':6,'default_glb_reexports':16,'production_checks':11,'walks':accepted['walks'],'stationary_native_memory':accepted['stationary_native_memory'],'selected_originals_reviewed':accepted['selected_originals_reviewed'],'visual_notes':accepted['visual_notes'],'artifact_locations':locations}
(dst/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
(dst/'README.md').write_text('''# Hengwu stone and lighting adoption

The closest pierced stone is narrower and lower, with smoothed faces and a small bevel. Its collider is scaled around the existing floor anchor. The book table, four stools, two other stones, cameras and the other fourteen site exports are preserved. The saved Blender authoring file reproduces all sixteen GLBs with the canonical exporter defaults.

All six source-lighting phases completed for 124 ordinary meshes and 141 source PNGs including backdrop wash and terminal spill. The combined review contains 47 completed checks and seven deliberate rejection controls. Failed first camera captures remain archived separately; corrected tests wait for actual tween completion. Nine completed Hengwu actions and fifteen portrait resize captures pass. The runtime is unchanged.

Desktop and portrait walks each visit fourteen rooms over twenty-six legs, retain 139 original PNGs, and record 17,582 supported grounded samples with zero floor misses. These are native Mac checks. Stationary texture allocation is 52,600,513 bytes at the normal-mode peak and 43,512,435 bytes in demo mode. These numbers do not establish phone, sustained or frame-timing acceptance.

The source and matching Godot assets were installed using checked staging hashes and backups. Eleven checks on the installed working project passed: import, source contract, full lighting, backdrop wash in both modes, terminal spill in both modes, surface materials, palette in both modes, and completed portrait architecture behavior.

All nine Hengwu action originals and four settled walk originals were inspected. The smaller stone opens more of the courtyard. Narrow book/rock framing, the roof crop, foreground wall cap and facade lighting still need work. This is an incremental adoption, not final all-site art or full-goal completion.

The checkpoint maps every logical artifact to its exact bytes. Unchanged artifacts reuse an existing archive only after their bytes were checked. All 278 walk originals are retained. The application report and backed-up plan preserve the previous and installed hashes. A staging-helper syntax error was corrected before preflight or mutation; that helper version is retained for diagnostics.
''')
for p in [dst/'README.md',dst/'checkpoint.json']:files[str(p.relative_to(repo))]=sha(p)
for rel,digest in files.items():assert sha(repo/rel)==digest,rel
(repo/'export/hengwu-native-review-evidence.json').write_text(json.dumps({'status':checkpoint['status'],'scope':scope,'files':files},indent=2)+'\n')
print('HENGWU_NATIVE_EVIDENCE_ARCHIVED',len(locations),'logical',len(files),'unique checked files',flush=True)
