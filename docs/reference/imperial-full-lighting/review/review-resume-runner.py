"""Resume the existing failed candidate review, preserving its first rejection.
Only the full-lighting gate changes; existing imports and passed phases are reused.
"""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,shutil
from datetime import datetime,timezone
ROOT=Path(json.loads(Path('/tmp/garden-imperial-chart-full-review.json').read_text())['folder']).resolve()
SOURCE=Path(json.loads(Path('/tmp/garden-imperial-full-source.json').read_text())['folder']).resolve()
GD=ROOT/'godot'; LOG=ROOT/'resume-logs'; LOG.mkdir(exist_ok=False)
REPORT=ROOT/'review-resume-pipeline.json'
EXPECTED='361a67c759974e4fb5897a15d5a7354076ef30392b7a6ed988cca6029f198611'
AUTHOR='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
initial=json.loads((ROOT/'review-pipeline.json').read_text())
revision=json.loads((ROOT/'review-test-revision.json').read_text())
assert initial['status']=='failed' and initial['phases'][-1]['name']=='full-lighting' and initial['phases'][-1]['exit_code']==1
assert all(p['status']=='passed' for p in initial['phases'][:-1])
assert 'SITE_daguan-lou_MAT_rooftile' in initial['error']
for p in initial['phases']:
 if 'log_sha256' in p: assert sha(p['log'])==p['log_sha256']
for key,value in initial['runtime_inputs_sha256'].items():
 actual=sha(GD/key)
 if key=='tests/test_full_scene_lighting.gd':assert value==revision['before_sha256'] and actual==revision['after_sha256']
 else:assert actual==value,key
for filename,row in initial['catalogs'].items():assert sha(GD/'lightmaps'/filename)==row['sha256']
for filename,value in initial['installed_source_png_sha256'].items():
 assert sha(GD/'lightmaps'/filename)==sha(SOURCE/'export/lightmaps'/filename)==value
bake=json.loads((SOURCE/'export/full-lighting-refresh.json').read_text())
assert bake['status']=='source_complete' and bake['source_glb_sha256']==EXPECTED
assert [p['name'] for p in bake['phases']]==['ordinary','backdrop-wash','terminal-spill','terminal-spill-pixels','native-pixels','coverage']
assert all(p['status']=='passed' and p['exit_code']==0 for p in bake['phases'])
for path in [SOURCE/'export/garden-of-dreams.glb',ROOT/'export/garden-of-dreams.glb',GD/'assets/garden-of-dreams.glb']:assert sha(path)==EXPECTED
assert sha(SOURCE/'blender/authoring.blend')==AUTHOR
for filename in ['lightmap-pixels.json','terminal-spill-pixels.json']:
 path=ROOT/'export'/filename
 assert not path.is_symlink() and sha(path)==sha(SOURCE/'export'/filename)
assert (ROOT/'precision-report-freezing.json').is_file()
py=sys.executable;godot='/Applications/Godot.app/Contents/MacOS/Godot'
head=[godot,'--headless','--path',str(GD)];native=[godot,'--path',str(GD)]
report={'status':'running','folder':str(ROOT),'source_root':str(SOURCE),'source_glb_sha256':EXPECTED,'authoring_blend_sha256':AUTHOR,
 'orchestrator_pid':os.getpid(),'started_at':datetime.now(timezone.utc).isoformat(),
 'initial_review_sha256':sha(ROOT/'review-pipeline.json'),'test_revision_sha256':sha(ROOT/'review-test-revision.json'),
 'precision_freezing_sha256':sha(ROOT/'precision-report-freezing.json'),
 'source_bake_report_sha256':sha(SOURCE/'export/full-lighting-refresh.json'),
 'inherited_passed_phases':[p['name'] for p in initial['phases'][:-1]],
 'runtime_inputs_sha256':{key:sha(GD/key) for key in initial['runtime_inputs_sha256']},
 'scope':'Resume of exact-source candidate; initial native rejection retained. Only explicit verified-UV/import/decoded-size test exception changed. No rebake, reimport, production adoption, device or final-art acceptance.', 'phases':[]}
def save():REPORT.write_text(json.dumps(report,indent=2)+'\n')
def emit(message):print(message,flush=True)
def run(label,command,expected_marker=None,expected_exit=0):
 assert sha(ROOT/'export/garden-of-dreams.glb')==EXPECTED
 phase={'name':label,'command':command,'status':'running','log':str(LOG/(label+'.log'))};report['phases'].append(phase);save();emit('REVIEW_PHASE_START '+label)
 with open(phase['log'],'w') as log:
  child=subprocess.Popen(command,cwd=GD,stdout=log,stderr=subprocess.STDOUT)
  phase['pid']=child.pid;save()
  try:phase['exit_code']=child.wait(timeout=1800)
  except subprocess.TimeoutExpired:
   child.terminate();phase['exit_code']=child.wait(timeout=30);phase['status']='timed_out';save();raise
 text=Path(phase['log']).read_text(errors='replace');phase['log_sha256']=sha(phase['log']);save()
 assert phase['exit_code']==expected_exit,(label,phase['exit_code'],text[-3000:])
 if expected_exit==0:assert not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed)',text),(label,text[-4000:])
 if expected_marker:assert expected_marker in text,(label,'missing marker',text[-3000:])
 phase['status']='passed';save();emit('REVIEW_PHASE_PASS '+label)
try:
 save()
 run('default-policy-rejection',head+['--script','res://tests/test_full_scene_lighting.gd'],'Full bake texture missing or runtime size exceeds the configured budget: SITE_daguan-lou_MAT_rooftile',1)
 for label,script,args,marker in [
  ('full-lighting','test_full_scene_lighting.gd',['--imperial-lossless512'],'FULL_SCENE_LIGHTING_PASS'),
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
   receiver=next(row for row in memory['textures'] if row['resource_path']=='res://lightmaps/SITE_daguan-lou_MAT_rooftile.png');assert receiver['size']==[512,512] and receiver['image_format']==4 and receiver['image_data_bytes']==786432
 cap=ROOT/'review-captures';cap.mkdir(exist_ok=False)
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
 report['status']='technical_checks_complete_visual_review_pending';report['finished_at']=datetime.now(timezone.utc).isoformat();save()
 emit('IMPERIAL_CHART_FULL_TECHNICAL_REVIEW_COMPLETE '+str(ROOT))
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
