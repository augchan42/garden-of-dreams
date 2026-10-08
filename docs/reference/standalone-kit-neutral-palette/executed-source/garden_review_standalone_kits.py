import datetime,json,subprocess,sys
from pathlib import Path
c=json.loads(Path('/tmp/garden-kit-neutral-palette.json').read_text());work=Path(c['work']);project=work/'godot';out=work/'native-checks';out.mkdir()
godot='/Applications/Godot.app/Contents/MacOS/Godot'
commands=[('cold-import',[godot,'--headless','--path',str(project),'--editor','--import'],0)]
for kit in ('pavilion','corridor','wall','rockery'):
 commands.append(('pbr-'+kit,[godot,'--headless','--path',str(project),'--script','res://tests/test_pavilion_atlas.gd','--']+([] if kit=='pavilion' else ['--'+kit]),0))
 commands.append(('physics-'+kit,[godot,'--headless','--path',str(project),'--fixed-fps','60','--script','res://tests/test_'+kit+'_kit.gd'],0))
commands.append(('corrupt-palette',[godot,'--path',str(project),'--windowed','--resolution','390x844','--script','res://tests/test_standalone_kit_palette.gd','--','--corrupt-color','--output='+str(work/'rejected-palette')],1))
report={'status':'running','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':[]}
for name,args,wanted in commands:
 print('START',name,flush=True)
 log=out/(name+'.log')
 with log.open('w') as file:run=subprocess.run(args,stdout=file,stderr=subprocess.STDOUT,timeout=900)
 text=log.read_text()
 if name=='corrupt-palette':assert 'Atlas swatch differs' in text, text[-4000:]
 if name=='cold-import':assert 'SCRIPT ERROR' not in text and 'ERROR:' not in text, text[-4000:]
 phase={'name':name,'command':args,'exit_code':run.returncode,'expected_exit_code':wanted,'log':str(log)};report['phases'].append(phase)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if run.returncode!=wanted:print('FAIL',name,text[-5000:],flush=True);sys.exit(1)
 print('PASS',name,flush=True)
report['status']='ten_native_kit_phases_passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('STANDALONE_KITS_NATIVE_REVIEW_PASS',len(commands),flush=True)
