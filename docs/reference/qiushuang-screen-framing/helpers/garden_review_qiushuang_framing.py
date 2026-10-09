from pathlib import Path
import json, hashlib, subprocess, re, datetime

repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/qiushuang-runtime'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
focused=json.loads((work/'accepted-focused-pipeline.json').read_text())
assert focused['status']=='passed' and len(focused['phases'])==3
assert sha(repo/'godot/runtime/entry_route.gd')==focused['route_sha256']
assert sha(repo/'godot/tests/test_qiushuang_framing.gd')==focused['test_sha256']
for phase in focused['phases']:
    assert phase['exit_code']==0 and sha(phase['log'])==phase['log_sha256']
engine='/Applications/Godot.app/Contents/MacOS/Godot'
base=[engine,'--headless','--path',str(repo/'godot')]
native=[engine,'--path',str(repo/'godot'),'--windowed','--resolution','390x844']
commands=[('cold-import',base+['--editor','--import'],None,90),('source-contract',base+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(work/'production-source-contract.json')],'IMPORT_SOURCE_CONTRACT_PASS',60)]
for name,script,marker,timeout in [('hilltop','test_hilltop_route.gd','HILLTOP_ROUTE_PASS',150),('study','test_study_route.gd','STUDY_ROUTE_PASS',150),('courtyard','test_courtyard_route.gd','COURTYARD_ROUTE_PASS',120),('farmhouse','test_farmhouse_route.gd','FARMHOUSE_ROUTE_PASS',120),('mobile-ui','test_mobile_ui_scaling.gd','MOBILE_UI_SCALE_PASS',60),('gate-reveal','test_gate_reveal.gd','GATE_REVEAL_PASS',120),('first-reading-demo','test_first_reading_demo.gd','FIRST_READING_DEMO_PASS',180)]:
    commands.append((name,base+['--script','res://tests/'+script],marker,timeout))
commands.append(('pond-view',native+['--script','res://tests/test_pond_view.gd'],'POND_VIEW_PASS',90))
for name,script,marker in [('tubi-framing','test_tubi_framing.gd','TUBI_FRAMING_RESULT 10 originals; 0 failures'),('portrait-architecture','test_portrait_architecture.gd','PORTRAIT_ARCHITECTURE_RESULT 15 captures; 0 failures'),('hengwu-details','test_hengwu_detail_framing.gd','HENGWU_DETAIL_FRAMING_RESULT 10 captures; 0 failures'),('ouxiang-framing','test_oux_portrait_framing.gd','OUXIANG_FRAMING_PASS')]:
    commands.append((name,native+['--script','res://tests/'+script,'--','--output='+str(work/('regression-'+name))],marker,120))
report={'status':'running','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':focused['source_glb_sha256'],'route_sha256':focused['route_sha256'],'phases':[],'scope':'Installed project import/source, actual bulletin/study/hilltop climb/descent and adjacent routes, mobile UI, first-reading and Tubi/Hengwu/architecture/Ouxiang camera-state regressions. No physical-phone, new full-tour, sustained or final-art acceptance.'}
def save(): (work/'regression-pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
save()
for name,cmd,marker,timeout in commands:
    log=work/('regression-'+name+'.log')
    with log.open('w') as f:
        try:result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout);exit_code=result.returncode
        except subprocess.TimeoutExpired:exit_code=1
    content=log.read_text()
    ok=exit_code==0 and not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:|Assertion failed)',content,re.M) and (marker is None or marker in content)
    report['phases'].append({'name':name,'command':cmd,'exit_code':exit_code,'log':str(log),'log_sha256':sha(log),'status':'passed' if ok else 'failed'});save();print('QIUSHUANG_REGRESSION',name,'passed' if ok else 'failed',flush=True)
    if not ok:report['status']='failed';save();print(content[-3500:]);raise SystemExit(1)
assert sha(repo/'godot/runtime/entry_route.gd')==report['route_sha256']
assert sha(repo/'godot/assets/garden-of-dreams.glb')==report['source_glb_sha256']
report['status']='passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('QIUSHUANG_FRAMING_REGRESSIONS_PASS',flush=True)
