from pathlib import Path
import hashlib,json,shutil,tempfile
repo=Path('/Users/auchan/projects/garden-of-dreams');src=Path(json.load(open('/tmp/garden-tile-ridge-candidate.json'))['folder']);review=Path(json.load(open('/tmp/garden-tile-chart-full-review.json'))['folder']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected='b540496a9129879389a96f5fff0cf59c04c0ff116fa44f2a2389fee3f643f4f1';author='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c'
assert sha(src/'blender/authoring.blend')==author
assert sha(src/'export/garden-of-dreams.glb')==sha(review/'godot/assets/garden-of-dreams.glb')==expected
b=json.loads((src/'export/full-lighting-refresh.json').read_text());assert b['status']=='source_complete' and all(x['status']=='passed' and x['exit_code']==0 for x in b['phases'])
j=json.loads((review/'review-pipeline.json').read_text());assert j['status']=='technical_checks_complete_visual_review_pending'
j['source_native_pixel_indexes_sha256']={}
for name in ['lightmap-pixels.json','terminal-spill-pixels.json']:
 assert sha(src/'export'/name)==sha(review/'export'/name)
 records=json.loads((src/'export'/name).read_text());assert len(records)==(124 if name=='lightmap-pixels.json' else 7)
 for key,record in records.items():
  image=key if name=='lightmap-pixels.json' else key+'_terminal_spill.png'
  if name=='terminal-spill-pixels.json':
   matching=[p for p in (src/'export/lightmaps').rglob('*.png') if sha(p)==record['png_sha256']];assert len(matching)==1;image=str(matching[0].relative_to(src/'export/lightmaps'))
  assert sha(src/'export/lightmaps'/image)==record.get('sha256',record.get('png_sha256')) and record['finite']
 j['source_native_pixel_indexes_sha256'][name]=sha(src/'export'/name)
(review/'review-pipeline.json').write_text(json.dumps(j,indent=2)+'\n')
work=Path(tempfile.mkdtemp(prefix='tile-chart-adoption-',dir=repo/'.superpowers/sdd/2026-09-23-garden-completion'));stage=work/'stage';stage.mkdir();backup=work/'backup';backup.mkdir()
pairs=[('blender/authoring.blend',src/'blender/authoring.blend'),('blender/master.blend',src/'blender/master.blend'),('blender/sites',src/'blender/sites'),('export/sites',src/'export/sites'),('export/lightmaps',src/'export/lightmaps'),('export/garden-of-dreams.glb',src/'export/garden-of-dreams.glb'),('godot/assets/garden-of-dreams.glb',review/'godot/assets/garden-of-dreams.glb'),('godot/assets/garden-source.json',review/'godot/assets/garden-source.json'),('godot/lightmaps',review/'godot/lightmaps'),('godot/tests/moon-paint-atlas.json',review/'godot/tests/moon-paint-atlas.json'),('godot/tests/source-contract.json',review/'godot/tests/source-contract.json'),('godot/project.godot',review/'godot/project.godot')]
for n in ['manifest.json','site-wash-rig.json','site-source-audit.json','candidate-libraries.json','full-lighting-refresh.json','lightmap-pixels.json','lightmaps-coverage.json','terminal-spill-pixels.json']:pairs.append(('export/'+n,src/'export'/n))
def digest_tree(p):
 if not p.exists():return None
 if p.is_file():return {'file':sha(p)}
 return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file()}
plan={'status':'prepared_not_applied','source_glb_sha256':expected,'authoring_sha256':author,'source_root':str(src),'review_root':str(review),'work':str(work),'items':[],'scope':'Working-scene adoption of preserved pavilion geometry with outward tile normals and explicit UV2 charts, and a complete fresh matching lighting bundle; whole-site art and complete goal acceptance remain open. Apply requires both native full walks to pass and all staged/current bytes to match these snapshots. Default launch remains the fourteen-room exploration route; the dedicated first-reading demo scene remains available.'}
for rel,p in pairs:
 target=repo/rel;out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True)
 if p.is_dir():shutil.copytree(p,out,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
 else:shutil.copy2(p,out)
 expected_tree=digest_tree(p)
 if p.is_dir():expected_tree={k:v for k,v in expected_tree.items() if not k.endswith(('.blend1','.blend2'))}
 assert digest_tree(out)==expected_tree,rel
 plan['items'].append({'target':rel,'original':digest_tree(target),'staged':digest_tree(out)})
# Any changed extracted paint PNG/import must be included so the source hook cannot load stale image bytes.
for p in sorted((review/'godot/assets').glob('*')):
 if p.suffix not in ('.png','.import'):continue
 target=repo/'godot/assets'/p.name
 if digest_tree(p)!=digest_tree(target):
  rel='godot/assets/'+p.name;out=stage/rel;shutil.copy2(p,out);plan['items'].append({'target':rel,'original':digest_tree(target),'staged':digest_tree(out)})
(work/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');Path('/tmp/garden-tile-chart-adoption.json').write_text(json.dumps({'work':str(work),'plan':str(work/'plan.json')},indent=2)+'\n');print('ADOPTION_STAGED',len(plan['items']),str(work))
