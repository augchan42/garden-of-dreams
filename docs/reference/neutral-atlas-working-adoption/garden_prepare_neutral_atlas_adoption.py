"""Stage the verified Ouxiang working scene; retain full source and review evidence."""
from pathlib import Path
import hashlib,json,shutil,tempfile,struct
repo=Path('/Users/auchan/projects/garden-of-dreams')
def pointer(n):return Path(json.load(open('/tmp/garden-'+n+'.json'))['folder']).resolve()
src=pointer('neutral-atlas-full-source');review=pointer('neutral-atlas-full-review');verified=pointer('neutral-atlas-source-verified')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected='59de1ca29bc9d02235fc29a18b78c7b2c3dfde893a27f3b8fb318af6e042ddc8';author='3a3ae2536f17cf8f19b8e5c1c811b080fe05c25615297fa20cb24019c0709621'
a=json.load(open(review/'review-pipeline.json'));v=json.load(open(verified/'verification.json'));b=json.load(open(src/'export/full-lighting-refresh.json'))
assert a['status']=='technical_checks_complete_visual_review_pending' and len(a['phases'])==42
assert v['status']=='saved_source_and_default_export_passed_visual_adoption_pending'
assert sha(review/'review-pipeline.json')==v['completed_review_report_sha256']
assert len(v['default_export_equality'])==16
assert sha(repo/'scripts/export_garden.py')==v['canonical_inputs']['export_garden.py']
assert sha(repo/'scripts/ouxiang_tile_lightmap_uv.py')==v['canonical_inputs']['ouxiang_tile_lightmap_uv.py']
for rel,digest in v['default_export_equality'].items():assert sha(verified/'export'/rel)==sha(src/'export'/rel)==digest
assert sha(verified/'saved-source-verification.json')==v['native_report_sha256']
accepted={**a,'review_report_sha256':sha(review/'review-pipeline.json'),'native_default_verification_sha256':sha(verified/'verification.json'),'default_export_equality':v['default_export_equality'],'verified_root':str(verified),'source_native_pixel_indexes_sha256':{},'source_phase_log_sha256':{p['name']:sha(p['log']) for p in b['phases']},'scope':'Incremental exact-source paving and neutral plain/architectural palette adoption with matching fresh lighting. Six source phases, 42 engine phases and exact default reexport pass; selected original views reviewed. Final art/framing, standalone kit palette synchronization, devices, services and full goal remain open.'}
for name,count in [('lightmap-pixels.json',124),('terminal-spill-pixels.json',7)]:
 assert sha(src/'export'/name)==sha(review/'export'/name)
 records=json.load(open(src/'export'/name));assert len(records)==count
 for key,record in records.items():
  digest=record.get('sha256',record.get('png_sha256'))
  if name=='lightmap-pixels.json':image=src/'export/lightmaps'/key
  else:
   candidates=[p for p in (src/'export/lightmaps').rglob('*.png') if sha(p)==digest];assert len(candidates)==1;image=candidates[0]
  assert sha(image)==digest and record['finite']
 accepted['source_native_pixel_indexes_sha256'][name]=sha(src/'export'/name)
dims=json.load(open(review/'native-window-capture-dimensions.json'))
assert len(dims['captures'])==4
for row in dims['captures']:
 p=review/row['path'];data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and list(struct.unpack('>II',data[16:24]))==row['actual_png_dimensions'] and sha(p)==row['sha256']
accepted['native_window_dimensions_sha256']=sha(review/'native-window-capture-dimensions.json')
accepted['selected_originals_reviewed']=['review-captures/arrivals-desktop/route-ouxiang.png','review-captures/arrivals-portrait/route-mobile-ouxiang.png','review-captures/arrivals-desktop/route-pavilion.png','review-captures/arrivals-portrait/route-mobile-pavilion.png','review-captures/arrivals-desktop/route-courtyard.png','review-captures/arrivals-portrait/route-mobile-cell.png','review-captures/moon-scene/baseline.png']
accepted['selected_originals_sha256']={p:sha(review/p) for p in accepted['selected_originals_reviewed']}
accepted['visual_notes']='Working color revision: slate pavilion/corridor/plain roofs, brown timber and neutral plaster; repaired paving visible and CRT green retained. Selected originals reviewed, not final all-site art acceptance. Stage exposure, other portrait framing and organic rock/foliage remain open.'
accepted['stationary_native_memory']={}
for mode in ['normal','demo']:
 m=json.load(open(review/('runtime-texture-inventory-'+mode+'.json')))
 assert m['source_glb_sha256']==expected and m['status']=='passed'
 peak=max(row['texture_memory_bytes'] for row in m['views'].values())
 accepted['stationary_native_memory'][mode]={'inventory_sha256':sha(review/('runtime-texture-inventory-'+mode+'.json')),'final_texture_memory_bytes':m['texture_memory_bytes'],'maximum_arrival_texture_memory_bytes':peak,'bound_image_data_bytes':m['bound_image_data_bytes'],'scope':'M2 Max gl_compatibility stationary arrival allocation; not phone, sustained, frame timing or release acceptance.'}
(review/'accepted-working-review.json').write_text(json.dumps(accepted,indent=2)+'\n')
work=Path(tempfile.mkdtemp(prefix='neutral-atlas-adoption-',dir=repo/'.superpowers/sdd/2026-09-23-garden-completion'));stage=work/'stage';stage.mkdir();(work/'backup').mkdir()
pairs=[('blender/authoring.blend',src/'blender/authoring.blend'),('textures/atlases/pavilion',src/'textures/atlases/pavilion'),('textures/atlases/wall',src/'textures/atlases/wall'),('godot/tests/garden-palette-contract.json',review/'godot/tests/garden-palette-contract.json'),('blender/master.blend',src/'blender/master.blend'),('blender/sites',src/'blender/sites'),('export/sites',src/'export/sites'),('export/lightmaps',src/'export/lightmaps'),('export/garden-of-dreams.glb',src/'export/garden-of-dreams.glb'),('godot/assets/garden-of-dreams.glb',review/'godot/assets/garden-of-dreams.glb'),('godot/assets/garden-source.json',review/'godot/assets/garden-source.json'),('godot/lightmaps',review/'godot/lightmaps'),('godot/tests/moon-paint-atlas.json',review/'godot/tests/moon-paint-atlas.json'),('godot/tests/source-contract.json',review/'godot/tests/source-contract.json'),('godot/project.godot',review/'godot/project.godot')]
for n in ['manifest.json','site-wash-rig.json','candidate-libraries.json','full-lighting-refresh.json','full-refresh-inputs.json','lightmap-pixels.json','lightmaps-coverage.json','terminal-spill-pixels.json','imperial-tile-uv-layout.json','ouxiang-tile-uv-layout.json']:
 pairs.append(('export/'+n,src/n if n=='full-refresh-inputs.json' else src/'export'/n))
pairs.append(('export/site-source-audit.json',review/'export/site-source-audit.json'))
def snapshot(path):
 if not path.exists():return None
 assert not path.is_symlink(),str(path)
 if path.is_file():return {'file':sha(path)}
 return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file() and not p.name.endswith(('.blend1','.blend2'))}
plan={'status':'prepared_not_applied','source_glb_sha256':expected,'authoring_sha256':author,'source_root':str(src),'review_root':str(review),'verified_root':str(verified),'review_report':'accepted-working-review.json','work':str(work),'items':[],'scope':accepted['scope']}
assert sha(repo/'blender/authoring.blend')=='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c'
assert sha(src/'blender/authoring.blend')==author
assert all(path.exists() for _,path in pairs)
for rel,path in pairs:
 if snapshot(path)==snapshot(repo/rel):continue
 out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True)
 if path.is_dir():shutil.copytree(path,out,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
 else:shutil.copy2(path,out)
 assert snapshot(out)==snapshot(path),rel
 plan['items'].append({'target':rel,'original':snapshot(repo/rel),'staged':snapshot(out)})
for p in sorted((review/'godot/assets').glob('*')):
 if p.suffix not in ('.png','.import'):continue
 rel='godot/assets/'+p.name
 if snapshot(p)!=snapshot(repo/rel):
  out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);plan['items'].append({'target':rel,'original':snapshot(repo/rel),'staged':snapshot(out)})
(work/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');Path('/tmp/garden-neutral-atlas-adoption.json').write_text(json.dumps({'work':str(work),'plan':str(work/'plan.json')},indent=2)+'\n')
print('NEUTRAL_ATLAS_ADOPTION_STAGED',len(plan['items']),work)
