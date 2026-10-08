import json,subprocess
from pathlib import Path
work=Path(json.loads(Path('/tmp/garden-hengwu-compact-rock.json').read_text())['root']).resolve();project=work/'godot';godot='/Applications/Godot.app/Contents/MacOS/Godot';out=work/'native-geometry-review-corrected';out.mkdir();phases=[]
commands=[('cold-import',[godot,'--headless','--path',str(project),'--editor','--import'])]
preview=project/'garden_preview.tscn';before=preview.read_text()
for name,args in commands:
 with (out/(name+'.log')).open('w') as f:run=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=900)
 phases.append({'name':name,'command':args,'exit_code':run.returncode});assert run.returncode==0,(name,run.returncode)
 assert 'ERROR:' not in (out/(name+'.log')).read_text();assert 'UID duplicate' not in (out/(name+'.log')).read_text()
for variant in ['baseline','candidate']:
 preview.write_text(before if variant=='baseline' else before.replace('res://assets/garden-of-dreams.glb','res://assets/garden-hengwu-candidate.glb'))
 args=[godot,'--path',str(project),'--windowed','--resolution','1410x600','--fixed-fps','60','--script','/tmp/garden_render_hengwu_rock_candidate.gd','--','--variant='+variant,'--output='+str(out)]
 with (out/(variant+'.log')).open('w') as f:run=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=900)
 phases.append({'name':variant,'command':args,'exit_code':run.returncode});assert run.returncode==0,(variant,run.returncode)
preview.write_text(before)
(out/'report.json').write_text(json.dumps({'status':'unbaked_native_comparison_phases_passed','phases':phases},indent=2)+'\n');print('HENGWU_NATIVE_GEOMETRY_REVIEW_PASS',out)
