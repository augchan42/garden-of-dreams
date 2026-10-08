from pathlib import Path
import json,subprocess,hashlib
repo=Path('/Users/auchan/projects/garden-of-dreams');work=Path(json.loads(Path('/tmp/garden-hengwu-compact-rock.json').read_text())['root']).resolve();project=work/'godot';out=work/'native-physics-review';out.mkdir();preview=project/'garden_preview.tscn';before=preview.read_text();preview.write_text(before.replace('res://assets/garden-of-dreams.glb','res://assets/garden-hengwu-candidate.glb'))
phases=[];inputs={}
for name in ['test_courtyard_route','test_farmhouse_route']:
 original=repo/'godot/tests'/(name+'.gd');p=out/(name+'.gd');p.write_text(original.read_text().replace(' root.add_child(route)',' route.site_bakes_enabled=false\n root.add_child(route)'));inputs[str(p)]={'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'executed_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'only_change':'Disable site bakes before scene initialization; candidate has no fresh lighting yet.'}
commands=[(name,str(out/(name+'.gd'))) for name in ['test_courtyard_route','test_farmhouse_route']]+[('compact-rock-collider','/tmp/garden_test_hengwu_compact_collider.gd')]
for name,script in commands:
 args=['/Applications/Godot.app/Contents/MacOS/Godot','--headless','--path',str(project),'--fixed-fps','60','--script',script]
 with (out/(name+'.log')).open('w') as f:run=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=900)
 phases.append({'name':name,'command':args,'exit_code':run.returncode,'script_sha256':hashlib.sha256(Path(script).read_bytes()).hexdigest()});assert run.returncode==0,(name,(out/(name+'.log')).read_text())
preview.write_text(before);(out/'report.json').write_text(json.dumps({'status':'native_compact_collider_and_adjacent_route_checks_passed','phases':phases,'adapted_inputs':inputs,'scope':'Actual imported compact-rock collider bounds/blocking and courtyard/farmhouse bidirectional physics. Site bakes disabled only; lighting and complete garden walk remain separate.'},indent=2)+'\n');print('HENGWU_COMPACT_PHYSICS_REVIEW_PASS')
