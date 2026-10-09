"""One sequential isolated review after the existing complete source pipeline exits."""
from pathlib import Path
import json,hashlib,os,sys,time,shutil,subprocess,re,datetime,struct
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root']);s=w/'reeds-volume';root=Path(json.loads(Path('/tmp/garden-ziling-lit-review.json').read_text())['root']);g=root/'godot';logroot=root/'review-logs-resume1';assert not logroot.exists();logroot.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();expected=sha(s/'export/garden-of-dreams.glb');author=sha(s/'blender/authoring.blend');report={'status':'waiting_for_existing_source_pipeline','source_glb_sha256':expected,'authoring_sha256':author,'root':str(root),'orchestrator_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':[],'scope':'All work is isolated. The current source bake and preparation parent must both finish and exit before any native review job. No production adoption, visual acceptance, phone budgets or services completion.'}
def save():(root/'review-pipeline-resume1.json').write_text(json.dumps(report,indent=2)+'\n')
def alive(pid):
 try:os.kill(pid,0);return True
 except ProcessLookupError:return False
def run(name,cmd,marker,timeout=180):
 assert sha(s/'export/garden-of-dreams.glb')==expected and sha(s/'blender/authoring.blend')==author
 log=logroot/(name+'.log');phase={'name':name,'status':'running','command':cmd,'log':str(log)};report['phases'].append(phase);save();print('ZILING_REVIEW_START',name,flush=True)
 with log.open('w') as f:
  proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);phase['pid']=proc.pid;save()
  try:phase['exit_code']=proc.wait(timeout=timeout)
  except subprocess.TimeoutExpired:proc.terminate();proc.wait();phase['exit_code']=124
 txt=log.read_text(errors='replace');phase['log_sha256']=sha(log);okay=phase['exit_code']==0 and marker in txt and not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)',txt);phase['status']='passed' if okay else 'failed';save()
 if not okay:raise RuntimeError((name,phase['exit_code'],txt[-4000:]))
 print('ZILING_REVIEW_PASS',name,flush=True)
try:
 save();shutil.copyfile(__file__,root/'executed-review-pipeline-resume1.py');deadline=time.monotonic()+10800
 while True:
  bake=json.loads((s/'export/full-lighting-refresh.json').read_text());prep=json.loads((s/'lighting-preparation.json').read_text());assert bake['source_glb_sha256']==expected
  if bake['status']=='failed' or prep['status']=='failed':raise RuntimeError(('Existing source pipeline failed',bake['status'],prep['status']))
  if bake['status']=='source_complete' and prep['status']=='complete_source_lighting_passed_native_review_pending' and not alive(bake['orchestrator_pid']) and not alive(prep['orchestrator_pid']):break
  assert alive(prep['orchestrator_pid']) or prep['status']=='complete_source_lighting_passed_native_review_pending','Preparation process exited without completion'
  assert alive(bake['orchestrator_pid']) or bake['status']=='source_complete','Source baker exited without completion'
  if time.monotonic()>deadline:raise RuntimeError('Observation deadline reached; do not restart the existing bake')
  time.sleep(5)
 assert [p['name'] for p in bake['phases']]==['ordinary','backdrop-wash','terminal-spill','terminal-spill-pixels','native-pixels','coverage'] and all(p['status']=='passed' and p['exit_code']==0 for p in bake['phases'])
 frozen=json.loads((s/'full-lighting-inputs.json').read_text())['files']
 for name,h in frozen.items():assert sha(s/name)==h,name
 report.update(status='native_review_running',source_bake_report=bake,source_preparation_report=prep,frozen_inputs_verified=len(frozen));save()
 blender=['/Applications/Blender.app/Contents/MacOS/Blender','--background','--threads','8','--python-exit-code','1','--python'];py=sys.executable
 water=w/'water-kit-parity'
 previous=json.loads((root/'review-pipeline.json').read_text());assert previous['status']=='failed' and previous['phases'][-1]['name']=='saved-flora-default-reexports'
 assert previous['source_glb_sha256']==expected and previous['authoring_sha256']==author
 for p in previous['phases'][:2]:assert p['status']=='passed' and p['exit_code']==0 and sha(p['log'])==p['log_sha256']
 water_source=json.loads((water/'source-review.json').read_text());assert sha(water/'KIT_water.blend')==water_source['candidate_saved_source_sha256']
 assert json.loads((water/'export-preservation.json').read_text())['status']=='controlled_water_kit_palette_passed'
 repair=json.loads((w/'flora-collider-preview-repair/repair-report.json').read_text());assert repair['status']=='saved_reopened_library_default_all16exports_byte_exact' and sha(w/'flora-collider-preview-repair/KIT_flora.blend')==repair['repaired_source_sha256']
 for name,h in repair['exports'].items():assert sha(w/'flora-collider-preview-repair/default-reexports'/name)==h and sha(s/'export/kits/flora'/name)==h
 report['reused_checked_phases']=previous['phases'][:2];report['previous_failed_review_sha256']=sha(root/'review-pipeline.json');report['flora_preview_repair']=repair;save()
 run('saved-flora-default-reexports',blender+[str(w/'source-code-candidates/reexport_repaired_saved_flora.py')],'SAVED_FLORA_REEXPORT_PASS_16',240)
 run('fresh-flora-generator',blender+[str(w/'flora-generator-reproduction/scripts/complete_flora_kit.py')],'FLORA_KIT_COMPLETE',240)
 run('fresh-flora-generator-semantics',[py,str(w/'source-code-candidates/verify_flora_generator.py')],'REGENERATED_FLORA_SEMANTICS_PASS_16')
 # Stage only checked kit assets; runtime atlas remains byte-identical to production.
 shutil.copyfile(w/'flora-collider-preview-repair/KIT_flora.blend',root/'blender/kits/KIT_flora.blend')
 shutil.copyfile(water/'KIT_water.blend',root/'blender/kits/KIT_water.blend');shutil.copytree(r/'export/kits/water',root/'export/kits/water')
 for p in (water/'candidate').glob('*.glb'):
  shutil.copyfile(p,root/'export/kits/water'/p.name);shutil.copyfile(p,g/'assets/kits/water'/p.name)
 for suffix in ['', '_LOD1']:
  name='KIT_water'+suffix+'.glb';module='KIT_water_wood_bridge'+suffix+'.glb';assert (r/'export/kits'/name).read_bytes()==(r/'export/kits/water'/module).read_bytes();shutil.copyfile(water/'candidate'/module,root/'export/kits'/name);shutil.copyfile(water/'candidate'/module,g/'assets/kits'/name)
 shutil.copyfile(w/'source-code-candidates/complete_flora_kit.py',root/'scripts/complete_flora_kit.py')
 shutil.copytree(s/'export/lightmaps',root/'export/lightmaps')
 for name in ['full-lighting-refresh.json','lightmaps-coverage.json','lightmap-pixels.json','terminal-spill-pixels.json']:shutil.copyfile(s/'export'/name,root/'export'/name)
 assert sha(g/'assets/kits/flora/flora-basecolor.png')==sha(r/'godot/assets/kits/flora/flora-basecolor.png')
 for label,args,marker in [('coverage',['verify_lightmaps.py','--current','--require-all'],'BAKE_COVERAGE 124 / 124'),('sync-full',['sync_full_lightmaps.py'],'FULL_LIGHTMAP_CATALOG_PASS'),('sync-demo',['sync_lightmaps.py','--demo'],'Synced'),('sync-priority2',['sync_priority2_lightmaps.py'],'PRIORITY2_LIGHTMAPS_PASS'),('sync-wash',['sync_backdrop_wash.py'],'BACKDROP_WASH_CATALOG_PASS'),('sync-spill',['sync_terminal_spill.py'],'TERMINAL_SPILL_CATALOG_PASS')]:run(label,[py,str(root/'scripts'/args[0]),*args[1:]],marker)
 pngs={}
 for name,count in {'full-index.json':124,'demo-index.json':33,'priority2-index.json':29,'backdrop-wash-index.json':6,'terminal-spill-index.json':7}.items():
  data=json.loads((g/'lightmaps'/name).read_text());assert len(data)==count and {x['source_glb_sha256'] for x in data.values()}=={expected}
  for record in data.values():
   for side in record.get('sides',{'front':record}).values():
    texture=side['texture'];assert sha(root/'export/lightmaps'/texture)==sha(g/'lightmaps'/texture);pngs[texture]=sha(g/'lightmaps'/texture)
 assert len(pngs)==141;report['installed_source_png_sha256']=pngs;save()
 godot='/Applications/Godot.app/Contents/MacOS/Godot';head=[godot,'--headless','--path',str(g)];native=[godot,'--path',str(g),'--windowed','--resolution','1410x600']
 run('cold-import',head+['--editor','--import'],'Godot Engine',300)
 run('configure-lightmap-caps',[py,str(root/'scripts/configure_lightmap_imports.py'),'--size-limit','256','--imperial-lossless512','--ouxiang-lossless512'],'Configured')
 run('configured-import',head+['--editor','--import'],'Godot Engine',300)
 run('native-source-contract',head+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(root/'native-import-contract.json')],'IMPORT_SOURCE_CONTRACT_PASS')
 run('native-flora-kit',head+['--script','res://tests/test_flora_kit.gd'],'FLORA_RUNTIME_PASS')
 run('native-water-kit',head+['--script','res://tests/test_water_kit.gd'],'WATER_KIT_PASS',180)
 run('full-lighting',head+['--script','res://tests/test_full_scene_lighting.gd','--','--imperial-lossless512','--ouxiang-lossless512'],'FULL_SCENE_LIGHTING_PASS')
 for label,script,marker in [('wash','test_baked_backdrop_wash.gd','BAKED_BACKDROP_WASH_PASS'),('spill','test_terminal_spill.gd','TERMINAL_SPILL_PASS')]:
  for mode,args in [('normal',[]),('demo',['--demo'])]:run(label+'-'+mode,head+['--script','res://tests/'+script,'--',*args],marker)
 reexport=w/'saved-source-reproduction';assert not reexport.exists()
 run('saved-source-default-reexports',['/Applications/Blender.app/Contents/MacOS/Blender','--background',str(root/'blender/authoring.blend'),'--threads','8','--python-exit-code','1','--python',str(root/'scripts/verify_saved_garden_candidate.py'),'--','--source-root',str(root),'--output-root',str(reexport)],'SAVED_GARDEN_CANDIDATE_PASS',300)
 run('site-source-audit',blender+[str(root/'scripts/audit_site_sources.py')],'SITE_SOURCE_AUDIT_RECORDED',240)
 site=json.loads((root/'export/site-source-audit.json').read_text());assert len(site['sites'])==14
 for name,row in site['sites'].items():assert not row['structural_differences_from_authoring'] and row['signs_match_authoring'] and not row['missing_current_bakes'] and not row['triggers_without_room_id'],name
 cap=root/'review-captures';cap.mkdir()
 for mode,args in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
  output=cap/('ziling-'+mode);run('ziling-'+mode,native+['--script','res://tests/test_ziling_framing.gd','--','--output='+str(output)]+args,'ZILING_FRAMING_RESULT 10 originals; 0 failures',160);d=json.loads((output/'report.json').read_text());assert len(d['rows'])==10 and not d['errors']
  for row in d['rows']:
   p=Path(row['capture']);assert sha(p)==row['sha256'] and list(struct.unpack('>II',p.read_bytes()[16:24]))==row['pixels']
 for label,script,marker in [('ouxiang','test_oux_portrait_framing.gd','OUXIANG_FRAMING_PASS'),('architecture','test_portrait_architecture.gd','PORTRAIT_ARCHITECTURE_PASS'),('hengwu','test_hengwu_detail_framing.gd','HENGWU_DETAIL_FRAMING_RESULT'),('tubi','test_tubi_framing.gd','TUBI_FRAMING_RESULT'),('qiushuang','test_qiushuang_framing.gd','QIUSHUANG_FRAMING_RESULT'),('pond','test_pond_view.gd','POND_VIEW_PASS')]:
  run('adjacent-'+label,native+['--script','res://tests/'+script,'--','--output='+str(cap/label)],marker,160)
 for mode,args in [('normal',[]),('demo',['--demo'])]:
  run('texture-memory-'+mode,native+['--script','res://tests/audit_runtime_textures.gd','--','--output='+str(root/('texture-memory-'+mode+'.json'))]+args,'RUNTIME_TEXTURE_INVENTORY_PASS',160)
 for mode,args in [('desktop',[]),('portrait',['--mobile'])]:
  output=cap/('arrivals-'+mode);run('arrivals-'+mode,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--fixed-clock','--output-directory='+str(output)]+args,'ROUTE_RENDER_SAVED',160);d=json.loads((output/('route-'+mode+'-report.json')).read_text());assert d['source_glb_sha256']==expected and len(d['captures'])==14
 for mode,args in [('desktop',[]),('portrait',['--portrait'])]:
  output=cap/('tour-'+mode);output.mkdir();run('full-tour-'+mode,native+['--script','res://tests/render_full_garden_traversal.gd','--','--capture-directory='+str(output),'--output='+str(output/'report.json')]+args,'FULL_GARDEN_TRAVERSAL',900);d=json.loads((output/'report.json').read_text());assert d['status']=='passed' and d['source_glb_sha256']==expected
 for name,h in frozen.items():assert sha(s/name)==h,name
 assert sha(g/'runtime/entry_route.gd')==sha(r/'godot/runtime/entry_route.gd')
 report['status']='technical_review_complete_original_lit_visual_review_pending';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('ZILING_FULL_TECHNICAL_REVIEW_COMPLETE',root,flush=True)
except BaseException as e:report['status']='failed';report['error']=str(e);save();raise
