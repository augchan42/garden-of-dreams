from pathlib import Path
import json,hashlib,subprocess,re,datetime,struct
r=Path('/Users/auchan/projects/garden-of-dreams');w=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-runtime'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'running','source_glb_sha256':sha(r/'godot/assets/garden-of-dreams.glb'),'route_sha256':sha(r/'godot/runtime/entry_route.gd'),'test_sha256':sha(r/'godot/tests/test_ziling_framing.gd'),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':[]}
def save():(w/'accepted-focused-pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
save()
for mode,args in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
 out=w/('accepted-'+mode);log=w/('accepted-'+mode+'.log')
 cmd=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(r/'godot'),'--windowed','--resolution','390x844','--script','res://tests/test_ziling_framing.gd','--','--output='+str(out)]+args
 with log.open('w') as f:
  try:result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=130);code=result.returncode
  except subprocess.TimeoutExpired:code=1
 text=log.read_text();ok=code==0 and 'ZILING_FRAMING_RESULT 10 originals; 0 failures' in text and not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:)',text,re.M)
 phase={'name':mode,'command':cmd,'exit_code':code,'log':str(log),'log_sha256':sha(log),'status':'passed' if ok else 'failed'}
 if ok:
  data=json.loads((out/'report.json').read_text());assert data['route_sha256']==report['route_sha256'] and not data['errors']
  for row in data['rows']:
   path=Path(row['capture']);assert sha(path)==row['sha256'] and list(struct.unpack('>II',path.read_bytes()[16:24]))==row['pixels']
 report['phases'].append(phase);save();print('ZILING_FOCUSED',mode,phase['status'],flush=True)
 if not ok:report['status']='failed';save();print(text[-6000:]);raise SystemExit(1)
assert sha(r/'godot/runtime/entry_route.gd')==report['route_sha256']
report['status']='passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('ZILING_FOCUSED_PASS',flush=True)
