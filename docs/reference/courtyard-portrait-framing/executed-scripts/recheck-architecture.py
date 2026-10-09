from pathlib import Path
import json,subprocess,hashlib,datetime
work=Path(__file__).resolve().parent
game=work/'candidate-godot';out=work/'final-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not out.exists();out.mkdir()
prior=json.loads((work/'final-v2/pipeline.json').read_text())
frozen=json.loads((work/'final-v2/frozen-inputs.json').read_text())
for n,h in frozen.items():
 if n!='tests/test_portrait_architecture.gd':assert sha(game/n)==h,n
frozen['tests/test_portrait_architecture.gd']=sha(game/'tests/test_portrait_architecture.gd')
(out/'frozen-inputs.json').write_text(json.dumps(frozen,indent=2)+'\n')
report={'status':'running','runtime_sha256':sha(game/'runtime/entry_route.gd'),'source_glb_sha256':prior['source_glb_sha256'],'phases':[],'scope':'Three affected architecture modes repeated after test-only wait for real FloraLOD interval.32original positive phases remain preserved under final-v2; runtime unchanged.'}
def save():(out/'pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
for original in prior['phases']:
 if not original['name'].startswith('architecture-'):continue
 cmd=[s.replace(str(work/'final-v2'),str(out)) for s in original['command']]
 row={'name':original['name'],'command':cmd,'timeout':original['timeout'],'native_report':original['native_report'].replace(str(work/'final-v2'),str(out)),'log':str(out/(original['name']+'.log')),'status':'running'}
 report['phases'].append(row)
 with Path(row['log']).open('w') as f:
  child=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);row['pid']=child.pid;save()
  try:code=child.wait(timeout=row['timeout'])
  except subprocess.TimeoutExpired:
   child.terminate()
   try:child.wait(timeout=10)
   except subprocess.TimeoutExpired:child.kill();child.wait()
   raise
 row.update(exit_code=code,log_sha256=sha(row['log']))
 text=Path(row['log']).read_text();assert code==0 and 'ERROR:' not in text and 'SCRIPT ERROR:' not in text,text[-2000:]
 d=json.loads(Path(row['native_report']).read_text());assert not d['errors'] and d['status']=='portrait_architecture_behavior_passed'
 row.update(status='passed',native_report_sha256=sha(row['native_report']));save()
for n,h in frozen.items():assert sha(game/n)==h,n
report['status']='three_architecture_rechecks_passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('ARCHITECTURE_REAL_LOD_WAIT_PASSED3',flush=True)
