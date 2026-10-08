"""Archive the completed Hengwu source bake; native acceptance remains separate."""
from pathlib import Path
import hashlib,json,shutil,datetime
repo=Path('/Users/auchan/projects/garden-of-dreams');source=Path(json.loads(Path('/tmp/garden-hengwu-compact-rock.json').read_text())['root']).resolve();dst=repo/'docs/reference/hengwu-full-lighting';dst.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prepared=json.loads((source/'lighting-preparation.json').read_text());bake=json.loads((source/'export/full-lighting-refresh.json').read_text());freeze=json.loads((source/'full-lighting-inputs.json').read_text())['files']
assert prepared['status']=='complete_source_lighting_passed_native_review_pending' and bake['status']=='source_complete'
assert [p['name'] for p in bake['phases']]==['ordinary','backdrop-wash','terminal-spill','terminal-spill-pixels','native-pixels','coverage'] and all(p['status']=='passed' and p['exit_code']==0 for p in bake['phases'])
assert bake['coverage']['expected_meshes']==bake['coverage']['baked_meshes']==124 and not bake['coverage']['missing']
assert sha(source/'export/garden-of-dreams.glb')==bake['source_glb_sha256']==prepared['source_glb_sha256']=='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'
assert sha(source/'blender/authoring.blend')==prepared['authoring_sha256']=='19eb386d8e93007ebd8e4ae2d9ee59ec7daa07dcd8dbe3c3a88d4ec84b5e5a08'
existing={}
for index in sorted((repo/'export').glob('*evidence.json')):
 record=json.loads(index.read_text())
 for path,digest in record.get('files',{}).items():
  if isinstance(digest,str):existing.setdefault(digest,path)
 for row in record.get('artifacts',[]):
  if 'path' in row and 'sha256' in row:existing.setdefault(row['sha256'],row['path'])
files={};locations={};reuse_cache={}
def retain(original,relative):
 digest=sha(original);old=existing.get(digest)
 valid=False
 if old:
  if old not in reuse_cache:reuse_cache[old]=(repo/old).is_file() and sha(repo/old)==digest
  valid=reuse_cache[old]
 if valid:archived=old
 else:
  target=dst/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target);assert sha(target)==digest;archived=str(target.relative_to(repo))
 files[archived]=digest;locations[str(relative)]={'path':archived,'sha256':digest}
for name,digest in freeze.items():
 assert sha(source/name)==digest,name
 retain(source/name,Path('frozen-source')/name)
for p in sorted((source/'export/lightmaps').rglob('*')):
 if p.is_file():retain(p,Path('source-lightmaps')/p.relative_to(source/'export/lightmaps'))
for name in ['lighting-preparation.json','full-lighting-inputs.json','export-preservation.json']:
 retain(source/name,Path(name))
for name in ['full-lighting-refresh.json','lightmaps-coverage.json','lightmap-pixels.json','terminal-spill-pixels.json']:
 retain(source/'export'/name,Path(name))
for phase in prepared['phases']:
 retain(Path(phase['log']),Path('preparation-logs')/(phase['name']+'.log'))
for phase in bake['phases']:
 retain(Path(phase['log']),Path('native-bake-logs')/(phase['name']+'.log'))
retain(Path('/tmp/garden_prepare_hengwu_full_lighting.py'),Path('executed-preparation.py'));retain(Path(__file__),Path('executed-archive.py'))
assert len([name for name in locations if name.startswith('source-lightmaps/') and name.endswith('.png')])==141
scope='Complete fresh lighting for isolated compact Hengwu stone source26033/author19eb, with saved libraries/shared receiver master and all 240 frozen inputs. Native visual/material/physics review, canonical reexport and production adoption remain separate. Final all-site art, five references, devices, release and authenticated services remain open.'
checkpoint={'status':'complete_hengwu_source_lighting_native_review_separate','scope':scope,'source_glb_sha256':bake['source_glb_sha256'],'authoring_sha256':prepared['authoring_sha256'],'ordinary_receivers':124,'source_png_files':141,'source_phases':6,'verified_frozen_inputs':len(freeze),'artifact_locations':locations,'native_review_pointer':'/tmp/garden-hengwu-full-review.json','archived_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(dst/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
(dst/'README.md').write_text('''# Hengwu compact-stone source lighting

All six source phases pass for isolated source `26033c99` / saved authoring `19eb386d`. The nearest pierced stone is compacted at its existing floor anchor; other source objects remain preserved as recorded in the preparation archive. Complete fresh lighting covers 124 ordinary receivers, backdrop wash and terminal spill: 141 original source PNGs in total.

`checkpoint.json` maps each source map, report, original log and all 240 frozen inputs to an archived path and SHA256. Matching prior immutable files are reused only after hashing their actual bytes. The saved fifteen libraries, portable receiver master, complete/site exports and copied helper inputs are preserved. Copied helpers are frozen inputs; this does not claim every helper was executed. Actual executed phases are listed by the completed preparation and bake reports and their original logs.

Godot review, default canonical reexport, visual acceptance and production adoption are separate. This archive does not establish final all-site art, physical-phone/2020 Adreno/sustained budgets, release or authenticated services. Five external references remain missing.
''')
for p in [dst/'checkpoint.json',dst/'README.md']:files[str(p.relative_to(repo))]=sha(p)
index=repo/'export/hengwu-full-lighting-evidence.json';index.write_text(json.dumps({'status':checkpoint['status'],'scope':scope,'files':files},indent=2)+'\n')
for name,digest in files.items():assert sha(repo/name)==digest,name
print('HENGWU_SOURCE_LIGHTING_ARCHIVED',len(locations),'logical artifacts',len(files),'unique verified files',flush=True)
