import datetime,json,subprocess,sys
from pathlib import Path
root=Path('/Users/auchan/projects/garden-of-dreams');out=Path('/tmp/garden-portrait-architecture-review');out.mkdir(exist_ok=False);godot='/Applications/Godot.app/Contents/MacOS/Godot';project=str(root/'godot')
commands=[]
for name in ('test_entry_route','test_farmhouse_route','test_imperial_route','test_nunnery_route','test_mobile_ui_scaling'):
 commands.append((name,[godot,'--headless','--path',project,'--fixed-fps','60','--script','res://tests/'+name+'.gd']))
for name in ('test_pavilion_portrait_framing','test_pond_view'):
 commands.append((name,[godot,'--path',project,'--windowed','--resolution','390x844','--fixed-fps','60','--script','res://tests/'+name+'.gd']))
for mode in ('desktop','portrait'):
 captures=out/('tour-'+mode);captures.mkdir();args=[godot,'--path',project,'--windowed','--resolution','390x844' if mode=='portrait' else '1410x600','--script','res://tests/render_full_garden_traversal.gd','--','--output='+str(out/(mode+'-tour.json')),'--capture-directory='+str(captures),'--diagnose-floor']
 if mode=='portrait':args.append('--portrait')
 commands.append(('full-rendered-tour-'+mode,args))
report={'status':'running','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phases':[]}
for name,args in commands:
 print('START',name,flush=True);log=out/(name+'.log')
 with log.open('w') as file:run=subprocess.run(args,stdout=file,stderr=subprocess.STDOUT,timeout=1800)
 row={'name':name,'command':args,'exit_code':run.returncode,'log':str(log)};report['phases'].append(row);(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if run.returncode!=0:print('FAIL',name,log.read_text()[-6000:],flush=True);sys.exit(1)
 print('PASS',name,flush=True)
report['status']='seven_regressions_and_both_full_native_tours_passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PORTRAIT_ARCHITECTURE_REGRESSIONS_PASS',len(commands),flush=True)
