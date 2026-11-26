"""Run only owned isolated native workers and retain every phase log."""
import subprocess,json,time,hashlib,re,shutil
from pathlib import Path
repo=Path('/Users/auchan/projects/garden-of-dreams')
work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-arrival-overview'
root=Path('/tmp/garden-hengwu-arrival-20261010')
game=root/'godot'
output=root/'comparisons'
assert (game/'tests/hengwu-arrival-subjects.json').exists()
shutil.copyfile(work/'compare-arrivals.gd',game/'tests/compare_hengwu_arrivals.gd')
godot='/Applications/Godot.app/Contents/MacOS/Godot'
report={'status':'running','phases':[],'production_changed':False,'protected_editor_pids':[43873,55899]}
commands=[('import',[godot,'--headless','--path',str(game),'--editor','--import']),
          ('original-comparison',[godot,'--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/compare_hengwu_arrivals.gd','--','--output='+str(output)])]
for name,command in commands:
    print('HENGWU_COMPARISON_START',name,flush=True)
    log=root/(name+'.log')
    phase={'name':name,'command':command,'log':str(log),'status':'running'}
    report['phases'].append(phase)
    (root/'pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
    with log.open('w') as stream:
        child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT)
        phase['pid']=child.pid
        (root/'pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
        try:phase['exit_code']=child.wait(timeout=300)
        except subprocess.TimeoutExpired:
            child.terminate();child.wait(timeout=30);phase['exit_code']=124
    text=log.read_text(errors='replace')
    okay=phase['exit_code']==0 and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|Traceback)',text)
    if name=='original-comparison':okay=okay and 'HENGWU_COMPARISON_RESULT 24 originals; 0 failures' in text
    phase.update(status='passed' if okay else 'failed',log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
    (root/'pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
    assert okay,(name,text[-2500:])
    print('HENGWU_COMPARISON_PASS',name,flush=True)
report['status']='native_originals_captured_direct_review_pending'
(root/'pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
