"""Stage or atomically adopt the completed isolated bank and lotus source review."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,struct,subprocess,sys

repo=Path('/Users/auchan/projects/garden-of-dreams')
w=repo/'.superpowers/sdd/2026-09-23-garden-completion/water-edge-source'
src=w/'closed-leaf-candidate';review=w/'lit-native-review';work=w/'adoption';stage=work/'stage';backup=work/'backup'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def snap(p):
 if not p.exists():return None
 require(not p.is_symlink(),'Unexpected symlink '+str(p))
 if p.is_file():return {'file':sha(p)}
 return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file() and not f.name.endswith(('.blend1','.blend2'))}
expected='7a9fc523bc1517941cc248c040877b86f9cd00a11654c6c31e40f3acc089632f'
author='074ab2014d9122e207783d9e7c7992f9dfc9197a6f380a2d6f5e8c0c05e31978'
old='1380ceca14ee8bd79723c351a6084438eed4384416aee76a78222802550ca485'
oldauthor='0d3e84e3cb0aada4d7aafda8448f3ebb90bb39426eb18f24941a97c56977f400'

def preflight():
 require(subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()=='codex/water-edge-bank-lotus','Wrong adoption branch')
 require(sha(repo/'export/garden-of-dreams.glb')==sha(repo/'godot/assets/garden-of-dreams.glb')==old and sha(repo/'blender/authoring.blend')==oldauthor,'Production source changed')
 d=load(review/'review-pipeline-resume1.json');v=load(w/'completed-review-verification.json')
 require(v['status']=='completed_water_edge_source_review_verified' and v['native_review_phases']==36 and v['source_phases']==6,'Final verification incomplete')
 require(d['status']=='technical_review_complete_original_lit_visual_review_pending' and 'finished_at' in d,'Native review incomplete')
 require(d['source_glb_sha256']==sha(src/'export/garden-of-dreams.glb')==sha(review/'godot/assets/garden-of-dreams.glb')==expected,'Source mismatch')
 require(d['authoring_sha256']==sha(src/'blender/authoring.blend')==author,'Authoring mismatch')
 phases=d['reused_checked_phases']+d['phases']
 require(len(phases)==len({x['name'] for x in phases})==36,'Review coverage')
 for p in phases:require(p['status']=='passed' and p['exit_code']==0 and sha(p['log'])==p['log_sha256'],'Completed check changed '+p['name'])
 require(sha(review/'review-pipeline.json')==d['prior_failed_report_sha256'],'Initial failed runner evidence changed')
 frozen=load(src/'full-lighting-inputs.json')['files'];require(len(frozen)==257,'Frozen input coverage')
 for rel,h in frozen.items():require(sha(src/rel)==h,'Frozen input changed '+rel)
 maps=d['installed_source_png_sha256'];require(len(maps)==141,'Source map coverage')
 for rel,h in maps.items():require(sha(src/'export/lightmaps'/rel)==sha(review/'godot/lightmaps'/rel)==h,'Source map changed '+rel)
 milestone=load(w/'completed-source-milestone-verification.json')
 require(sha(src/'export/full-lighting-refresh.json')==milestone['bake_report_sha256'],'Bake report changed')
 for p,h in milestone['finished_source_log_sha256'].items():require(sha(p)==h,'Bake log changed')
 native=load(review/'native-import-contract.json');require(native['passed'] and native['cameras_checked']==42 and native['colliders_checked']==native['physics_rays_passed']==454 and native['marker_metadata_checked']==71 and native['render_meshes_snapshotted']==167,'Native contract failed')
 saved=load(w/'saved-source-reproduction/saved-source-verification.json');require(saved['status']=='saved_candidate_and_default_exports_verified' and saved['authoring_sha256']==author and len(saved['default_export_equality'])==16,'Saved source reproduction incomplete')
 for rel,h in saved['default_export_equality'].items():require(sha(src/'export'/rel)==sha(w/'saved-source-reproduction/export'/rel)==h,'Saved-source export mismatch '+rel)
 kit=load(w/'water-kit-preservation.json');require(kit['status']=='ten_unchanged_water_exports_byte_exact' and sum(x['unchanged'] for x in kit['exports'])==10,'Kit preservation')
 for row in kit['exports']:
  require(sha(src/'export/kits/water'/row['file'])==sha(review/'godot/assets/kits/water'/row['file'])==row['sha256'],'Module changed')
  if row['unchanged']:require(sha(repo/'export/kits/water'/row['file'])==row['sha256'],'Unchanged module changed')
 factory=load(w/'water-generator-reproduction/semantic-preservation.json');require(factory['status']=='all12regenerated_water_semantics_equal' and len(factory['rows'])==12,'Factory reproduction')
 for row in factory['rows']:require(sha(src/'export/kits/water'/row['file'])==row['saved_sha256'] and sha(w/'water-generator-reproduction/export/kits/water'/row['file'])==row['factory_sha256'],'Factory bytes changed')
 require(sha(review/'blender/kits/KIT_water.blend')==load(w/'saved-water-kit.json')['candidate_kit_sha256'],'Editable water kit mismatch')
 for n in ['complete_water_kit.py','lotus_geometry.py','lotus_blender.py']:require(sha(review/'scripts'/n)==sha(w/'source-code-candidates'/n),'Generator mismatch '+n)
 fixture=load(review/'fixture-preparation.json');guard_names=set(fixture['source_guard_changes']);runtime={}
 for p in sorted((repo/'godot').rglob('*')):
  rel=p.relative_to(repo/'godot')
  if not p.is_file() or p.suffix not in ('.gd','.gdshader','.tscn','.godot') or any(x in ('.godot','lightmaps','captures','acceptance-captures') for x in rel.parts):continue
  candidate=review/'godot'/rel;require(candidate.exists(),'Missing runtime '+str(rel))
  if rel.parent==Path('tests') and rel.name in guard_names:
   g=fixture['source_guard_changes'][rel.name];require(sha(p)==g['baseline_sha256'] and sha(candidate)==g['candidate_sha256'],'Guard changed '+str(rel));require(p.read_text().replace(old,expected)==candidate.read_text(),'Unexpected test change '+str(rel))
  else:require(sha(p)==sha(candidate),'Runtime changed '+str(rel))
  runtime[str(rel)]=sha(candidate)
 for mode,size in [('desktop',[1410,600]),('portrait',[540,960])]:
  root=review/'review-captures-resume1'/('tour-'+mode);t=load(root/'report.json')
  require(t['status']=='passed' and not t['error'] and not t['floor_failures'] and t['source_glb_sha256']==expected,'Tour failed '+mode)
  require(len(t['visited_rooms'])==14 and len(t['legs'])==len(t['arrival_signals'])==len(t['settled_arrivals'])==26 and len(t['captures'])==len(list(root.glob('*.png')))==139,'Tour coverage')
  require(t['time_scale']==1 and t['maximum_practicals']<=4 and t['physics_ticks_per_second']==60,'Tour limits')
  for leg in t['legs']:require(leg['grounded_ray_samples']>0 and leg['supported_ray_samples']==leg['grounded_ray_samples'] and not leg['centre_ray_misses'],'Ground support failed')
  for c in t['captures']:require(sha(root/c['file'])==c['sha256'] and list(struct.unpack('>II',(root/c['file']).read_bytes()[16:24]))==size,'Tour original changed '+c['file'])
  require(sha(root/'report.json')==v['walks'][mode]['report_sha256'],'Tour report changed')
 visual=load(review/'direct-original-visual-review.json');require(visual['status']=='incremental_bank_and_closed_lotus_source_accepted_final_site_art_open' and visual['directly_reviewed_original_count']==42 and sha(review/'direct-original-visual-review.json')==v['visual_review_sha256'],'Direct visual review pending')
 for rel,h in visual['directly_reviewed_originals_sha256'].items():require(sha(review/rel)==h,'Viewed original changed '+rel)
 require(subprocess.run(['ps','-p','62359,63518'],stdout=subprocess.DEVNULL).returncode!=0,'Managed native review still running')
 return {'source_glb_sha256':expected,'authoring_sha256':author,'review_report_sha256':sha(review/'review-pipeline-resume1.json'),'phases':36,'walks':v['walks'],'runtime_inputs_sha256':runtime,'source_png_sha256':maps,'visual_review_sha256':v['visual_review_sha256']}

def prepare():
 verification=preflight();require(not work.exists(),'Adoption directory already exists');stage.mkdir(parents=True);backup.mkdir()
 pairs=[(rel,src/rel) for rel in ['blender/authoring.blend','blender/master.blend','blender/sites','export/sites','export/lightmaps','export/garden-of-dreams.glb']]
 pairs += [(rel,review/rel) for rel in ['blender/kits/KIT_flora.blend','blender/kits/KIT_water.blend','scripts/complete_flora_kit.py','scripts/complete_water_kit.py','scripts/lotus_geometry.py','scripts/lotus_blender.py','export/kits/flora','export/kits/water','export/kits/KIT_water.glb','export/kits/KIT_water_LOD1.glb','godot/assets/garden-of-dreams.glb','godot/assets/garden-source.json','godot/assets/kits/flora','godot/assets/kits/water','godot/lightmaps','godot/tests/source-contract.json','godot/tests/garden-palette-contract.json','godot/tests/portrait-architecture-contract.json','export/site-source-audit.json']]
 pairs += [('godot/tests/'+n,review/'godot/tests'/n) for n in load(review/'fixture-preparation.json')['source_guard_changes']]
 pairs += [('export/'+n,src/'export'/n) for n in ['manifest.json','candidate-libraries.json','full-lighting-refresh.json','lightmap-pixels.json','lightmaps-coverage.json','terminal-spill-pixels.json','site-wash-rig.json','ouxiang-tile-uv-layout.json','imperial-tile-uv-layout.json','pavilion-tile-uv-layout.json']]
 pairs += [('export/full-lighting-inputs.json',src/'full-lighting-inputs.json')]
 plan={'status':'prepared_not_applied','verification':verification,'items':[],'scope':'54 stock bank modules with54 new colliders; raised circular closed lotus pads with matching864/360LOD kit/generator; complete fresh lighting. All42 cameras,400preexisting colliders,71markers and runtime preserved. Final-site art remains open. Reversible backups; no phone or service completion claim.'}
 for rel,p in pairs:
  require(p.exists(),'Missing staged input '+rel)
  if snap(repo/rel)==snap(p):continue
  out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True)
  if p.is_dir():shutil.copytree(p,out,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
  else:shutil.copyfile(p,out)
  require(snap(out)==snap(p),'Staging mismatch '+rel)
  plan['items'].append({'target':rel,'original':snap(repo/rel),'staged':snap(out)})
 write(work/'plan.json',plan);shutil.copyfile(__file__,work/'executed-adoption.py');print('WATER_EDGE_ADOPTION_PREPARED',len(plan['items']),flush=True)

def apply():
 preflight();plan=load(work/'plan.json');require(plan['status']=='prepared_not_applied' and not any(backup.rglob('*')),'Adoption already used')
 for x in plan['items']:require(snap(repo/x['target'])==x['original'] and snap(stage/x['target'])==x['staged'],'Staged/current bytes changed '+x['target'])
 report={'status':'installing','source_glb_sha256':expected,'authoring_sha256':author,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[]};write(work/'application.json',report);processed=[]
 try:
  for x in plan['items']:
   rel=x['target'];target=repo/rel;saved=backup/rel;saved.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():os.replace(target,saved)
   processed.append((rel,False));os.replace(stage/rel,target);processed[-1]=(rel,True)
  godot='/Applications/Godot.app/Contents/MacOS/Godot';head=[godot,'--headless','--path',str(repo/'godot')];native=[godot,'--path',str(repo/'godot'),'--windowed','--resolution','390x844']
  commands=[('installed-import',head+['--editor','--import'],None),('installed-source-contract',head+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(work/'installed-import-contract.json')],'IMPORT_SOURCE_CONTRACT_PASS'),('installed-flora',head+['--script','res://tests/test_flora_kit.gd'],'FLORA_RUNTIME_PASS'),('installed-water',head+['--script','res://tests/test_water_kit.gd'],'WATER_KIT_PASS')]
  completed=load(review/'review-pipeline-resume1.json')['reused_checked_phases']
  markers={'full-lighting':'FULL_SCENE_LIGHTING_PASS','wash-normal':'BAKED_BACKDROP_WASH_PASS','wash-demo':'BAKED_BACKDROP_WASH_PASS','spill-normal':'TERMINAL_SPILL_PASS','spill-demo':'TERMINAL_SPILL_PASS'}
  for p in completed:
   if p['name'] in markers:commands.append(('installed-'+p['name'],[arg.replace(str(review),str(repo)) for arg in p['command']],markers[p['name']]))
  commands += [('installed-surface-materials',head+['--script','res://tests/test_surface_materials.gd'],'SURFACE_MATERIAL_PASS')]
  for mode,args in [('normal',[]),('demo',['--demo'])]:commands.append(('installed-palette-'+mode,native+['--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(work/('installed-palette-'+mode+'.json'))]+args,'GARDEN_PALETTE_TRANSFER_PASS'))
  commands.append(('installed-ziling-framing',[godot,'--path',str(repo/'godot'),'--windowed','--resolution','1410x600']+['--script','res://tests/test_ziling_framing.gd','--','--output='+str(work/'installed-ziling')],'ZILING_FRAMING_RESULT'))
  commands.append(('installed-western-route',head+['--script','res://tests/test_western_route.gd'],'WESTERN_ROUTE_PASS'))
  commands.append(('installed-water-edge',[godot,'--path',str(repo/'godot'),'--windowed','--resolution','1410x600','--script',str(w/'garden_compare_water_edge_lit.gd'),'--','--output='+str(work/'installed-water-edge'),'--candidate'],'WATER_EDGE_COMPARISON_RESULT'))
  for name,cmd,marker in commands:
   print('WATER_EDGE_INSTALLED_CHECK_START',name,flush=True);log=work/(name+'.log')
   with log.open('w') as out:p=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=300)
   txt=log.read_text(errors='replace');require(p.returncode==0 and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)',txt),'Installed native failure '+name)
   if marker:require(marker in txt,'Installed completion marker '+name)
   report['checks'].append({'name':name,'command':cmd,'exit_code':p.returncode,'status':'passed','log':str(log),'log_sha256':sha(log)});write(work/'application.json',report);print('WATER_EDGE_INSTALLED_CHECK_PASS',name,flush=True)
  for x in plan['items']:require(snap(repo/x['target'])==x['staged'],'Installed bytes changed '+x['target'])
  report['status']='working_source_adopted_installed_checks_passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(work/'application.json',report);plan['status']='applied';write(work/'plan.json',plan);print('WATER_EDGE_WORKING_SOURCE_ADOPTION_PASS',flush=True)
 except BaseException as e:
  report['status']='rolling_back';report['error']=str(e);write(work/'application.json',report)
  for rel,installed in reversed(processed):
   if installed and (repo/rel).exists():os.replace(repo/rel,stage/rel)
   if (backup/rel).exists():os.replace(backup/rel,repo/rel)
  report['status']='rolled_back';write(work/'application.json',report);raise

if __name__=='__main__':
 if '--apply' in sys.argv:apply()
 else:prepare()
