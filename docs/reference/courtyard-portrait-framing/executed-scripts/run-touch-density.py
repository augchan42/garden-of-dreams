from pathlib import Path
import subprocess,sys,json,hashlib
w=Path(__file__).resolve().parent
expected=hashlib.sha256((w/'candidate-godot/runtime/entry_route.gd').read_bytes()).hexdigest()
report={'status':'running','runtime_sha256':expected,'phases':[]};out=w/'touch-density-queue.json'
for label,flags in [('posed-touch',['--touch']),('posed-density',['--density'])]:
 assert hashlib.sha256((w/'candidate-godot/runtime/entry_route.gd').read_bytes()).hexdigest()==expected
 log=w/(label+'-output.log');row={'label':label,'status':'running'};report['phases'].append(row);out.write_text(json.dumps(report,indent=2)+'\n')
 with log.open('w') as f:code=subprocess.run([sys.executable,str(w/'run-framing.py'),'--game','candidate','--label',label,*flags],stdout=f,stderr=subprocess.STDOUT).returncode
 row['exit_code']=code;row['status']='passed' if code==0 else 'failed';out.write_text(json.dumps(report,indent=2)+'\n');assert code==0,log.read_text()[-1500:]
report['status']='touch_density_passed';out.write_text(json.dumps(report,indent=2)+'\n');print('TOUCH_DENSITY_PASSED',flush=True)
