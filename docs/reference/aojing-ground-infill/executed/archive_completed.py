from pathlib import Path
import json,hashlib,shutil
r=Path(__file__).resolve().parent;repo=Path('/Users/auchan/projects/garden-of-dreams');arc=repo/'.superpowers/sdd/2026-09-23-garden-completion/aojing-ground-lit-20261013';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((r/'isolated-pipeline.json').read_text())['status']=='isolated_source_native_tours_complete_direct_review_adoption_pending'
files={p for p in r.iterdir() if p.is_file() and p.suffix in ['.json','.py','.gd','.log']}
files.update(p for p in (r/'export').glob('*.json'))
for folder in ['export/lightmaps','native-lit-ground','native-lit-corridor','lit-arrivals-desktop','lit-arrivals-portrait','lit-framing-normal','lit-framing-touch','lit-tour-desktop','lit-tour-portrait','lit-validation-logs','failed-native-winding-01']:
 files.update(p for p in (r/folder).rglob('*') if p.is_file() and p.suffix in ['.json','.py','.gd','.log','.png'])
for p in sorted(files):
 out=arc/p.relative_to(r);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);assert sha(out)==sha(p)
manifest={'status':'completed_ground_lighting_native_tours_direct_review_archived','source_glb_sha256':'09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290','prior_source_archive':str(repo/'.superpowers/sdd/2026-09-23-garden-completion/aojing-ground-export-v2-20261011'),'files':{str(p.relative_to(arc)):sha(p) for p in sorted(arc.rglob('*')) if p.is_file() and p!=arc/'files.json'}}
(arc/'files.json').write_text(json.dumps(manifest,indent=2)+'\n')
for n,h in manifest['files'].items():assert sha(arc/n)==h,n
print('GROUND_COMPLETED_ARCHIVE_PASS',len(manifest['files']))
