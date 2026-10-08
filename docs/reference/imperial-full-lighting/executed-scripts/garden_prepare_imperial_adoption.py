"""Stage the completed imperial working bundle with original failed gate retained."""
from pathlib import Path
import hashlib,json,shutil,tempfile
repo=Path('/Users/auchan/projects/garden-of-dreams')
src=Path(json.loads(Path('/tmp/garden-imperial-full-source.json').read_text())['folder']).resolve()
review=Path(json.loads(Path('/tmp/garden-imperial-chart-full-review.json').read_text())['folder']).resolve()
exporter=Path(json.loads(Path('/tmp/garden-imperial-default-export.json').read_text())['folder']).resolve()
follow=Path(json.loads(Path('/tmp/garden-oux-native-source.json').read_text())['folder']).resolve()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected='361a67c759974e4fb5897a15d5a7354076ef30392b7a6ed988cca6029f198611';author='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c'
a=json.loads((review/'review-pipeline.json').read_text());r=json.loads((review/'review-resume-pipeline.json').read_text());f=json.loads((follow/'native-phases.json').read_text())
assert a['status']=='failed' and r['status']=='technical_checks_complete_visual_review_pending'
assert f['phases'][0]['status']=='passed' and len(f['default_export_equality'])==16
assert all(p['status']=='passed' for p in r['phases'])
accepted={**a,'status':'technical_checks_complete_visual_review_pending','finished_at':r['finished_at'],'phases':a['phases'][:-1]+[p for p in r['phases'] if p['name']!='default-policy-rejection'],'runtime_inputs_sha256':r['runtime_inputs_sha256'],'initial_failed_review_sha256':sha(review/'review-pipeline.json'),'resumed_review_sha256':sha(review/'review-resume-pipeline.json'),'default_policy_rejection':r['phases'][0], 'default_export_equality':f['default_export_equality'],'scope':'Completed exact-source working-scene review with explicit verified-UV512lossless gate. Initial256cap rejection retained. Final art, device/performance and full goal remain open.'}
accepted.pop('error',None)
assert len(accepted['phases'])==31 and all(p['status']=='passed' for p in accepted['phases'])
accepted['source_native_pixel_indexes_sha256']={}
for name in ['lightmap-pixels.json','terminal-spill-pixels.json']:
 assert sha(src/'export'/name)==sha(review/'export'/name)
 records=json.loads((src/'export'/name).read_text());assert len(records)==(124 if name=='lightmap-pixels.json' else 7)
 for key,record in records.items():
  if name=='lightmap-pixels.json':image=src/'export/lightmaps'/key
  else:
   matching=[p for p in (src/'export/lightmaps').rglob('*.png') if sha(p)==record['png_sha256']];assert len(matching)==1;image=matching[0]
  assert sha(image)==record.get('sha256',record.get('png_sha256')) and record['finite']
 accepted['source_native_pixel_indexes_sha256'][name]=sha(src/'export'/name)
(review/'accepted-working-review.json').write_text(json.dumps(accepted,indent=2)+'\n')
work=Path(tempfile.mkdtemp(prefix='imperial-chart-adoption-',dir=repo/'.superpowers/sdd/2026-09-23-garden-completion'))
stage=work/'stage';stage.mkdir();(work/'backup').mkdir()
pairs=[('blender/authoring.blend',src/'blender/authoring.blend'),('blender/master.blend',src/'blender/master.blend'),('blender/sites',src/'blender/sites'),('export/sites',src/'export/sites'),('export/lightmaps',src/'export/lightmaps'),('export/garden-of-dreams.glb',src/'export/garden-of-dreams.glb'),('godot/assets/garden-of-dreams.glb',review/'godot/assets/garden-of-dreams.glb'),('godot/assets/garden-source.json',review/'godot/assets/garden-source.json'),('godot/lightmaps',review/'godot/lightmaps'),('godot/tests/moon-paint-atlas.json',review/'godot/tests/moon-paint-atlas.json'),('godot/tests/source-contract.json',review/'godot/tests/source-contract.json'),('godot/project.godot',review/'godot/project.godot'),('scripts/export_garden.py',exporter/'scripts/export_garden.py'),('scripts/imperial_tile_lightmap_uv.py',exporter/'scripts/imperial_tile_lightmap_uv.py')]
for n in ['manifest.json','site-wash-rig.json','candidate-libraries.json','full-lighting-refresh.json','full-refresh-inputs.json','lightmap-pixels.json','lightmaps-coverage.json','terminal-spill-pixels.json','imperial-tile-uv-layout.json']:
 path=(src/n) if n=='full-refresh-inputs.json' else src/'export'/n
 if n=='imperial-tile-uv-layout.json':path=exporter/'export'/n
 pairs.append(('export/'+n,path))
pairs.append(('export/site-source-audit.json',review/'export/site-source-audit.json'))
def snapshot(path):
 if not path.exists():return None
 if path.is_file():return {'file':sha(path)}
 return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file() and not p.name.endswith(('.blend1','.blend2'))}
plan={'status':'prepared_not_applied','source_glb_sha256':expected,'authoring_sha256':author,'source_root':str(src),'review_root':str(review),'review_report':'accepted-working-review.json','work':str(work),'items':[],'scope':'Incremental working-scene adoption of UV2-only imperial tile correction with complete fresh matching lighting, source libraries and reproducible default exporter. Both full native walks passed; final site art/material/joins/framing, phone/budgets/release/services and full goal acceptance remain open.'}
assert all(path.exists() for _,path in pairs), 'Every staged input must exist before copying'
for rel,path in pairs:
 out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True)
 if path.is_dir():shutil.copytree(path,out,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
 else:shutil.copy2(path,out)
 assert snapshot(out)==snapshot(path),rel
 plan['items'].append({'target':rel,'original':snapshot(repo/rel),'staged':snapshot(out)})
for p in sorted((review/'godot/assets').glob('*')):
 if p.suffix not in ('.png','.import'):continue
 target=repo/'godot/assets'/p.name
 if snapshot(p)!=snapshot(target):
  rel='godot/assets/'+p.name;out=stage/rel;shutil.copy2(p,out);plan['items'].append({'target':rel,'original':snapshot(target),'staged':snapshot(out)})
(work/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
Path('/tmp/garden-imperial-chart-adoption.json').write_text(json.dumps({'work':str(work),'plan':str(work/'plan.json')},indent=2)+'\n')
print('IMPERIAL_ADOPTION_STAGED',len(plan['items']),work)
