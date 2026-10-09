from pathlib import Path
import json,hashlib,subprocess,re,datetime,struct
r=Path('/Users/auchan/projects/garden-of-dreams');w=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-runtime';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
f=json.loads((w/'accepted-focused-pipeline.json').read_text());assert f['status']=='passed' and len(f['phases'])==3
assert sha(r/'godot/runtime/entry_route.gd')==f['route_sha256'];assert sha(r/'godot/tests/test_ziling_framing.gd')==f['test_sha256']
for phase in f['phases']:assert phase['exit_code']==0 and sha(phase['log'])==phase['log_sha256']
g='/Applications/Godot.app/Contents/MacOS/Godot';base=[g,'--headless','--path',str(r/'godot')];native=[g,'--path',str(r/'godot'),'--windowed','--resolution','390x844']
commands=[('cold-import',base+['--editor','--import'],None,90),('source-contract',base+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(w/'production-source-contract.json')],'IMPORT_SOURCE_CONTRACT_PASS',60),('western-route',base+['--script','res://tests/test_western_route.gd'],'WESTERN_ROUTE_PASS',150),('mobile-ui',base+['--script','res://tests/test_mobile_ui_scaling.gd'],'MOBILE_UI_SCALE_PASS',60),('pond-view',native+['--script','res://tests/test_pond_view.gd'],'POND_VIEW_PASS',90)]
for name,script,marker in [('tubi-framing','test_tubi_framing.gd','TUBI_FRAMING_RESULT 10 originals; 0 failures'),('qiushuang-framing','test_qiushuang_framing.gd','QIUSHUANG_FRAMING_RESULT 18 originals; 0 failures'),('portrait-architecture','test_portrait_architecture.gd','PORTRAIT_ARCHITECTURE_RESULT 15 captures; 0 failures'),('hengwu-details','test_hengwu_detail_framing.gd','HENGWU_DETAIL_FRAMING_RESULT 10 captures; 0 failures'),('ouxiang-framing','test_oux_portrait_framing.gd','OUXIANG_FRAMING_PASS')]:commands.append((name,native+['--script','res://tests/'+script,'--','--output='+str(w/('regression-'+name))],marker,120))
p={'status':'running','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':f['source_glb_sha256'],'route_sha256':f['route_sha256'],'phases':[],'scope':'Installed import/source, actual western approach/island/return floor support, mobile UI and pond/Ouxiang/Hengwu/architecture/Tubi/Qiushuang camera-state regressions. No new full moving fourteen-room tour, physical-phone, sustained or final site-art acceptance.'}
def save():(w/'regression-pipeline.json').write_text(json.dumps(p,indent=2)+'\n')
save()
for name,cmd,marker,timeout in commands:
 log=w/('regression-'+name+'.log')
 with log.open('w') as out:
  try:res=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=timeout);code=res.returncode
  except subprocess.TimeoutExpired:code=124
 text=log.read_text();ok=code==0 and not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:|Assertion failed)',text,re.M) and (marker is None or marker in text)
 p['phases'].append({'name':name,'command':cmd,'exit_code':code,'log':str(log),'log_sha256':sha(log),'status':'passed' if ok else 'failed'});save();print('ZILING_REGRESSION',name,'passed' if ok else 'failed',flush=True)
 if not ok:p['status']='failed';save();print(text[-4000:]);raise SystemExit(1)
assert sha(r/'godot/runtime/entry_route.gd')==p['route_sha256'];assert sha(r/'godot/assets/garden-of-dreams.glb')==p['source_glb_sha256']
p['status']='passed';p['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('ZILING_FRAMING_REGRESSIONS_PASS',flush=True)
