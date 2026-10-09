"""Execute the remaining focused native modes on frozen fixture inputs."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-arrival-overview'
root=Path('/tmp/garden-hengwu-arrival-20261010');game=root/'godot'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (root/'focused-pipeline-v2.json').exists()
first=json.loads((root/'overview-v1-normal/report.json').read_text())
assert first['status']=='hengwu_overview_passed' and not first['errors']
assert first['status']=='hengwu_overview_passed'
shutil.copyfile(work/'detail-regression-candidate.gd',game/'tests/test_hengwu_detail_framing.gd')
frozen={str(p.relative_to(game)):sha(p) for folder in ['runtime','assets','lightmaps','tests'] for p in (game/folder).rglob('*') if p.is_file() and p.suffix!='.uid'}
report={'status':'running','frozen_inputs':frozen,'phases':[],'first_normal_report_sha256':sha(root/'overview-v1-normal/report.json')}
godot='/Applications/Godot.app/Contents/MacOS/Godot'
native=[godot,'--path',str(game),'--windowed','--resolution','1410x600']
commands=[]
for mode,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
    commands.append(('overview-'+mode,native+['--script','res://tests/test_hengwu_overview.gd','--','--output='+str(root/('overview-v2-'+mode)),*flags],'HENGWU_OVERVIEW_RESULT 10 originals; 0 failures'))
for mode,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
    commands.append(('detail-'+mode,native+['--script','res://tests/test_hengwu_detail_framing.gd','--','--output='+str(root/('detail-v2-'+mode)),*flags],'HENGWU_DETAIL_FRAMING_RESULT 10 captures; 0 failures'))
for name,command,marker in commands:
    print('HENGWU_FOCUSED_START',name,flush=True)
    log=root/(name+'.log');phase={'name':name,'command':command,'status':'running','log':str(log)};report['phases'].append(phase)
    (root/'focused-pipeline-v2.json').write_text(json.dumps(report,indent=2)+'\n')
    with log.open('w') as stream:
        child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid
        (root/'focused-pipeline-v2.json').write_text(json.dumps(report,indent=2)+'\n')
        try:phase['exit_code']=child.wait(timeout=300)
        except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);phase['exit_code']=124
    text=log.read_text(errors='replace')
    okay=phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|Traceback)',text)
    phase.update(status='passed' if okay else 'failed',log_sha256=sha(log))
    (root/'focused-pipeline-v2.json').write_text(json.dumps(report,indent=2)+'\n')
    assert okay,(name,text[-2500:])
    print('HENGWU_FOCUSED_PASS',name,flush=True)
assert all(sha(game/name)==digest for name,digest in frozen.items()),'Fixture inputs changed during focused review'
assert sha(repo/'godot/runtime/entry_route.gd')=='7970380d11f8eb59530602e391565f355a844a94e9aa16a369d260a86a434a05'
report['status']='focused_native_modes_passed_original_review_pending'
(root/'focused-pipeline-v2.json').write_text(json.dumps(report,indent=2)+'\n')
