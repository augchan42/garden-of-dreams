from pathlib import Path
import json, hashlib, shutil, tempfile, subprocess
repo = Path('/Users/auchan/projects/garden-of-dreams')
work = Path(tempfile.mkdtemp(prefix='garden-tubi-framing-')).resolve()
source = Path(json.loads(Path('/tmp/garden-hengwu-detail-framing.json').read_text())['folder']) / 'godot'
shutil.copytree(source, work / 'godot', ignore=shutil.ignore_patterns('acceptance-captures', 'captures', 'android', 'export', '*.log'))
shutil.copytree(repo / 'godot/runtime', work / 'godot/runtime', dirs_exist_ok=True)
shutil.copyfile('/tmp/garden_compare_tubi_framing.gd', work / 'godot/tests/compare_tubi_framing.gd')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(work/'godot/assets/garden-of-dreams.glb') == sha(repo/'godot/assets/garden-of-dreams.glb') == '26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'
preservation=json.loads((repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-detail-runtime/source-preservation.json').read_text())
for path,digest in preservation['source']['lighting_pngs'].items():
 if path.startswith('godot/'):
  assert sha(work/path)==digest,path
report={'status':'isolated_camera_probe_prepared','folder':str(work),'source_glb_sha256':sha(work/'godot/assets/garden-of-dreams.glb'),'route_sha256':sha(work/'godot/runtime/entry_route.gd'),'main_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'engine_lightmap_count':141}
(work/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
Path('/tmp/garden-tubi-framing.json').write_text(json.dumps({'folder':str(work)},indent=2)+'\n')
print('TUBI_PREPARED', work)
