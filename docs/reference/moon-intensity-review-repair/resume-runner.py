"""Prepare an isolated candidate and review it after the full source bake passes.

This never modifies production or restarts the source baker. Every native job
runs sequentially, after all six source phases and the source orchestrator exit.
"""
from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone

REPO=Path('/Users/auchan/projects/garden-of-dreams')
SOURCE=Path(json.loads(Path('/tmp/garden-moon-intensity-final.json').read_text())['folder'])
EXPECTED='8d1d9b4e4372ee097199f0b8b0c1a33f72aa55cb6ce978cf5a847b75febadf3f'
AUTHOR='a273a4c0ea33c9897f3096f51b5833b905e04a6d0ca62cab001e8291aa93b8de'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE/'export/garden-of-dreams.glb')==EXPECTED
assert sha(SOURCE/'blender/authoring.blend')==AUTHOR
ROOT=Path(json.loads(Path('/tmp/garden-moon-intensity-baked-review.json').read_text())['folder'])
GD=ROOT/'godot'
LOG=ROOT/'review-logs';LOG.mkdir(exist_ok=True)
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

report=json.loads(REPORT.read_text())
assert report['status']=='failed' and report['phases'][0]['exit_code']==1
report['rejected_attempts']=[{'reason':'Missing native-precision indexes in the static review fixture','folder':str(ROOT/'review-rejections/missing-native-pixel-index')}]
report['phases']=[]
report.pop('error',None)
report['status']='resuming_after_fixture_metadata_repair'
report['resuming_at']=datetime.now(timezone.utc).isoformat()
save()
try:
 bake=json.loads((SOURCE/'export/full-lighting-refresh.json').read_text())
 assert bake['status']=='source_complete' and bake['source_glb_sha256']==EXPECTED
 assert len(bake['phases'])==6 and all(x['status']=='passed' and x['exit_code']==0 for x in bake['phases'])
 assert not alive(bake['orchestrator_pid'])
 for n in ['lightmap-pixels.json','terminal-spill-pixels.json']:
  assert sha(ROOT/'export'/n)==sha(SOURCE/'export'/n)
 for rel,digest in report['runtime_inputs_sha256'].items():assert sha(GD/rel)==digest
 report['source_native_pixel_indexes_sha256']={n:sha(ROOT/'export'/n) for n in ['lightmap-pixels.json','terminal-spill-pixels.json']}
 report['status']='running';save()
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
 run('source-import-contract',[py,str(ROOT/'scripts/build_godot_import_contract.py'),'--output',str(GD/'tests/source-contract.json')],'GODOT_IMPORT_SOURCE_CONTRACT')
 godot='/Applications/Godot.app/Contents/MacOS/Godot'
 head=[godot,'--headless','--path',str(GD)]
 native=[godot,'--path',str(GD)]
 run('initial-cold-import',head+['--editor','--import'])
 run('configure-lightmap-cap',[py,str(ROOT/'scripts/configure_lightmap_imports.py'),'--size-limit','256'],'Configured')
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
 for label,script,args,marker in [
  ('full-lighting','test_full_scene_lighting.gd',[],'FULL_SCENE_LIGHTING_PASS'),
  ('wash-normal','test_baked_backdrop_wash.gd',[],'BAKED_BACKDROP_WASH_PASS'),
  ('wash-demo','test_baked_backdrop_wash.gd',['--demo'],'BAKED_BACKDROP_WASH_PASS'),
  ('spill-normal','test_terminal_spill.gd',[],'TERMINAL_SPILL_PASS'),
  ('spill-demo','test_terminal_spill.gd',['--demo'],'TERMINAL_SPILL_PASS')]:
  run(label,head+['--script','res://tests/'+script,'--',*args],marker)
 cap=ROOT/'review-captures';cap.mkdir()
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
 emit('MOON_INTENSITY_TECHNICAL_REVIEW_COMPLETE '+str(ROOT))
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
