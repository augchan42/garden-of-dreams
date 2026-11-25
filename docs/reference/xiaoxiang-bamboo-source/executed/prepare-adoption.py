"""Install the reviewed bamboo source with recoverable backups and native replay."""
from pathlib import Path
import datetime, hashlib, json, os, re, shutil, subprocess, sys
repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/xiaoxiang-bamboo-source'
source=Path('/tmp/garden-xiaoxiang-bamboo-20261010')
review=source/'native-review-final'
adoption=work/'adoption';stage=adoption/'stage';backup=adoption/'backup'
old='ba40866e18f9ab3dcb0263855020099b7eedce70243c6a37e4d50c5f74c0e4f2'
new='faa8a7fe4a7a399899e84373c0550c8ff2f5f15ab0273109e8ea68f433b8fe0f'
author='0f93c42421a17b85b297fa0ff5447fad95cb7b98afeff183a2282ffe060492a4'
runtime='bde869171ad37d520ce34d10aa1ca825a327a6c6c6ce13e3dfafbeca6be5ba95'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def snapshot(p):
 if not p.exists():return None
 assert not p.is_symlink(),p
 if p.is_file():return {'file':sha(p)}
 return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file() and not f.name.endswith(('.blend1','.blend2'))}
def preflight():
 assert subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()=='codex/xiaoxiang-bamboo-source'
 assert sha(repo/'blender/authoring.blend')=='7eba169a1252dcad46aff5ad76906e4ce75ab009103fb98e586cc0c367897b8a'
 assert sha(repo/'export/garden-of-dreams.glb')==sha(repo/'godot/assets/garden-of-dreams.glb')==old
 assert sha(source/'blender/authoring.blend')==author and sha(source/'export/garden-of-dreams.glb')==new
 assert sha(repo/'godot/runtime/entry_route.gd')==sha(source/'godot/runtime/entry_route.gd')==runtime
 bake=load(source/'export/full-lighting-refresh.json');assert bake['status']=='source_complete' and len(bake['phases'])==6
 native=load(review/'pipeline.json');guards=load(source/'source-guard-review/pipeline.json')
 assert native['status']=='isolated_bamboo_technical_review_complete_direct_visual_review_pending'
 assert guards['status']=='all_updated_source_guard_checks_passed' and len(guards['phases'])==10 and len(native['phases'])==30
 for report in [bake,native,guards]:
  for phase in report['phases']:
   assert phase['status']=='passed' and phase['exit_code']==0
   if 'log_sha256' in phase:assert sha(phase['log'])==phase['log_sha256']
   try:os.kill(phase['pid'],0)
   except ProcessLookupError:pass
   else:raise AssertionError(('Owned process remains alive',phase['pid']))
 frozen=load(source/'full-lighting-inputs.json')['files'];assert len(frozen)==439
 for name,h in frozen.items():assert sha(source/name)==h,name
 assert len(native['source_engine_png_sha256'])==141
 for name,h in native['source_engine_png_sha256'].items():assert sha(source/'export/lightmaps'/name)==sha(source/'godot/lightmaps'/name)==h
 contract=load(review/'import-contract.json');assert contract['passed'] and [contract[k] for k in ['cameras_checked','colliders_checked','physics_rays_passed','marker_metadata_checked','render_meshes_snapshotted']]==[42,454,454,71,167]
 saved=load('/tmp/garden-xiaoxiang-bamboo-reexport-20261010/saved-source-verification.json');assert saved['status']=='saved_candidate_and_default_exports_verified' and len(saved['default_export_equality'])==16
 for n,h in saved['default_export_equality'].items():assert sha(source/'export'/n)==h
 assert load(source/'portable-saved-bamboo-contract.json')['status']=='saved_bamboo_contract_passed'
 assert load(source/'export-preservation.json')['status']=='bamboo_export_preservation_passed'
 assert load(source/'factory-reproduction.json')['status']=='all16candidate_flora_factory_semantics_equal'
 visual=load(review/'direct-original-visual-review.json');assert visual['status']=='bamboo_source_repair_accepted_final_site_art_open' and len(visual['directly_reviewed_originals_sha256'])==64
 for n,h in visual['directly_reviewed_originals_sha256'].items():assert sha(review/n)==h
 for mode in ['desktop','portrait']:
  tour=load(review/('tour-'+mode)/'report.json');assert tour['status']=='passed' and not tour['error'] and not tour['floor_failures']
  assert len(tour['visited_rooms'])==14 and len(tour['legs'])==len(tour['arrival_signals'])==len(tour['settled_arrivals'])==26
  assert tour['time_scale']==1 and tour['physics_ticks_per_second']==60 and tour['maximum_practicals']<=4 and tour['source_glb_sha256']==new
 return {'candidate_glb_sha256':new,'authoring_sha256':author,'runtime_sha256':runtime,'source_phases':6,'native_phases':40,'direct_originals':64,'frozen_files':439}
def prepare():
 verification=preflight();assert not adoption.exists();stage.mkdir(parents=True);backup.mkdir()
 names=['blender/authoring.blend','blender/master.blend','blender/kits/KIT_flora.blend','blender/sites','scripts/complete_flora_kit.py','export/garden-of-dreams.glb','export/sites','export/kits/flora','export/kits/KIT_flora.glb','export/kits/KIT_flora_LOD1.glb','export/lightmaps','export/manifest.json','export/candidate-libraries.json','export/site-wash-rig.json','export/ouxiang-tile-uv-layout.json','export/full-lighting-refresh.json','export/lightmap-pixels.json','export/lightmaps-coverage.json','export/terminal-spill-pixels.json','export/site-source-audit.json','godot/assets/garden-of-dreams.glb','godot/assets/garden-source.json','godot/assets/kits/flora','godot/lightmaps','godot/tests/source-contract.json']
 pairs=[(n,source/n) for n in names]
 pairs += [('export/full-lighting-inputs.json',source/'full-lighting-inputs.json')]
 pairs += [('scripts/'+n,work/n) for n in ['bamboo_source_contract.py','verify_saved_bamboo_sources.py']]
 pairs += [('godot/tests/test_xiaoxiang_bamboo_views.gd',source/'godot/tests/test_xiaoxiang_bamboo_views.gd')]
 guards=load(source/'source-guard-preparation.json')['changes'] if 'changes' in load(source/'source-guard-preparation.json') else load(source/'source-guard-review/pipeline.json')['source_guards']
 # Bind the new assembly; preserve all behavior and pixel assertions.
 guards=load(source/'source-guard-review/pipeline.json')['source_guards']
 for n,g in guards.items():
  assert sha(repo/n)==g['before_sha256'] and sha(source/n)==g['after_sha256']
  assert (repo/n).read_text().replace(old,new)==(source/n).read_text()
  pairs.append((n,source/n))
 plan={'status':'prepared_not_applied','verification':verification,'items':[],'source_guard_changes':guards}
 for n,p in pairs:
  assert p.exists(),n
  if snapshot(repo/n)==snapshot(p):continue
  out=stage/n;out.parent.mkdir(parents=True,exist_ok=True)
  if p.is_dir():shutil.copytree(p,out,ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
  else:shutil.copyfile(p,out)
  assert snapshot(out)==snapshot(p)
  plan['items'].append({'target':n,'original':snapshot(repo/n),'staged':snapshot(out)})
 assert len({i['target'] for i in plan['items']})==len(plan['items'])
 write(adoption/'plan.json',plan);print('BAMBOO_ADOPTION_PREPARED',len(plan['items']),flush=True)
def apply():
 preflight();plan=load(adoption/'plan.json');assert plan['status']=='prepared_not_applied' and not any(backup.rglob('*'))
 for i in plan['items']:assert snapshot(repo/i['target'])==i['original'] and snapshot(stage/i['target'])==i['staged']
 report={'status':'installing','checks':[],'source_glb_sha256':new,'authoring_sha256':author};write(adoption/'application.json',report);processed=[]
 def run(name,cmd,marker,timeout=300):
  log=adoption/(name+'.log');phase={'name':name,'command':cmd,'log':str(log),'status':'running'};report['checks'].append(phase);write(adoption/'application.json',report);print('BAMBOO_INSTALLED_START',name,flush=True)
  with log.open('w') as f:
   child=subprocess.Popen(cmd,cwd=repo,stdout=f,stderr=subprocess.STDOUT);phase['pid']=child.pid;write(adoption/'application.json',report)
   try:phase['exit_code']=child.wait(timeout=timeout)
   except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);phase['exit_code']=124
  text=log.read_text(errors='replace');okay=phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)|AssertionError:',text)
  phase.update(status='passed' if okay else 'failed',log_sha256=sha(log));write(adoption/'application.json',report);assert okay,(name,text[-3000:]);print('BAMBOO_INSTALLED_PASS',name,flush=True)
 try:
  for i in plan['items']:
   target=repo/i['target'];saved=backup/i['target'];saved.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():os.replace(target,saved)
   processed.append((i['target'],False));os.replace(stage/i['target'],target);processed[-1]=(i['target'],True)
  godot='/Applications/Godot.app/Contents/MacOS/Godot';head=[godot,'--headless','--path',str(repo/'godot')];native=[godot,'--path',str(repo/'godot'),'--windowed','--resolution','1410x600']
  run('import',head+['--editor','--import'],'Godot Engine')
  run('saved-source',['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','4','--python-exit-code','1','--python',str(repo/'scripts/verify_saved_bamboo_sources.py'),'--','--root',str(repo),'--output',str(adoption/'installed-saved-source.json')],'SAVED_BAMBOO_CONTRACT_PASS 27')
  run('source-contract',head+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(adoption/'installed-import-contract.json')],'IMPORT_SOURCE_CONTRACT_PASS')
  for name,script,marker,flags in [('full-lighting','test_full_scene_lighting.gd','FULL_SCENE_LIGHTING_PASS',['--','--imperial-lossless512','--ouxiang-lossless512']),('flora-kit','test_flora_kit.gd','FLORA_RUNTIME_PASS',[]),('flora-placement','test_flora_placements.gd','FLORA_PLACEMENT_RUNTIME_PASS',[]),('bamboo-route','test_bamboo_route.gd','BAMBOO_ROUTE_PASS',[]),('entry','test_entry_route.gd','ENTRY_ROUTE_PASS',[]),('first-demo','test_first_reading_demo.gd','FIRST_READING_DEMO_PASS',[]),('surface','test_surface_materials.gd','SURFACE_MATERIAL_PASS',[])]:run(name,head+['--script','res://tests/'+script,*flags],marker)
  for name,script,marker in [('wash','test_baked_backdrop_wash.gd','BAKED_BACKDROP_WASH_PASS'),('spill','test_terminal_spill.gd','TERMINAL_SPILL_PASS')]:
   for mode,flags in [('normal',[]),('demo',['--demo'])]:run(name+'-'+mode,head+['--script','res://tests/'+script,'--',*flags],marker)
  for mode,flags in [('normal',[]),('demo',['--demo'])]:run('palette-'+mode,native+['--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(adoption/('palette-'+mode+'.json')),*flags],'GARDEN_PALETTE_TRANSFER_PASS')
  run('public-views',native+['--script','res://tests/test_xiaoxiang_bamboo_views.gd','--','--output='+str(adoption/'public-views'),'--source='+new],'XIAOXIANG_BAMBOO_VIEWS_RESULT 24 originals; 0 failures')
  for mode,flags in [('desktop',[]),('portrait',['--mobile'])]:run('arrivals-'+mode,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--fixed-clock','--output-directory='+str(adoption/('arrivals-'+mode)),*flags],'ROUTE_RENDER_SAVED')
  for mode,flags in [('normal',[]),('demo',['--demo'])]:run('textures-'+mode,native+['--script','res://tests/audit_runtime_textures.gd','--','--output='+str(adoption/('textures-'+mode+'.json')),*flags],'RUNTIME_TEXTURE_INVENTORY_PASS')
  exact={}
  for folder in ['public-views','arrivals-desktop','arrivals-portrait']:
   for p in sorted((review/folder).glob('*.png')):
    assert sha(adoption/folder/p.name)==sha(p),p.name
    exact[folder+'/'+p.name]=sha(p)
  assert len(exact)==52
  for i in plan['items']:assert snapshot(repo/i['target'])==i['staged'],i['target']
  assert sha(repo/'godot/runtime/entry_route.gd')==runtime
  report.update(status='working_bamboo_source_adopted_installed_checks_passed',installed_originals_byte_exact=exact,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());write(adoption/'application.json',report)
  plan['status']='applied';write(adoption/'plan.json',plan);print('BAMBOO_WORKING_SOURCE_ADOPTION_PASS',flush=True)
 except BaseException as error:
  report.update(status='rolling_back',error=str(error));write(adoption/'application.json',report)
  for n,installed in reversed(processed):
   if installed and (repo/n).exists():os.replace(repo/n,stage/n)
   if (backup/n).exists():os.replace(backup/n,repo/n)
  report['status']='rolled_back';write(adoption/'application.json',report);raise
if __name__=='__main__':apply() if '--apply' in sys.argv else prepare()
