from pathlib import Path
import subprocess,json,hashlib,argparse
parser=argparse.ArgumentParser();parser.add_argument('--game',choices=['baseline','candidate'],required=True);parser.add_argument('--label',required=True);parser.add_argument('--expect-rejection',action='store_true');parser.add_argument('--touch',action='store_true');parser.add_argument('--density',action='store_true');args=parser.parse_args()
work=Path(__file__).resolve().parent;game=work/(args.game+'-godot');captures=work/args.label
assert not captures.exists(),'Preserve earlier native attempts'
exe='/Applications/Godot.app/Contents/MacOS/Godot'
report={'status':'running','label':args.label,'phases':[],'runtime_sha256':hashlib.sha256((game/'runtime/entry_route.gd').read_bytes()).hexdigest(),'test_sha256':hashlib.sha256((game/'tests/test_yihong_framing.gd').read_bytes()).hexdigest()};output=work/(args.label+'-pipeline.json')
def save():output.write_text(json.dumps(report,indent=2)+'\n')
command=[exe,'--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/test_yihong_framing.gd','--','--output='+str(captures)]
if args.touch:command.append('--touch')
if args.density:command.append('--density')
for name,cmd in [('import',[exe,'--headless','--path',str(game),'--editor','--import']),('framing',command)]:
 log=work/(args.label+'-'+name+'.log');row={'name':name,'command':cmd,'status':'running','log':str(log)};report['phases'].append(row)
 with log.open('w') as f:
  child=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);row['pid']=child.pid;save()
  try:code=child.wait(timeout=300 if name=='import' else 140)
  except subprocess.TimeoutExpired:
   child.terminate()
   try:child.wait(timeout=10)
   except subprocess.TimeoutExpired:child.kill();child.wait()
   row['status']='owned_native_timeout';save();raise
 row['exit_code']=code;row['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest();text=log.read_text()
 assert 'SCRIPT ERROR:' not in text and 'Parse Error' not in text,text[-2000:]
 if name=='import':assert code==0 and 'ERROR:' not in text;row['status']='passed'
 else:
  native=json.loads((captures/'report.json').read_text());assert native['facade_vertex_count']==2744 and native['closed_door_vertex_count']==48;assert len(native['rows'])==15
  report['errors']=native['errors'];report['report_sha256']=hashlib.sha256((captures/'report.json').read_bytes()).hexdigest()
  if args.expect_rejection:assert code==1 and native['status']=='rejected' and native['errors'];row['status']='passed_expected_framing_rejections'
  else:assert code==0 and native['status']=='yihong_framing_passed' and not native['errors'] and 'ERROR:' not in text;row['status']='passed'
 save()
report['status']='completed_expected_rejection' if args.expect_rejection else 'completed_pass';save();print('YIHONG_NATIVE_COMPLETED',args.label,len(report['errors']),'errors',flush=True)
