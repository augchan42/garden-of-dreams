from pathlib import Path
import subprocess, json, hashlib, datetime
work=Path(__file__).resolve().parent
game=work/'baseline-godot'
exe='/Applications/Godot.app/Contents/MacOS/Godot'
report={'status':'running','phases':[],'scope':'Isolated current-main import then one actual courtyard RED test. One native child at a time. Protected user apps untouched.'}
output=work/'baseline-pipeline.json'
def save():output.write_text(json.dumps(report,indent=2)+'\n')
for name,command in [('import',[exe,'--headless','--path',str(game),'--editor','--import']),('courtyard-red',[exe,'--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/test_yihong_framing.gd','--','--output='+str(work/'baseline-normal')])]:
 log=work/(name+'.log')
 row={'name':name,'command':command,'status':'running','log':str(log)};report['phases'].append(row)
 with log.open('w') as f:
  process=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT);row['pid']=process.pid;save()
  try:code=process.wait(timeout=300 if name=='import' else 140)
  except subprocess.TimeoutExpired:
   process.terminate()
   try:process.wait(timeout=10)
   except subprocess.TimeoutExpired:process.kill();process.wait()
   row['status']='owned_native_timeout';save();raise
 row['exit_code']=code;row['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest()
 text=log.read_text()
 assert 'SCRIPT ERROR:' not in text and 'Parse Error' not in text,text[-2000:]
 if name=='import':assert code==0 and 'ERROR:' not in text;row['status']='passed'
 else:
  native=json.loads((work/'baseline-normal/report.json').read_text())
  assert code==1 and native['status']=='rejected' and len(native['errors'])>=3
  assert native['facade_vertex_count']==2744 and native['closed_door_vertex_count']==48
  assert len(native['rows'])==15
  row['status']='passed_expected_framing_rejections';row['failure_count']=len(native['errors'])
 save()
report['status']='baseline_actual_courtyard_failures_reproduced';save()
print('BASELINE_COURTYARD_RED_VERIFIED',report['phases'][-1]['failure_count'],flush=True)
