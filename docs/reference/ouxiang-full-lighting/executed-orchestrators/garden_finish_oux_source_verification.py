"""Wait for the existing reviewer to exit, then run one native source check.

This never starts or restarts the reviewer and never modifies production.
"""
from pathlib import Path
import datetime,hashlib,json,os,re,subprocess,tempfile,time
REPO=Path('/Users/auchan/projects/garden-of-dreams')
SOURCE=Path(json.load(open('/tmp/garden-oux-full-source.json'))['folder']).resolve()
REVIEW=Path(json.load(open('/tmp/garden-oux-chart-full-review.json'))['folder']).resolve()
ROOT=Path(tempfile.mkdtemp(prefix='garden-oux-source-verified-'))
EXPECTED='be80374cbc0959830205af0efbe198f044ec25df15e7933c91178d0ecf516e5a'
AUTHOR='9356f6ec3b310ffb408a915fe6a8824c3a6cc329c81daeef5c5dfc14fcb6658c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def alive(pid):
 try:os.kill(pid,0);return True
 except ProcessLookupError:return False
report={'status':'waiting_for_existing_reviewer','review_root':str(REVIEW),'folder':str(ROOT),
 'orchestrator_pid':os.getpid(),'source_glb_sha256':EXPECTED,'authoring_sha256':AUTHOR,
 'scope':'Fresh canonical default export and native saved authoring/site path ownership only. No source edits, repair, rendering, bake or production installation.',
 'phases':[],'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
def save():(ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
save();Path('/tmp/garden-oux-source-verified.json').write_text(json.dumps({'folder':str(ROOT),'report':str(ROOT/'verification.json'),'orchestrator_pid':os.getpid()})+'\n')
try:
 while True:
  review=json.load(open(REVIEW/'review-pipeline.json'))
  if review['status']=='failed':raise RuntimeError(('Review failed',review.get('error')))
  if review['status']=='technical_checks_complete_visual_review_pending' and not alive(review['orchestrator_pid']):break
  time.sleep(5)
 assert all(p['status']=='passed' for p in review['phases'])
 assert sha(SOURCE/'blender/authoring.blend')==sha(REPO/'blender/authoring.blend')==AUTHOR
 assert sha(SOURCE/'export/garden-of-dreams.glb')==EXPECTED
 report['completed_review_report_sha256']=sha(REVIEW/'review-pipeline.json')
 wrapper=ROOT/'inspect_and_export.py'
 wrapper.write_text('''import bpy,json,sys,runpy,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
REPO=Path('/Users/auchan/projects/garden-of-dreams')
SOURCE=Path(json.load(open('/tmp/garden-oux-full-source.json'))['folder']).resolve()
expected=[([-20.1,-.24,0],[-18.3,0,5]),([-25.9,-.24,4.1],[-18.3,0,5.9]),([-25.9,-.24,4.1],[-24.1,0,11.7])]
def bounds(o):
 points=[o.matrix_world@v.co for v in o.data.vertices]
 points=[(p.x,p.z,-p.y) for p in points]
 return [min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]
def inspect(label):
 col=bpy.data.collections['SITE_stage'];rows=[]
 for prefix in ['LONGCUI_approach','COL_longcui_approach']:
  objects=sorted([o for o in col.objects if o.name.startswith(prefix)],key=lambda o:o.name)
  assert len(objects)==3,(label,prefix,[o.name for o in objects])
  for i,o in enumerate(objects):
   assert o.type=='MESH' and len(o.data.vertices)==8 and len(o.data.polygons)==6
   lo,hi=bounds(o);elo,ehi=expected[i]
   assert all(abs(a-b)<1e-5 for a,b in zip(lo+hi,elo+ehi)),(label,o.name,lo,hi)
   if prefix=='LONGCUI_approach':assert len(o.data.materials)==1 and o.data.materials[0].name=='MAT_plaster_rock'
   rows.append({'name':o.name,'vertices':8,'polygons':6,'bounds_min_y_up':lo,'bounds_max_y_up':hi,
    'materials':[m.name if m else None for m in o.data.materials],
    'matrix_world':[list(row) for row in o.matrix_world],
    'hide_render':o.hide_render,'collision':prefix.startswith('COL_')})
 return rows
report={'status':'native_saved_path_ownership_verified','scope':'Read-only native saved-object ownership. No source repair applied.','authoring':inspect('authoring')}
sys.path.insert(0,str(REPO/'scripts'))
runpy.run_path(str(REPO/'scripts/export_garden.py'),run_name='__main__')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'blender/sites/SITE_stage.blend'))
report['stage_library']=inspect('stage library')
assert report['authoring']==report['stage_library']
report['saved_stage_library_sha256']=hashlib.sha256((SOURCE/'blender/sites/SITE_stage.blend').read_bytes()).hexdigest()
(ROOT/'saved-path-ownership.json').write_text(json.dumps(report,indent=2)+'\\n')
print('SAVED_NUNNERY_PATH_OWNERSHIP_PASS')
''')
 command=['/Applications/Blender.app/Contents/MacOS/Blender','--background',str(SOURCE/'blender/authoring.blend'),'--python-exit-code','1','--python',str(wrapper),'--','--output-root',str(ROOT)]
 log=ROOT/'default-export-path-ownership.log'
 phase={'name':'native-default-export-and-saved-path-ownership','command':command,'log':str(log),'status':'running'}
 report['status']='running';report['phases'].append(phase);save();print('NATIVE_OUX_SOURCE_VERIFICATION_START',ROOT,flush=True)
 with log.open('w') as out:
  child=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT);phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 text=log.read_text();assert phase['exit_code']==0,text[-3000:]
 assert 'SAVED_NUNNERY_PATH_OWNERSHIP_PASS' in text and not re.search(r'Traceback|^Error:',text,re.M),text[-3000:]
 phase['log_sha256']=sha(log);phase['status']='passed'
 report['default_export_equality']={}
 for p in [SOURCE/'export/garden-of-dreams.glb',*sorted((SOURCE/'export/sites').glob('*.glb'))]:
  target=ROOT/'export'/p.relative_to(SOURCE/'export');assert p.read_bytes()==target.read_bytes(),str(p)
  report['default_export_equality'][str(p.relative_to(SOURCE/'export'))]=sha(target)
 assert len(report['default_export_equality'])==16
 assert sha(ROOT/'export/garden-of-dreams.glb')==EXPECTED
 assert sha(SOURCE/'blender/authoring.blend')==sha(REPO/'blender/authoring.blend')==AUTHOR
 report['canonical_export_script_sha256']=sha(REPO/'scripts/export_garden.py')
 report['canonical_oux_allocator_sha256']=sha(REPO/'scripts/ouxiang_tile_lightmap_uv.py')
 report['native_path_ownership_sha256']=sha(ROOT/'saved-path-ownership.json')
 report['status']='native_default_export_and_saved_path_ownership_passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('OUX_SOURCE_VERIFICATION_PASS',ROOT,flush=True)
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
