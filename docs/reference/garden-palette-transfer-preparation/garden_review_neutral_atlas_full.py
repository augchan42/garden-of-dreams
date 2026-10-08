"""Prepare an isolated candidate and review it after the full source bake passes.

This never modifies production or restarts the source baker. Every native job
runs sequentially, after all six source phases and the source orchestrator exit.
"""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone

REPO=Path('/Users/auchan/projects/garden-of-dreams')
SOURCE=Path(json.loads(Path('/tmp/garden-neutral-atlas-full-source.json').read_text())['folder'])
EXPECTED=hashlib.sha256((SOURCE/'export/garden-of-dreams.glb').read_bytes()).hexdigest()
AUTHOR=hashlib.sha256((SOURCE/'blender/authoring.blend').read_bytes()).hexdigest()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE/'export/garden-of-dreams.glb')==EXPECTED
assert sha(SOURCE/'blender/authoring.blend')==AUTHOR
ROOT=Path(tempfile.mkdtemp(prefix='garden-neutral-atlas-full-review-'))
GD=ROOT/'godot'
LOG=ROOT/'review-logs';LOG.mkdir()
REPORT=ROOT/'review-pipeline.json'
report={'status':'preparing','source_root':str(SOURCE),'folder':str(ROOT),'source_glb_sha256':EXPECTED,
 'authoring_blend_sha256':AUTHOR,'orchestrator_pid':os.getpid(),'started_at':datetime.now(timezone.utc).isoformat(),
 'scope':'Separate exact-source review fixture; no production adoption. Pixel inspection remains a human/agent review after technical checks. Native jobs run sequentially only after the completed source baker exits.', 'phases':[]}
def save():REPORT.write_text(json.dumps(report,indent=2)+'\n')
def emit(message):print(message,flush=True)
def alive(pid):
 try:os.kill(pid,0);return True
 except ProcessLookupError:return False

def run(label,command,expected_marker=None,expected_exit=0):
 assert sha(ROOT/'export/garden-of-dreams.glb')==EXPECTED
 phase={'name':label,'command':command,'status':'running','log':str(LOG/(label+'.log'))};report['phases'].append(phase);save();emit('REVIEW_PHASE_START '+label)
 with open(phase['log'],'w') as log:
  child=subprocess.Popen(command,cwd=GD,stdout=log,stderr=subprocess.STDOUT)
  phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 text=Path(phase['log']).read_text(errors='replace')
 phase['log_sha256']=sha(phase['log'])
 assert phase['exit_code']==expected_exit,(label,phase['exit_code'],text[-3000:])
 if expected_exit==0:
  assert not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed)',text),(label,text[-4000:])
 if expected_marker:assert expected_marker in text,(label,'missing success marker',text[-3000:])
 phase['status']='passed';save();emit('REVIEW_PHASE_PASS '+label)

try:
 save()
 # Static copies only; no native import, rendering or source-map installation yet.
 shutil.copytree(SOURCE/'blender',ROOT/'blender',ignore=shutil.ignore_patterns('*.blend1','*.blend2'))
 shutil.copytree(REPO/'scripts',ROOT/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(SOURCE/'scripts',ROOT/'scripts',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
 shutil.copytree(SOURCE/'export',ROOT/'export',ignore=shutil.ignore_patterns('lightmaps','full-lighting-refresh.json','lightmaps-coverage.json'))
 shutil.copytree(REPO/'docs/sites',ROOT/'docs/sites')
 shutil.copytree(REPO/'godot',GD,ignore=shutil.ignore_patterns('.godot','lightmaps','acceptance-captures','captures'))
 (GD/'lightmaps').mkdir()
 (GD/'tests/palette-before').mkdir()
 for kind in ['pavilion','wall']:
  shutil.copy2(SOURCE/'baseline/textures/atlases'/kind/(kind+'_basecolor.png'),GD/'tests/palette-before'/(kind+'_basecolor.png'))
 shutil.copy2(SOURCE/'export/garden-of-dreams.glb',GD/'assets/garden-of-dreams.glb')
 (GD/'assets/garden-source.json').write_text(json.dumps({'source_glb_sha256':EXPECTED},indent=2)+'\n')
 shutil.copy2(REPO/'textures/backdrops/moon-paint/atlas.json',GD/'tests/moon-paint-atlas.json')
 report['unchanged_moon_atlas_sha256']=sha(REPO/'textures/backdrops/moon-paint/atlas.json')
 config=GD/'project.godot';s=config.read_text();s,n=re.subn(r'^run/main_scene=.*$', 'run/main_scene="res://runtime/entry_route.tscn"',s,flags=re.M);assert n==1;config.write_text(s)
 assert 'site_bakes_enabled = false' not in (GD/'runtime/entry_route.tscn').read_text()
 assert not (GD/'.godot').exists() and not list((GD/'lightmaps').iterdir())
 report['runtime_inputs_sha256']={str(p.relative_to(GD)):sha(p) for p in sorted(GD.rglob('*')) if p.suffix in ('.gd','.gdshader','.tscn','.godot') and p.is_file()}
 report['status']='waiting_for_source_bake';save()
 Path('/tmp/garden-neutral-atlas-full-review.json').write_text(json.dumps({'folder':str(ROOT),'source_glb_sha256':EXPECTED,'report':str(REPORT),'orchestrator_pid':os.getpid(),'scope':report['scope']},indent=2)+'\n')
 emit('REVIEW_FIXTURE_PREPARED '+str(ROOT))
 prior_phase=None
 while True:
  bake=json.loads((SOURCE/'export/full-lighting-refresh.json').read_text())
  assert bake['source_glb_sha256']==EXPECTED
  if bake['status']=='failed':raise RuntimeError(('Source bake failed',bake))
  if bake['status']=='source_complete':
   names=['ordinary','backdrop-wash','terminal-spill','terminal-spill-pixels','native-pixels','coverage']
   assert [x['name'] for x in bake['phases']]==names and all(x['status']=='passed' and x['exit_code']==0 for x in bake['phases'])
   if not alive(bake['orchestrator_pid']):break
  elif not alive(bake['orchestrator_pid']):raise RuntimeError('Source baker exited without a terminal source-complete report')
  phase=bake['phases'][-1]['name']
  if phase!=prior_phase:emit('WAITING_FOR_SOURCE_PHASE '+phase);prior_phase=phase
  time.sleep(5)
 assert sha(SOURCE/'export/garden-of-dreams.glb')==EXPECTED and sha(SOURCE/'blender/authoring.blend')==AUTHOR
 report['source_bake_report']=bake
 report['status']='running';save()
 shutil.copytree(SOURCE/'export/lightmaps',ROOT/'export/lightmaps')
 shutil.copy2(SOURCE/'export/full-lighting-refresh.json',ROOT/'export/full-lighting-refresh.json')
 shutil.copy2(SOURCE/'export/lightmaps-coverage.json',ROOT/'export/lightmaps-coverage.json')
 for filename in ['lightmap-pixels.json','terminal-spill-pixels.json']:
  shutil.copy2(SOURCE/'export'/filename,ROOT/'export'/filename)
  assert not (ROOT/'export'/filename).is_symlink() and sha(ROOT/'export'/filename)==sha(SOURCE/'export'/filename)
 (ROOT/'precision-report-freezing.json').write_text(json.dumps({'files':{name:sha(ROOT/'export'/name) for name in ['lightmap-pixels.json','terminal-spill-pixels.json']},'scope':'Regular byte-identical completed native source reports, copied after all six source phases and baker exit.'},indent=2)+'\n')
 py=sys.executable
 for label,args,marker in [
  ('source-coverage',['verify_lightmaps.py','--current','--require-all'],'LIGHTMAP'),
  ('sync-full',['sync_full_lightmaps.py'],'FULL_LIGHTMAP_CATALOG_PASS'),
  ('sync-demo',['sync_lightmaps.py','--demo'],'Synced'),
  ('sync-priority2',['sync_priority2_lightmaps.py'],'PRIORITY2_LIGHTMAPS_PASS'),
  ('sync-wash',['sync_backdrop_wash.py'],'BACKDROP_WASH_CATALOG_PASS'),
  ('sync-spill',['sync_terminal_spill.py'],'TERMINAL_SPILL_CATALOG_PASS')]:
  run(label,[py,str(ROOT/'scripts'/args[0]),*args[1:]],marker)
 catalog_counts={'full-index.json':124,'demo-index.json':33,'priority2-index.json':29,'backdrop-wash-index.json':6,'terminal-spill-index.json':7}
 report['catalogs']={};pngs={}
 for filename,count in catalog_counts.items():
  path=GD/'lightmaps'/filename;records=json.loads(path.read_text());assert len(records)==count
  assert {x['source_glb_sha256'] for x in records.values()}=={EXPECTED}
  report['catalogs'][filename]={'receivers':len(records),'sha256':sha(path)}
  for record in records.values():
   for side in record.get('sides',{'front':record}).values():
    name=side['texture'];src=ROOT/'export/lightmaps'/name;dst=GD/'lightmaps'/name
    assert sha(src)==sha(dst);pngs[name]=sha(src)
 assert len(pngs)==141
 report['installed_source_png_sha256']=pngs;save()
 run('palette-source-contract',[py,str(ROOT/'scripts/build_garden_palette_contract.py'),'--source',str(ROOT/'export/garden-of-dreams.glb'),'--atlas-root',str(SOURCE),'--output',str(GD/'tests/garden-palette-contract.json')],'GARDEN_PALETTE_SOURCE_CONTRACT_PASS')
 run('source-import-contract',[py,str(ROOT/'scripts/build_godot_import_contract.py'),'--output',str(GD/'tests/source-contract.json')],'GODOT_IMPORT_SOURCE_CONTRACT')
 godot='/Applications/Godot.app/Contents/MacOS/Godot'
 head=[godot,'--headless','--path',str(GD)]
 native=[godot,'--path',str(GD)]
 run('initial-cold-import',head+['--editor','--import'])
 run('configure-lightmap-cap',[py,str(ROOT/'scripts/configure_lightmap_imports.py'),'--size-limit','256','--imperial-lossless512','--ouxiang-lossless512'],'Configured')
 run('configured-import',head+['--editor','--import'])
 run('first-source-contract',head+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(ROOT/'first-import.json')],'IMPORT_SOURCE_CONTRACT_PASS')
 shutil.rmtree(GD/'.godot')
 run('forced-cold-reimport',head+['--editor','--import'])
 run('second-source-contract',head+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(ROOT/'second-import.json')],'IMPORT_SOURCE_CONTRACT_PASS')
 first=json.loads((ROOT/'first-import.json').read_text());second=json.loads((ROOT/'second-import.json').read_text())
 assert first['snapshot']==second['snapshot'] and first['source_glb_sha256']==second['source_glb_sha256']==EXPECTED
 report['reimport_preservation']={k:first[k] for k in ['cameras_checked','colliders_checked','marker_metadata_checked','physics_rays_passed','render_meshes_snapshotted']}
 for label,flag,marker in [('camera','--corrupt-camera','Camera'),('collider','--corrupt-collider','Collider'),('marker','--corrupt-marker','marker')]:
  run('reject-'+label,head+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(ROOT/('rejected-'+label+'.json')),flag],marker,1)
  assert not (ROOT/('rejected-'+label+'.json')).exists()
 run('default-policy-rejection',head+['--script','res://tests/test_full_scene_lighting.gd'],'Full bake texture missing or runtime size exceeds the configured budget:',1)
 run('ouxiang-policy-rejection',head+['--script','res://tests/test_full_scene_lighting.gd','--','--imperial-lossless512'],'Full bake texture missing or runtime size exceeds the configured budget: SITE_ouxiang-xie_MAT_rooftile',1)
 for label,script,args,marker in [
  ('full-lighting','test_full_scene_lighting.gd',['--imperial-lossless512','--ouxiang-lossless512'],'FULL_SCENE_LIGHTING_PASS'),
  ('wash-normal','test_baked_backdrop_wash.gd',[],'BAKED_BACKDROP_WASH_PASS'),
  ('wash-demo','test_baked_backdrop_wash.gd',['--demo'],'BAKED_BACKDROP_WASH_PASS'),
  ('spill-normal','test_terminal_spill.gd',[],'TERMINAL_SPILL_PASS'),
  ('spill-demo','test_terminal_spill.gd',['--demo'],'TERMINAL_SPILL_PASS')]:
  run(label,head+['--script','res://tests/'+script,'--',*args],marker)
 run('saved-site-source-audit',['/Applications/Blender.app/Contents/MacOS/Blender','--background','--python-exit-code','1','--python',str(ROOT/'scripts/audit_site_sources.py')],'SITE_SOURCE_AUDIT_RECORDED')
 source_audit=json.loads((ROOT/'export/site-source-audit.json').read_text());assert len(source_audit['sites'])==14
 for slug,row in source_audit['sites'].items():assert not row['structural_differences_from_authoring'] and row['signs_match_authoring'] and not row['missing_current_bakes'] and not row['triggers_without_room_id'],slug
 for mode,args in [('normal',[]),('demo',['--demo'])]:
  run('native-texture-memory-'+mode,native+['--script','res://tests/audit_runtime_textures.gd','--','--output='+str(ROOT/('runtime-texture-inventory-'+mode+'.json')),*args],'RUNTIME_TEXTURE_INVENTORY_PASS')
  memory=json.loads((ROOT/('runtime-texture-inventory-'+mode+'.json')).read_text());assert memory['source_glb_sha256']==EXPECTED and memory['status']=='passed'
  if mode=='normal':
   for name in ['SITE_daguan-lou_MAT_rooftile','SITE_ouxiang-xie_MAT_rooftile']:
    receiver=next(row for row in memory['textures'] if row['resource_path']=='res://lightmaps/'+name+'.png');assert receiver['size']==[512,512] and receiver['image_format']==4 and receiver['image_data_bytes']==786432
 cap=ROOT/'review-captures';cap.mkdir()
 for label,args in [('framing',[]),('framing-density',['--density'])]:
  run('ouxiang-'+label,native+['--script','res://tests/test_oux_portrait_framing.gd','--','--output='+str(cap/label),*args],'OUXIANG_FRAMING_PASS')
  framing=json.loads((cap/label/'report.json').read_text());assert framing['status']=='passed'
 for label,script,marker in [('western','test_western_route.gd','WESTERN_ROUTE_PASS'),('nunnery','test_nunnery_route.gd','NUNNERY_ROUTE_PASS'),('mobile-ui','test_mobile_ui_scaling.gd','MOBILE_UI_SCALE_PASS')]:
  run('route-'+label,head+['--script','res://tests/'+script],marker)
 run('moon-source-transfer',native+['--script','res://tests/test_moon_paint_transfer.gd','--','--source=res://assets/garden-of-dreams.glb','--atlas=res://tests/moon-paint-atlas.json','--output-directory='+str(cap/'moon-transfer')],'MOON_PAINT_TRANSFER_PASS')
 run('moon-baked-scene',native+['--script','res://tests/diagnose_moon_scene_contrast.gd','--','--output-directory='+str(cap/'moon-scene')],'MOON_SCENE_CONTRAST_DIAGNOSIS_RECORDED')
 for label,args in [('desktop',[]),('portrait',['--mobile'])]:
  run('arrivals-'+label,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--output-directory='+str(cap/('arrivals-'+label)),*args],'ROUTE_RENDER_SAVED')
  arrival=json.loads((cap/('arrivals-'+label)/('route-'+label+'-report.json')).read_text())
  assert arrival['source_glb_sha256']==EXPECTED and len(arrival['captures'])==14
 for label,args in [('desktop',[]),('portrait',['--portrait'])]:
  out=cap/('tour-'+label);out.mkdir()
  run('tour-'+label,native+['--script','res://tests/render_full_garden_traversal.gd','--','--capture-directory='+str(out),'--output='+str(out/'report.json'),*args],'FULL_GARDEN_TRAVERSAL')
  tour=json.loads((out/'report.json').read_text());assert tour['source_glb_sha256']==EXPECTED
 for label,flag in [('plain','--corrupt-plain'),('atlas','--corrupt-atlas')]:
  rejected=ROOT/('rejected-palette-'+label+'.json')
  run('reject-palette-'+label,native+['--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(rejected),flag],'GARDEN_PALETTE_TRANSFER_REJECTED',1)
  assert not rejected.exists()
 for label,args in [('normal',[]),('demo',['--demo'])]:
  out=ROOT/('garden-palette-transfer-'+label+'.json')
  run('palette-transfer-'+label,native+['--script','res://tests/test_garden_palette_transfer.gd','--','--output='+str(out),*args],'GARDEN_PALETTE_TRANSFER_PASS')
  palette=json.loads(out.read_text());assert palette['status']=='passed' and palette['source_glb_sha256']==EXPECTED
 report['status']='technical_checks_complete_visual_review_pending';report['finished_at']=datetime.now(timezone.utc).isoformat();save()
 emit('NEUTRAL_ATLAS_FULL_TECHNICAL_REVIEW_COMPLETE '+str(ROOT))
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
