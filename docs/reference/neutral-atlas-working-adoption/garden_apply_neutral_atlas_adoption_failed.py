from pathlib import Path
import json,hashlib,os,subprocess,re,sys,datetime
repo=Path('/Users/auchan/projects/garden-of-dreams')
pointer=json.load(open('/tmp/garden-neutral-atlas-adoption.json'));work=Path(pointer['work']);plan=json.load(open(pointer['plan']));stage=work/'stage';backup=work/'backup';review=Path(plan['review_root']);source=Path(plan['source_root'])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def snap(p):
 if not p.exists():return None
 if p.is_symlink():raise RuntimeError('Unexpected symlink '+str(p))
 if p.is_file():return {'file':sha(p)}
 return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file()}
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def write_report(): (work/'application.json').write_text(json.dumps(report,indent=2)+'\n')
report={'status':'preflight','scope':plan['scope'],'source_glb_sha256':plan['source_glb_sha256'],'authoring_sha256':plan['authoring_sha256'],'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[]}
require(plan['status']=='prepared_not_applied','Plan already used')
require(not any(backup.rglob('*')),'Backup must be empty')
j=json.load(open(review/'accepted-working-review.json'));b=json.load(open(source/'export/full-lighting-refresh.json'))
require(j['status']=='technical_checks_complete_visual_review_pending' and 'finished_at' in j,'Review not terminal')
require(sha(review/'review-pipeline.json')==j['review_report_sha256'],'Completed review changed')
verified=Path(plan['verified_root']);v=json.load(open(verified/'verification.json'))
require(sha(verified/'verification.json')==j['native_default_verification_sha256'],'Native verification changed')
require(v['status']=='saved_source_and_default_export_passed_visual_adoption_pending','Native export verification incomplete')
require(sha(repo/'scripts/export_garden.py')==v['canonical_inputs']['export_garden.py'],'Exporter changed')
require(sha(repo/'scripts/ouxiang_tile_lightmap_uv.py')==v['canonical_inputs']['ouxiang_tile_lightmap_uv.py'],'UV allocator changed')
require(sha(verified/'saved-source-verification.json')==v['native_report_sha256'],'Native path ownership report changed')
require(len(j['default_export_equality'])==16,'Sixteen default GLBs required')
for rel,digest in j['default_export_equality'].items():require(sha(verified/'export'/rel)==sha(source/'export'/rel)==digest,'Default export mismatch '+rel)
require(len(j['phases'])==42 and all(x['status']=='passed' for x in j['phases']),'42 review phases required')
negative={'reject-camera','reject-collider','reject-marker','default-policy-rejection','ouxiang-policy-rejection','reject-palette-plain','reject-palette-atlas'}
require({p['name'] for p in j['phases'] if p['exit_code']==1}==negative,'Expected negative review gates changed')
for name,digest in j['source_phase_log_sha256'].items():
 phase=next(x for x in b['phases'] if x['name']==name);require(sha(phase['log'])==digest,'Source bake log changed '+name)
for rel,digest in j['selected_originals_sha256'].items():require(sha(review/rel)==digest,'Reviewed original changed '+rel)
require(sha(review/'native-window-capture-dimensions.json')==j['native_window_dimensions_sha256'],'Native dimensions changed')
import struct
for row in json.load(open(review/'native-window-capture-dimensions.json'))['captures']:
 p=review/row['path'];data=p.read_bytes();require(sha(p)==row['sha256'] and list(struct.unpack('>II',data[16:24]))==row['actual_png_dimensions'],'Actual capture dimensions mismatch')
require(sha(repo/'blender/authoring.blend')=='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c','Production authoring changed')
for phase in j['phases']:
 require(phase['exit_code']==(1 if phase['name'] in negative else 0),'Wrong review exit '+phase['name'])
 require(sha(phase['log'])==phase['log_sha256'],'Review log changed '+phase['name'])
require(b['status']=='source_complete' and len(b['phases'])==6 and all(x['status']=='passed' and x['exit_code']==0 for x in b['phases']),'Source bake incomplete')
require(j['source_glb_sha256']==b['source_glb_sha256']==sha(source/'export/garden-of-dreams.glb')==sha(review/'godot/assets/garden-of-dreams.glb')==plan['source_glb_sha256'],'GLB mismatch')
require(sha(source/'blender/authoring.blend')==plan['authoring_sha256'],'Blender mismatch')
require(b['coverage']['expected_meshes']==b['coverage']['baked_meshes']==124 and not b['coverage']['missing'] and not b['coverage']['unexpected'],'Coverage incomplete')
for k,v in j['runtime_inputs_sha256'].items():
 path=stage/'godot'/k if (stage/'godot'/k).exists() and k=='project.godot' else repo/'godot'/k
 require(sha(path)==v,'Runtime changed '+k)
runtime_inventory={str(p.relative_to(repo/'godot')) for p in (repo/'godot').rglob('*') if p.is_file() and p.suffix in ('.gd','.gdshader','.tscn','.godot') and not any(part in ('.godot','lightmaps','acceptance-captures','captures') for part in p.relative_to(repo/'godot').parts)}
require(set(j['runtime_inputs_sha256'])==runtime_inventory,'Runtime inventory scope changed')
require(len(j['installed_source_png_sha256'])==141,'All source PNGs required')
for k,v in j['installed_source_png_sha256'].items():
 require(sha(source/'export/lightmaps'/k)==sha(review/'godot/lightmaps'/k)==v,'Source map mismatch '+k)
for k,v in j['source_native_pixel_indexes_sha256'].items():require(sha(source/'export'/k)==sha(review/'export'/k)==v,'Precision index mismatch '+k)
for k,v in j['catalogs'].items():require(sha(review/'godot/lightmaps'/k)==v['sha256'],'Catalog mismatch '+k)
report['walks']={}
for mode in ['desktop','portrait']:
 folder=review/f'review-captures/tour-{mode}';t=json.load(open(folder/'report.json'))
 require(t['status']=='passed' and not t['error'] and not t['floor_failures'],'Walk failed')
 require(t['source_glb_sha256']==plan['source_glb_sha256'],'Walk source mismatch')
 require(len(t['visited_rooms'])==14 and len(t['legs'])==len(t['arrival_signals'])==len(t['settled_arrivals'])==26,'Walk coverage')
 require(len(t['captures'])==len(list(folder.glob('*.png')))==139,'Capture coverage')
 require(all(x['grounded_ray_samples']>0 and x['grounded_ray_samples']==x['supported_ray_samples'] and x['physics_frames']>=x['grounded_ray_samples'] for x in t['legs']),'Walk floor sample mismatch')
 require(all(not x['centre_ray_misses'] for x in t['legs']) and t['maximum_practicals']<=4 and t['time_scale']==1,'Walk constraints')
 require(t['legs'][-1]['to']=='terminal_room','Return missing')
 for c in t['captures']:require(sha(folder/c['file'])==c['sha256'],'Capture mismatch')
 for key,path in [('route_sha256','runtime/entry_route.gd'),('test_sha256','tests/test_full_garden_traversal.gd'),('render_test_sha256','tests/render_full_garden_traversal.gd')]:require(sha(repo/'godot'/path)==t[key],'Walk code changed')
 report['walks'][mode]={'rooms':14,'legs':26,'supported_rays':sum(x['supported_ray_samples'] for x in t['legs']),'misses':0,'settled_arrivals':26,'captures':139}
m=json.load(open(review/'review-captures/moon-scene/report.json'))
require(m['source_glb_sha256']==plan['source_glb_sha256'],'Moon source mismatch')
for name in ['baseline','no-grade']:
 c=m['cases'][name];require(c['channel_clip_fraction']==0 and c['display_luminance_p95']>c['display_luminance_p05']+.1 and c['interior_samples']==3005,'Moon clipping/contrast')
 require(sha(review/f'review-captures/moon-scene/{name}.png')==c['image_sha256'],'Moon pixels changed')
require('entry_route.tscn' in (stage/'godot/project.godot' if (stage/'godot/project.godot').exists() else repo/'godot/project.godot').read_text().split('run/main_scene=')[1].splitlines()[0],'Default route missing')
for item in plan['items']:
 rel=item['target'];require(snap(repo/rel)==item['original'],'Current bytes changed '+rel);require(snap(stage/rel)==item['staged'],'Staged bytes changed '+rel)
for name,digest in v['canonical_inputs'].items():require(sha(repo/'scripts'/name)==digest,'Canonical source input changed '+name)
for name,reason in [('reject-palette-plain','Active baked base color differs'),('reject-palette-atlas','Atlas color swatch differs from reviewed palette')]:
 phase=next(p for p in j['phases'] if p['name']==name);require(reason in Path(phase['log']).read_text(),'Wrong palette rejection '+name)
for mode in ['normal','demo']:
 palette=json.load(open(review/('garden-palette-transfer-'+mode+'.json')))
 require(palette['source_glb_sha256']==plan['source_glb_sha256'] and palette['status']=='passed','Palette source mismatch '+mode)
 require(sha(stage/'godot/tests/garden-palette-contract.json')==palette['contract_sha256'],'Palette contract changed')
report['preflight']='passed';write_report();print('ADOPTION_PREFLIGHT_PASS',len(plan['items']),flush=True)
if '--preflight' in sys.argv:sys.exit(0)
processed=[]
try:
 for item in plan['items']:
  rel=item['target'];target=repo/rel;saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True)
  require(snap(target)==item['original'],'Concurrent target edit '+rel)
  if target.exists():os.replace(target,saved)
  processed.append((rel,False))
  os.replace(stage/rel,target);processed[-1]=(rel,True)
 for item in plan['items']:require(snap(repo/item['target'])==item['staged'],'Installed mismatch '+item['target'])
 report['status']='installed_checks_running';write_report();print('MATCHED_SCENE_INSTALLED',flush=True)
 commands=[('production-import',['/Applications/Godot.app/Contents/MacOS/Godot','--headless','--path',str(repo/'godot'),'--editor','--import'],None),('production-source-contract',['/Applications/Godot.app/Contents/MacOS/Godot','--headless','--path',str(repo/'godot'),'--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(work/'production-import.json')],'IMPORT_SOURCE_CONTRACT_PASS')]
 markers={'full-lighting':'FULL_SCENE_LIGHTING_PASS','wash-normal':'BAKED_BACKDROP_WASH_PASS','wash-demo':'BAKED_BACKDROP_WASH_PASS','spill-normal':'TERMINAL_SPILL_PASS','spill-demo':'TERMINAL_SPILL_PASS'}
 for phase in j['phases']:
  if phase['name'] in markers:commands.append((phase['name'],[arg.replace(str(review),str(repo)) for arg in phase['command']],markers[phase['name']]))
 commands.append(('surface-materials',['/Applications/Godot.app/Contents/MacOS/Godot','--headless','--path',str(repo/'godot'),'--script','res://tests/test_surface_materials.gd'],'SURFACE_MATERIAL_PASS'))
 for mode,args in [('normal',[]),('demo',['--demo'])]:
  commands.append(('palette-'+mode,['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(repo/'godot'),'--windowed','--resolution','390x844','--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(work/('production-palette-'+mode+'.json')),*args],'GARDEN_PALETTE_TRANSFER_PASS'))
 for name,cmd,marker in commands:
  log=work/(name+'.log')
  with log.open('w') as out:result=subprocess.run(cmd,cwd=repo/'godot',stdout=out,stderr=subprocess.STDOUT)
  txt=log.read_text();require(result.returncode==0,'Native check exit '+name)
  require(not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:|Assertion failed)',txt,re.M),'Native error '+name)
  if marker:require(marker in txt,'Missing marker '+name)
  report['checks'].append({'name':name,'command':cmd,'exit_code':result.returncode,'log':str(log),'log_sha256':sha(log),'status':'passed'});write_report();print('PRODUCTION_CHECK_PASS',name,flush=True)
 require(sha(repo/'export/garden-of-dreams.glb')==sha(repo/'godot/assets/garden-of-dreams.glb')==plan['source_glb_sha256'],'Installed source changed')
 report['installed_snapshots']={item['target']:snap(repo/item['target']) for item in plan['items']}
 report['status']='working_scene_adopted_checks_passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();write_report()
 plan['status']='applied';Path(pointer['plan']).write_text(json.dumps(plan,indent=2)+'\n');print('WORKING_SCENE_ADOPTION_PASS',flush=True)
except BaseException as error:
 report['error']=str(error);report['status']='rolling_back';write_report()
 for rel,installed in reversed(processed):
  if installed and (repo/rel).exists():os.replace(repo/rel,stage/rel)
  if (backup/rel).exists():os.replace(backup/rel,repo/rel)
 report['status']='rolled_back';write_report();raise
