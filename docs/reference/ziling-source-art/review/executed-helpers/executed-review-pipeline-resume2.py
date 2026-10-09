"""One sequential isolated review after the existing complete source pipeline exits."""
from pathlib import Path
import json,hashlib,os,sys,time,shutil,subprocess,re,datetime,struct
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root']);s=w/'reeds-volume';root=Path(json.loads(Path('/tmp/garden-ziling-lit-review.json').read_text())['root']);g=root/'godot';logroot=root/'review-logs-resume2';assert not logroot.exists();logroot.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();expected=sha(s/'export/garden-of-dreams.glb');author=sha(s/'blender/authoring.blend');report={'status':'validating_completed_review_evidence','source_glb_sha256':expected,'authoring_sha256':author,'root':str(root),'orchestrator_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':[],'scope':'All work is isolated. The current source bake and preparation parent must both finish and exit before any native review job. No production adoption, visual acceptance, phone budgets or services completion.'}
def save():(root/'review-pipeline-resume2.json').write_text(json.dumps(report,indent=2)+'\n')
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
 save();shutil.copyfile(__file__,root/'executed-review-pipeline-resume2.py')
 bake=json.loads((s/'export/full-lighting-refresh.json').read_text());prep=json.loads((s/'lighting-preparation.json').read_text())
 assert bake['status']=='source_complete' and prep['status']=='complete_source_lighting_passed_native_review_pending'
 assert not alive(bake['orchestrator_pid']) and not alive(prep['orchestrator_pid'])
 assert all(p['status']=='passed' and p['exit_code']==0 for p in bake['phases'])
 frozen=json.loads((s/'full-lighting-inputs.json').read_text())['files']
 for name,h in frozen.items():assert sha(s/name)==h,name
 previous=json.loads((root/'review-pipeline-resume1.json').read_text());assert previous['status']=='failed' and previous['source_glb_sha256']==expected and previous['authoring_sha256']==author
 assert previous['phases'][-1]['name']=='adjacent-architecture' and previous['phases'][-1]['exit_code']==0
 reused=previous['reused_checked_phases']+previous['phases'][:-1]
 for p in reused:assert p['status']=='passed' and p['exit_code']==0 and sha(p['log'])==p['log_sha256']
 phase=previous['phases'][-1];assert sha(phase['log'])==phase['log_sha256'] and 'PORTRAIT_ARCHITECTURE_RESULT 15 captures; 0 failures' in Path(phase['log']).read_text()
 ap=root/'review-captures/architecture/report.json';architecture=json.loads(ap.read_text())
 assert architecture['status']=='portrait_architecture_behavior_passed' and not architecture['errors'] and len(architecture['rows'])==15
 assert architecture['source_glb_sha256']==expected and architecture['route_sha256']==sha(g/'runtime/entry_route.gd') and architecture['test_sha256']==sha(g/'tests/test_portrait_architecture.gd')
 for row in architecture['rows']:
  p=Path(row['capture']);assert sha(p)==row['sha256'] and list(struct.unpack('>II',p.read_bytes()[16:24]))==row['capture_pixels']
 assert sha(g/'assets/garden-of-dreams.glb')==expected
 assert sha(root/'blender/kits/KIT_flora.blend')==sha(w/'flora-collider-preview-repair/KIT_flora.blend')
 assert sha(root/'scripts/complete_flora_kit.py')==sha(w/'source-code-candidates/complete_flora_kit.py')
 report.update(status='native_review_running',reused_checked_phases=reused,source_bake_report=bake,frozen_inputs_verified=len(frozen),previous_review_sha256=sha(root/'review-pipeline-resume1.json'),architecture_completion_verification={'status':'passed_exact_log_and_15_hashed_original_reports','report_sha256':sha(ap),'log_sha256':sha(phase['log']),'scope':'Runner originally expected a nonexistent PASS marker. Test exited0 and printed exact RESULT15/zero failures. Original failed runner report retained; no scene/test/image edited.'})
 save()
 godot='/Applications/Godot.app/Contents/MacOS/Godot';native=[godot,'--path',str(g),'--windowed','--resolution','1410x600']
 cap=root/'review-captures-resume2';assert not cap.exists();cap.mkdir()
 for label,script,marker in [('hengwu','test_hengwu_detail_framing.gd','HENGWU_DETAIL_FRAMING_RESULT'),('tubi','test_tubi_framing.gd','TUBI_FRAMING_RESULT'),('qiushuang','test_qiushuang_framing.gd','QIUSHUANG_FRAMING_RESULT'),('pond','test_pond_view.gd','POND_VIEW_PASS')]:
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
