"""Validate the completed review and stage the matching source with rollback metadata."""
from pathlib import Path
import hashlib,json,shutil,tempfile,struct,datetime
repo=Path('/Users/auchan/projects/garden-of-dreams')
src=Path(json.load(open('/tmp/garden-hengwu-compact-rock.json'))['root']).resolve()
review=Path(json.load(open('/tmp/garden-hengwu-full-review.json'))['folder']).resolve()
verified=Path('/private/var/folders/gf/s_g2zvzj3jxbylz3ylbc7k4c0000gn/T/garden-hengwu-native-reexport-tdjuzc76')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def write(p,j):Path(p).write_text(json.dumps(j,indent=2)+'\n')
expected='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'
author='19eb386d8e93007ebd8e4ae2d9ee59ec7daa07dcd8dbe3c3a88d4ec84b5e5a08'
old_source='59de1ca29bc9d02235fc29a18b78c7b2c3dfde893a27f3b8fb318af6e042ddc8'
old_author='3a3ae2536f17cf8f19b8e5c1c811b080fe05c25615297fa20cb24019c0709621'
first=load(review/'review-pipeline.json');resume=load(review/'review-resume-pipeline.json');bake=load(src/'export/full-lighting-refresh.json');native=load(verified/'saved-source-verification.json')
assert first['status']=='failed' and resume['status']=='technical_checks_complete_visual_review_pending' and 'finished_at' in resume
assert len(resume['reused_completed_checks'])==28 and len(resume['phases'])==19
phases=resume['reused_completed_checks']+resume['phases']
assert len({p['name'] for p in phases})==47
negative={'reject-camera','reject-collider','reject-marker','default-policy-rejection','ouxiang-policy-rejection','reject-palette-plain','reject-palette-atlas'}
assert {p['name'] for p in phases if p['exit_code']==1}==negative
for p in phases:
 assert p['status']=='passed' and p['exit_code']==(1 if p['name'] in negative else 0)
 assert sha(p['log'])==p['log_sha256'],p['name']
for name,reason in [('reject-palette-plain','Active baked base color differs'),('reject-palette-atlas','Atlas color swatch differs from reviewed palette')]:
 assert reason in Path(next(p for p in phases if p['name']==name)['log']).read_text()
assert bake['status']=='source_complete' and len(bake['phases'])==6
for p in bake['phases']:assert p['status']=='passed' and p['exit_code']==0
assert bake['coverage']['expected_meshes']==bake['coverage']['baked_meshes']==124 and not bake['coverage']['missing'] and not bake['coverage']['unexpected']
assert sha(repo/'blender/authoring.blend')==old_author
assert sha(repo/'export/garden-of-dreams.glb')==sha(repo/'godot/assets/garden-of-dreams.glb')==old_source
assert sha(src/'blender/authoring.blend')==native['authoring_sha256']==author
assert sha(src/'export/garden-of-dreams.glb')==sha(review/'godot/assets/garden-of-dreams.glb')==resume['source_glb_sha256']==bake['source_glb_sha256']==expected
assert native['status']=='saved_candidate_and_default_exports_verified' and len(native['default_export_equality'])==16
canonical={}
for name in ['export_garden.py','ouxiang_tile_lightmap_uv.py','verify_saved_garden_candidate.py']:
 assert sha(repo/'scripts'/name)==sha(review/'scripts'/name)
 canonical[name]=sha(repo/'scripts'/name)
for rel,digest in native['default_export_equality'].items():assert sha(verified/'export'/rel)==sha(src/'export'/rel)==digest
v={'status':'saved_source_and_default_export_passed_visual_adoption_pending','canonical_inputs':canonical,'native_report_sha256':sha(verified/'saved-source-verification.json'),'default_export_equality':native['default_export_equality'],'completed_review_report_sha256':sha(review/'review-resume-pipeline.json')}
write(verified/'verification.json',v)
runtime={**first['runtime_inputs_sha256'],**resume['updated_test_inputs_sha256']}
extra='tests/render_hengwu_lit_candidate.gd'
inventory={str(p.relative_to(repo/'godot')) for p in (repo/'godot').rglob('*') if p.is_file() and p.suffix in ('.gd','.gdshader','.tscn','.godot') and not any(x in ('.godot','lightmaps','acceptance-captures','captures') for x in p.relative_to(repo/'godot').parts)}
assert set(runtime)==inventory|{extra}
for rel,digest in runtime.items():
 assert sha(review/'godot'/rel)==digest,rel
 if rel!=extra:assert sha(repo/'godot'/rel)==digest,rel
assert sha(repo/'godot/runtime/entry_route.gd')=='db32d9c058a732c330d9df910b22b961f755045c5904c47e8fde68fd3c056138'
for rel,digest in first['installed_source_png_sha256'].items():assert sha(src/'export/lightmaps'/rel)==sha(review/'godot/lightmaps'/rel)==digest
assert len(first['installed_source_png_sha256'])==141
for rel,row in first['catalogs'].items():assert sha(review/'godot/lightmaps'/rel)==row['sha256']
accepted={**first,'status':resume['status'],'finished_at':resume['finished_at'],'phases':phases,'runtime_inputs_sha256':runtime,'review_report_sha256':sha(review/'review-resume-pipeline.json'),'first_review_report_sha256':sha(review/'review-pipeline.json'),'native_default_verification_sha256':sha(verified/'verification.json'),'default_export_equality':native['default_export_equality'],'verified_root':str(verified),'source_phase_log_sha256':{p['name']:sha(p['log']) for p in bake['phases']},'source_native_pixel_indexes_sha256':{},'walks':{},'capture_directory':'review-captures-completed-camera-waits','review_only_runtime_inputs':[extra]}
accepted.pop('error',None)
accepted['scope']='Incremental compact Hengwu stone and correctly anchored collider with matching fresh lighting. Six source phases, 47 completed review checks, seven intentional rejection controls and sixteen exact default GLB reexports. Final art/framing, devices, services and full goal remain open.'
accepted['visual_notes']='All nine completed Hengwu action originals and four settled walk originals inspected. Smaller stone exposes more courtyard. Narrow book/rock framing, roof crop, foreground wall cap and facade lighting remain open; this is not final site art acceptance.'
for name,count in [('lightmap-pixels.json',124),('terminal-spill-pixels.json',7)]:
 assert sha(src/'export'/name)==sha(review/'export'/name)
 records=load(src/'export'/name);assert len(records)==count
 for key,row in records.items():
  digest=row.get('sha256',row.get('png_sha256'));assert row['finite']
  matches=[p for p in (src/'export/lightmaps').rglob('*.png') if sha(p)==digest] if name=='terminal-spill-pixels.json' else [src/'export/lightmaps'/key]
  assert len(matches)==1 and sha(matches[0])==digest
 accepted['source_native_pixel_indexes_sha256'][name]=sha(src/'export'/name)
def png(p,digest,size):
 data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and sha(p)==digest and list(struct.unpack('>II',data[16:24]))==list(size),str(p)
selected=[]
for folder,count in [('hengwu-lit-actions',9),('portrait-architecture',15)]:
 report=load(review/accepted['capture_directory']/folder/'report.json');assert len(report['rows'])==count
 if folder=='portrait-architecture':assert not report['errors'] and report['status']=='portrait_architecture_behavior_passed'
 for row in report['rows']:
  assert not row['camera_transition_running'];p=Path(row['capture']);png(p,row['sha256'],row.get('actual_pixels',row.get('capture_pixels')))
  if folder=='hengwu-lit-actions':
   assert row['site_bakes_enabled'] and row['lightmap_source_sha256']==expected
   poses={'arrival':[-17.5,2.6,-10.5],'rocks':[-15.6,1.6,-10.6],'read':[-18,1.8,-13.4]}
   assert max(abs(x-y) for x,y in zip(row['camera_position'],poses[row['action']]))<.002
   selected.append(str(p.relative_to(review)))
for mode,size in [('desktop',[1410,600]),('portrait',[540,960])]:
 folder=review/accepted['capture_directory']/('tour-'+mode);t=load(folder/'report.json')
 assert t['status']=='passed' and not t['error'] and not t['floor_failures'] and t['source_glb_sha256']==expected
 assert len(t['visited_rooms'])==14 and len(t['legs'])==len(t['arrival_signals'])==len(t['settled_arrivals'])==26
 assert len(t['captures'])==len(list(folder.glob('*.png')))==139
 assert t['maximum_practicals']<=4 and t['time_scale']==1 and t['physics_ticks_per_second']==60 and t['legs'][-1]['to']=='terminal_room'
 for leg in t['legs']:assert leg['grounded_ray_samples']>0 and leg['grounded_ray_samples']==leg['supported_ray_samples'] and not leg['centre_ray_misses'] and leg['physics_frames']>=leg['grounded_ray_samples']
 for c in t['captures']:
  png(folder/c['file'],c['sha256'],size)
  if c['room']=='hengwu_yuan' and c['phase']=='settled':selected.append(str((folder/c['file']).relative_to(review)))
 for key,path in [('route_sha256','runtime/entry_route.gd'),('test_sha256','tests/test_full_garden_traversal.gd'),('render_test_sha256','tests/render_full_garden_traversal.gd')]:assert sha(repo/'godot'/path)==t[key]
 accepted['walks'][mode]={'rooms':14,'legs':26,'supported_rays':sum(x['supported_ray_samples'] for x in t['legs']),'misses':0,'settled_arrivals':26,'captures':139,'report_sha256':sha(folder/'report.json')}
accepted['selected_originals_reviewed']=selected;accepted['selected_originals_sha256']={rel:sha(review/rel) for rel in selected}
accepted['stationary_native_memory']={}
for mode in ['normal','demo']:
 m=load(review/('runtime-texture-inventory-'+mode+'.json'));assert m['status']=='passed' and m['source_glb_sha256']==expected
 accepted['stationary_native_memory'][mode]={'inventory_sha256':sha(review/('runtime-texture-inventory-'+mode+'.json')),'maximum_arrival_texture_memory_bytes':max(x['texture_memory_bytes'] for x in m['views'].values()),'final_texture_memory_bytes':m['texture_memory_bytes'],'scope':'M2 Max stationary allocation only; not phone, sustained or frame timing acceptance.'}
for mode in ['normal','demo']:
 p=load(review/('garden-palette-transfer-'+mode+'.json'));assert p['status']=='passed' and p['source_glb_sha256']==expected and p['contract_sha256']==sha(review/'godot/tests/garden-palette-contract.json')
write(review/'accepted-working-review.json',accepted)
def snapshot(path):
 if not path.exists():return None
 assert not path.is_symlink(),str(path)
 if path.is_file():return {'file':sha(path)}
 return {str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file() and not p.name.endswith(('.blend1','.blend2'))}
work=Path(tempfile.mkdtemp(prefix='hengwu-adoption-',dir=repo/'.superpowers/sdd/2026-09-23-garden-completion'));stage=work/'stage';stage.mkdir();(work/'backup').mkdir()
pairs=[(rel,src/rel) for rel in ['blender/authoring.blend','blender/master.blend','blender/sites','export/sites','export/lightmaps','export/garden-of-dreams.glb']]
pairs += [(rel,review/rel) for rel in ['godot/assets/garden-of-dreams.glb','godot/assets/garden-source.json','godot/lightmaps','godot/tests/source-contract.json','godot/tests/garden-palette-contract.json','godot/tests/portrait-architecture-contract.json','godot/tests/moon-paint-atlas.json','godot/project.godot','export/site-source-audit.json']]
pairs += [('export/'+name,src/'export'/name) for name in ['manifest.json','site-wash-rig.json','candidate-libraries.json','full-lighting-refresh.json','lightmap-pixels.json','lightmaps-coverage.json','terminal-spill-pixels.json','imperial-tile-uv-layout.json','ouxiang-tile-uv-layout.json','pavilion-tile-uv-layout.json']]
pairs += [('export/full-lighting-inputs.json',src/'full-lighting-inputs.json')]
plan={'status':'prepared_not_applied','source_glb_sha256':expected,'authoring_sha256':author,'previous_source_glb_sha256':old_source,'previous_authoring_sha256':old_author,'source_root':str(src),'review_root':str(review),'verified_root':str(verified),'work':str(work),'items':[],'scope':accepted['scope'],'accepted_review_sha256':sha(review/'accepted-working-review.json')}
for rel,path in pairs:
 assert path.exists(),str(path)
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
write(work/'plan.json',plan);write('/tmp/garden-hengwu-adoption.json',{'work':str(work),'plan':str(work/'plan.json')})
print('HENGWU_ADOPTION_STAGED',len(plan['items']),work,flush=True)
