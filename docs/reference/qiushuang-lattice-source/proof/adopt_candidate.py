"""Adopt a fully validated candidate with a verified reversible file backup."""
from pathlib import Path
import json,hashlib,shutil,subprocess
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path('/tmp/garden-qiushuang-lattice-20261010')
backup=repo/'.superpowers/sdd/2026-09-23-garden-completion/qiushuang-lattice-adoption-20261011'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='72ad817f07e1fb13b565197f0a39984a2d97bc1c7c3dff6c1bccf3ae1125cab1'
assert not backup.exists(),'Do not overwrite an adoption backup'
assert sha(repo/'blender/authoring.blend')=='0f93c42421a17b85b297fa0ff5447fad95cb7b98afeff183a2282ffe060492a4'
assert sha(repo/'export/garden-of-dreams.glb')=='faa8a7fe4a7a399899e84373c0550c8ff2f5f15ab0273109e8ea68f433b8fe0f'
assert sha(repo/'godot/runtime/entry_route.gd')=='ec42ec55bf382ec314b6da325da741d214d297d81418d4da38bdabe0d017ec87'
assert sha(root/'export/garden-of-dreams.glb')==expected
assert json.loads((root/'tour-jobs.json').read_text())['status']=='both_native_full_tours_passed','Both native tours must finish before adoption'
for shape in ['desktop','portrait']:
 d=json.loads((root/f'lit-tour-{shape}/report.json').read_text())
 assert d['status']=='passed' and len(d['legs'])==26 and len(d['visited_rooms'])==14 and not d['floor_failures']
 assert d['source_glb_sha256']==expected and len(d['settled_arrivals'])==26
assert json.loads((root/'generator-reproduction.json').read_text())['status']=='passed'
assert json.loads((root/'canonical-replay-green.json').read_text())['status']=='passed'
assert json.loads((root/'canonical-replay-baseline.json').read_text())['status']=='passed'
assert json.loads((root/'native-lit-file-verification.json').read_text())['decoded_and_verified_png']==72
assert json.loads((root/'direct-lit-review.json').read_text())['status']=='bounded_lattice_change_accepted_final_art_pending'
refresh=json.loads((root/'export/full-lighting-refresh.json').read_text())
assert refresh['status']=='source_complete' and len(refresh['phases'])==6 and all(p['exit_code']==0 for p in refresh['phases'])
for name,h in json.loads((root/'full-lighting-inputs.json').read_text())['files'].items():assert sha(root/name)==h,name
branch=subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()
assert branch=='codex/qiushuang-screen-lattice'
assert not subprocess.check_output(['git','diff','--name-only'],cwd=repo,text=True).strip()
copies={}
def add(source,target):copies[target]=source
for name in ['blender/authoring.blend','blender/master.blend','export/garden-of-dreams.glb','export/sites/SITE_qiushuang-zhai.glb','export/manifest.json','export/full-lighting-refresh.json','export/site-wash-rig.json','export/candidate-libraries.json','export/lightmaps-coverage.json','export/lightmap-pixels.json','export/terminal-spill-pixels.json']:
 add(root/name,repo/name)
for folder in ['blender/sites','export/lightmaps']:
 for file in (root/folder).rglob('*'):
  if file.is_file() and file.suffix in ['.blend','.png','.json']:add(file,repo/file.relative_to(root))
add(root/'canonical_export_garden.py',repo/'scripts/export_garden.py')
add(root/'canonical_complete_garden.py',repo/'scripts/complete_garden.py')
add(root/'lattice_contract.py',repo/'scripts/qiushuang_lattice_contract.py')
old={};new={}
for target,source in copies.items():
 assert source.is_file(),source
 relative=str(target.relative_to(repo));new[relative]=sha(source)
 if target.exists():
  saved=backup/relative;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,saved)
  assert sha(saved)==sha(target);old[relative]=sha(saved)
 else:old[relative]=None
(backup/'backup-manifest.json').write_text(json.dumps({'files':old,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()},indent=2)+'\n')
for name,h in old.items():
 if h:assert sha(backup/name)==h,name
for target,source in copies.items():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
for name,h in new.items():assert sha(repo/name)==h,name
assert sha(repo/'godot/runtime/entry_route.gd')=='ec42ec55bf382ec314b6da325da741d214d297d81418d4da38bdabe0d017ec87'
(root/'adoption.json').write_text(json.dumps({'status':'source_adopted_engine_sync_and_installed_validation_pending','branch':branch,'source_glb_sha256':expected,'backup':str(backup),'backed_up_files':len(old),'copied_files':new,'scope':'Source and full fresh bakes adopted after isolated native gates. No editor reload, device action or final art acceptance.'},indent=2)+'\n')
print('QIUSHUANG_SOURCE_ADOPTION_PASS',len(new),flush=True)
