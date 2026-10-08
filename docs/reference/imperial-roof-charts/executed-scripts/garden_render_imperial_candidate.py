"""Import then compare the exact source/map pair in a separate native engine."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
root=Path(json.loads(Path('/tmp/garden-imperial-roof-probe.json').read_text())['folder'])
f=root/'godot';engine='/Applications/Godot.app/Contents/MacOS/Godot'
phases=[]
def run(name,args,marker=None):
    cmd=[engine,'--path',str(f)]+args
    with (root/(name+'.log')).open('w') as file:
        result=subprocess.run(cmd,stdout=file,stderr=subprocess.STDOUT,timeout=300)
    log=(root/(name+'.log')).read_text()
    errors=re.findall(r'^.*(?:SCRIPT ERROR:|ERROR:|Parse Error:|Assertion failed).*$',log,re.M)
    record={'name':name,'command':cmd,'exit_code':result.returncode,'native_errors':errors,
            'status':'passed' if result.returncode==0 and not errors and (not marker or marker in log) else 'failed'}
    phases.append(record);(root/'native-phases.json').write_text(json.dumps(phases,indent=2)+'\n')
    print(name,record['status'],flush=True)
    assert record['status']=='passed',record
source=root/'export/garden-of-dreams.glb'
record=json.loads((f/'tests/imperial-chart-lightmap.json').read_text())
assert record['source_glb_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert hashlib.sha256((f/'tests/imperial-chart-candidate.glb').read_bytes()).hexdigest()==record['source_glb_sha256']
run('candidate-import',['--headless','--editor','--import'])
old=(f/'lightmaps/SITE_daguan-lou_MAT_rooftile.png.import').read_text()
target=f/'tests/imperial-chart-lightmap.png.import'
text=target.read_text();target.write_text(text.split('[params]')[0]+'[params]'+old.split('[params]')[1])
run('candidate-map-import',['--headless','--editor','--import'])
run('native-comparison',['--script','res://tests/diagnose_imperial_chart_candidate.gd','--','--output='+str(root/'native-captures')],'IMPERIAL_CHART_NATIVE_COMPARISON_PASS')
