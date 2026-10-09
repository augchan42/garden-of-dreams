from pathlib import Path
import json,hashlib,subprocess,re,datetime
repo=Path('/Users/auchan/projects/garden-of-dreams');work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-detail-runtime'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
focused=json.load(open(work/'accepted-focused-pipeline.json'))
assert focused['status']=='passed' and len(focused['phases'])==3
assert sha(repo/'godot/runtime/entry_route.gd')==focused['route_sha256']
assert sha(repo/'godot/tests/test_hengwu_detail_framing.gd')==focused['test_sha256']
for p in focused['phases']:assert p['status']=='passed' and p['exit_code']==0 and sha(p['log'])==p['log_sha256']
engine='/Applications/Godot.app/Contents/MacOS/Godot'
report={'status':'running','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':focused['source_glb_sha256'],'route_sha256':focused['route_sha256'],'phases':[],'scope':'Installed project import/source agreement, adjacent collision routes, other camera/resize flows, density-unit UI and the first-reading demo. These are not physical-phone, sustained or final all-site art checks.'}
base=[engine,'--headless','--path',str(repo/'godot')]
commands=[('cold-import',base+['--editor','--import'],None,90),('source-contract',base+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(work/'production-source-contract.json')],'IMPORT_SOURCE_CONTRACT_PASS',60)]
for name,script,marker,timeout in [('courtyard','test_courtyard_route.gd','COURTYARD_ROUTE_PASS',120),('farmhouse','test_farmhouse_route.gd','FARMHOUSE_ROUTE_PASS',120),('mobile-ui','test_mobile_ui_scaling.gd','MOBILE_UI_SCALE_PASS',60),('gate-reveal','test_gate_reveal.gd','GATE_REVEAL_PASS',120),('first-reading-demo','test_first_reading_demo.gd','FIRST_READING_DEMO_PASS',180)]:commands.append((name,base+['--script','res://tests/'+script],marker,timeout))
native=[engine,'--path',str(repo/'godot'),'--windowed','--resolution','390x844']
commands.append(('pond-view',native+['--script','res://tests/test_pond_view.gd'],'POND_VIEW_PASS',90))
commands.append(('portrait-architecture',native+['--script','res://tests/test_portrait_architecture.gd','--','--output='+str(work/'regression-portrait-architecture')],'PORTRAIT_ARCHITECTURE_RESULT 15 captures; 0 failures',90))
commands.append(('ouxiang-framing',native+['--script','res://tests/test_oux_portrait_framing.gd','--','--output='+str(work/'regression-ouxiang-framing')],'OUXIANG_FRAMING_PASS',90))
def save(): (work/'regression-pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
save()
for name,cmd,marker,timeout in commands:
 log=work/('regression-'+name+'.log')
 with log.open('w') as f:
  result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 txt=log.read_text();ok=result.returncode==0 and not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:|Assertion failed)',txt,re.M) and (marker is None or marker in txt)
 report['phases'].append({'name':name,'command':cmd,'exit_code':result.returncode,'log':str(log),'log_sha256':sha(log),'status':'passed' if ok else 'failed'});save();print('HENGWU_REGRESSION',name,'passed' if ok else 'failed',flush=True)
 if not ok:report['status']='failed';save();print(txt[-3500:]);raise SystemExit(1)
assert sha(repo/'godot/runtime/entry_route.gd')==report['route_sha256']
assert sha(repo/'godot/assets/garden-of-dreams.glb')==report['source_glb_sha256']
report['status']='passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('HENGWU_DETAILS_REGRESSIONS_PASS',flush=True)
