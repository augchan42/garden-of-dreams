"""Stage or atomically adopt the completed isolated Ziling source review."""
from pathlib import Path
import datetime,hashlib,json,os,re,shutil,struct,subprocess,sys

repo=Path('/Users/auchan/projects/garden-of-dreams')
w=repo/'.superpowers/sdd/2026-09-23-garden-completion/ziling-source-art'
src=w/'reeds-volume';review=w/'lit-native-review';work=w/'adoption';stage=work/'stage';backup=work/'backup'
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
expected='1380ceca14ee8bd79723c351a6084438eed4384416aee76a78222802550ca485'
author='0d3e84e3cb0aada4d7aafda8448f3ebb90bb39426eb18f24941a97c56977f400'
old='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'
oldauthor='19eb386d8e93007ebd8e4ae2d9ee59ec7daa07dcd8dbe3c3a88d4ec84b5e5a08'

def preflight():
 d=load(review/'review-pipeline-resume2.json')
 require(d['status']=='technical_review_complete_original_lit_visual_review_pending' and 'finished_at' in d,'Native review incomplete')
 require(d['source_glb_sha256']==sha(src/'export/garden-of-dreams.glb')==sha(review/'godot/assets/garden-of-dreams.glb')==expected,'Source mismatch')
 require(d['authoring_sha256']==sha(src/'blender/authoring.blend')==author,'Authoring mismatch')
 require(sha(repo/'export/garden-of-dreams.glb')==sha(repo/'godot/assets/garden-of-dreams.glb')==old and sha(repo/'blender/authoring.blend')==oldauthor,'Production source changed')
 phases=d['reused_checked_phases']+d['phases']
 require(len({x['name'] for x in phases})==len(phases),'Duplicate checks')
 for p in phases:require(p['status']=='passed' and p['exit_code']==0 and sha(p['log'])==p['log_sha256'],'Completed check changed '+p['name'])
 original=load(review/'review-pipeline-resume1.json')['phases'][-1]
 require(original['name']=='adjacent-architecture' and original['exit_code']==0 and sha(original['log'])==original['log_sha256'] and 'PORTRAIT_ARCHITECTURE_RESULT 15 captures; 0 failures' in Path(original['log']).read_text(),'Architecture evidence changed')
 bake=load(src/'export/full-lighting-refresh.json')
 require(bake['status']=='source_complete' and len(bake['phases'])==6 and all(p['status']=='passed' and p['exit_code']==0 for p in bake['phases']),'Source bake incomplete')
 require(bake['coverage']['expected_meshes']==bake['coverage']['baked_meshes']==124 and not bake['coverage']['missing'] and not bake['coverage']['unexpected'],'Source coverage incomplete')
 frozen=load(src/'full-lighting-inputs.json')['files'];require(len(frozen)==242,'Frozen input coverage changed')
 for rel,h in frozen.items():require(sha(src/rel)==h,'Frozen input changed '+rel)
 maps=load(review/'review-pipeline-resume1.json')['installed_source_png_sha256'];require(len(maps)==141,'Source map coverage')
 for rel,h in maps.items():require(sha(src/'export/lightmaps'/rel)==sha(review/'godot/lightmaps'/rel)==h,'Source map changed '+rel)
 contract=load(w/'candidate-contract-preservation.json');require(contract['status']=='unchanged_camera_collision_marker_contracts', 'Contract preservation incomplete')
 native=load(review/'native-import-contract.json');require(native['passed'] and native['cameras_checked']==42 and native['colliders_checked']==400 and native['marker_metadata_checked']==71 and native['physics_rays_passed']==400,'Native contract failed')
 saved=load(w/'saved-source-reproduction/saved-source-verification.json')
 require(saved['status']=='saved_candidate_and_default_exports_verified' and saved['authoring_sha256']==author and len(saved['default_export_equality'])==16,'Saved source reproduction incomplete')
 for rel,h in saved['default_export_equality'].items():require(sha(src/'export'/rel)==sha(w/'saved-source-reproduction/export'/rel)==h,'Saved-source export mismatch '+rel)
 repair=load(w/'flora-collider-preview-repair/repair-report.json');require(repair['status']=='saved_reopened_library_default_all16exports_byte_exact' and sha(review/'blender/kits/KIT_flora.blend')==repair['repaired_source_sha256'],'Flora repaired source changed')
 require(load(w/'flora-generator-reproduction/semantic-preservation.json')['status']=='all16regenerated_flora_semantics_equal','Fresh flora generation incomplete')
 require(load(w/'water-kit-parity/export-preservation.json')['status']=='controlled_water_kit_palette_passed','Water parity incomplete')
 fixture=load(review/'fixture-preparation.json');guard_names=set(fixture['source_guard_changes'])
 runtime={}
 for p in sorted((repo/'godot').rglob('*')):
  rel=p.relative_to(repo/'godot')
  if not p.is_file() or p.suffix not in ('.gd','.gdshader','.tscn','.godot') or any(x in ('.godot','lightmaps','captures','acceptance-captures') for x in rel.parts):continue
  candidate=review/'godot'/rel
  require(candidate.exists(),'Missing runtime '+str(rel))
  if rel.parent==Path('tests') and rel.name in guard_names:
   g=fixture['source_guard_changes'][rel.name];require(sha(p)==g['baseline_sha256'] and sha(candidate)==g['candidate_sha256'],'Guard changed '+str(rel))
   wanted=p.read_text().replace(old,expected)
   if rel.name=='test_ziling_framing.gd':wanted=wanted.replace('subjects.reeds.size()==10940','subjects.reeds.size()==48320')
   require(wanted==candidate.read_text(),'Unexpected test change '+str(rel))
  else:require(sha(p)==sha(candidate),'Runtime changed '+str(rel))
  runtime[str(rel)]=sha(candidate)
 walks={}
 for mode,size in [('desktop',[1410,600]),('portrait',[540,960])]:
  root=review/'review-captures-resume2'/('tour-'+mode);t=load(root/'report.json')
  require(t['status']=='passed' and not t['error'] and not t['floor_failures'] and t['source_glb_sha256']==expected,'Tour failed '+mode)
  require(len(t['visited_rooms'])==14 and len(t['legs'])==len(t['arrival_signals'])==len(t['settled_arrivals'])==26 and len(t['captures'])==len(list(root.glob('*.png')))==139,'Tour coverage '+mode)
  require(t['time_scale']==1 and t['maximum_practicals']<=4 and t['legs'][-1]['to']=='terminal_room','Tour constraints '+mode)
  for leg in t['legs']:require(leg['grounded_ray_samples']>0 and leg['supported_ray_samples']==leg['grounded_ray_samples'] and not leg['centre_ray_misses'],'Support failed '+mode)
  for c in t['captures']:require(sha(root/c['file'])==c['sha256'] and list(struct.unpack('>II',(root/c['file']).read_bytes()[16:24]))==size,'Tour original changed '+c['file'])
  for key,rel in [('route_sha256','runtime/entry_route.gd'),('test_sha256','tests/test_full_garden_traversal.gd'),('render_test_sha256','tests/render_full_garden_traversal.gd')]:require(t[key]==sha(repo/'godot'/rel),'Tour code changed '+rel)
  walks[mode]={'rooms':14,'legs':26,'supported_rays':sum(x['supported_ray_samples'] for x in t['legs']),'misses':0,'captures':139,'report_sha256':sha(root/'report.json')}
 visual=load(review/'direct-original-visual-review.json');require(visual['status']=='incremental_waterline_and_reed_source_accepted_final_site_art_open','Direct visual review pending')
 for rel,h in visual['directly_reviewed_originals_sha256'].items():require(sha(review/rel)==h,'Viewed original changed '+rel)
 return {'source_glb_sha256':expected,'authoring_sha256':author,'review_report_sha256':sha(review/'review-pipeline-resume2.json'),'phases':len(phases)+1,'walks':walks,'runtime_inputs_sha256':runtime,'source_png_sha256':maps,'visual_review_sha256':sha(review/'direct-original-visual-review.json')}

def prepare():
 verification=preflight();require(not work.exists(),'Adoption directory already exists');stage.mkdir(parents=True);backup.mkdir()
 pairs=[(rel,src/rel) for rel in ['blender/authoring.blend','blender/master.blend','blender/sites','export/sites','export/lightmaps','export/garden-of-dreams.glb']]
 pairs += [(rel,review/rel) for rel in ['blender/kits/KIT_flora.blend','blender/kits/KIT_water.blend','scripts/complete_flora_kit.py','export/kits/flora','export/kits/water','export/kits/KIT_water.glb','export/kits/KIT_water_LOD1.glb','godot/assets/garden-of-dreams.glb','godot/assets/garden-source.json','godot/assets/kits/flora','godot/assets/kits/water','godot/assets/kits/KIT_water.glb','godot/assets/kits/KIT_water_LOD1.glb','godot/lightmaps','godot/tests/source-contract.json','godot/tests/garden-palette-contract.json','godot/tests/portrait-architecture-contract.json','export/site-source-audit.json']]
 pairs += [('godot/tests/'+n,review/'godot/tests'/n) for n in load(review/'fixture-preparation.json')['source_guard_changes']]
 pairs += [('export/'+n,src/'export'/n) for n in ['manifest.json','candidate-libraries.json','full-lighting-refresh.json','lightmap-pixels.json','lightmaps-coverage.json','terminal-spill-pixels.json','site-wash-rig.json','ouxiang-tile-uv-layout.json','imperial-tile-uv-layout.json','pavilion-tile-uv-layout.json']]
 pairs += [('export/full-lighting-inputs.json',src/'full-lighting-inputs.json')]
 plan={'status':'prepared_not_applied','verification':verification,'items':[],'scope':'Incremental raised stream/lotus and neutral saved-source water; ten volumetric reed clumps with matching LOD kit/generator; fresh complete lighting. Cameras, collision, markers, runtime and final-site status preserved. Reversible backups; no phone or service completion claim.'}
 for rel,p in pairs:
  require(p.exists(),'Missing staged input '+rel)
  if snap(repo/rel)==snap(p):continue
  out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True)
  if p.is_dir():shutil.copytree(p,out,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
  else:shutil.copyfile(p,out)
  require(snap(out)==snap(p),'Staging mismatch '+rel)
  plan['items'].append({'target':rel,'original':snap(repo/rel),'staged':snap(out)})
 write(work/'plan.json',plan);shutil.copyfile(__file__,work/'executed-adoption.py');print('ZILING_ADOPTION_PREPARED',len(plan['items']),flush=True)

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
  completed=load(review/'review-pipeline-resume2.json')['reused_checked_phases']
  markers={'full-lighting':'FULL_SCENE_LIGHTING_PASS','wash-normal':'BAKED_BACKDROP_WASH_PASS','wash-demo':'BAKED_BACKDROP_WASH_PASS','spill-normal':'TERMINAL_SPILL_PASS','spill-demo':'TERMINAL_SPILL_PASS'}
  for p in completed:
   if p['name'] in markers:commands.append(('installed-'+p['name'],[arg.replace(str(review),str(repo)) for arg in p['command']],markers[p['name']]))
  commands += [('installed-surface-materials',head+['--script','res://tests/test_surface_materials.gd'],'SURFACE_MATERIAL_PASS')]
  for mode,args in [('normal',[]),('demo',['--demo'])]:commands.append(('installed-palette-'+mode,native+['--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(work/('installed-palette-'+mode+'.json'))]+args,'GARDEN_PALETTE_TRANSFER_PASS'))
  commands.append(('installed-ziling-framing',native+['--script','res://tests/test_ziling_framing.gd','--','--output='+str(work/'installed-ziling')],'ZILING_FRAMING_RESULT'))
  for name,cmd,marker in commands:
   print('ZILING_INSTALLED_CHECK_START',name,flush=True);log=work/(name+'.log')
   with log.open('w') as out:p=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=300)
   txt=log.read_text(errors='replace');require(p.returncode==0 and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)',txt),'Installed native failure '+name)
   if marker:require(marker in txt,'Installed completion marker '+name)
   report['checks'].append({'name':name,'command':cmd,'exit_code':p.returncode,'status':'passed','log':str(log),'log_sha256':sha(log)});write(work/'application.json',report);print('ZILING_INSTALLED_CHECK_PASS',name,flush=True)
  for x in plan['items']:require(snap(repo/x['target'])==x['staged'],'Installed bytes changed '+x['target'])
  report['status']='working_source_adopted_installed_checks_passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(work/'application.json',report);plan['status']='applied';write(work/'plan.json',plan);print('ZILING_WORKING_SOURCE_ADOPTION_PASS',flush=True)
 except BaseException as e:
  report['status']='rolling_back';report['error']=str(e);write(work/'application.json',report)
  for rel,installed in reversed(processed):
   if installed and (repo/rel).exists():os.replace(repo/rel,stage/rel)
   if (backup/rel).exists():os.replace(backup/rel,repo/rel)
  report['status']='rolled_back';write(work/'application.json',report);raise

if __name__=='__main__':
 if '--apply' in sys.argv:apply()
 else:prepare()
