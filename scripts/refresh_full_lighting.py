"""Sequential current-source ordinary/wash bakes; engine installation is separate.

A Sun or shared-fill change requires all eligible meshes to be rebaked. Never
mark old maps compatible after a lighting change. Logs remain outside the repo.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--samples',type=int,default=128)
parser.add_argument('--size',type=int,default=1024)
options=parser.parse_args()
assert options.samples>=128 and options.size>=512
source=ROOT/'export/garden-of-dreams.glb'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
log_root=Path(tempfile.mkdtemp(prefix='garden-full-key-refresh-'))
report_path=ROOT/'export/full-lighting-refresh.json'
report={'status':'running','source_glb_sha256':digest,'samples':options.samples,
        'maximum_source_map_size':options.size,'engine_installed':False,
        'started_at':datetime.now(timezone.utc).isoformat(),'log_root':str(log_root),
        'orchestrator_pid':os.getpid(),'phases':[]}
def save():
    report_path.write_text(json.dumps(report,indent=2)+'\n')
def run(label,command):
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,'Source changed during refresh'
    phase={'name':label,'status':'running','log':str(log_root/(label+'.log'))}
    report['phases'].append(phase);save()
    print('FULL_LIGHTING_PHASE_START',label,flush=True)
    with open(phase['log'],'w') as log:
        process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        phase['pid']=process.pid;save()
        phase['exit_code']=process.wait()
    phase['status']='passed' if phase['exit_code']==0 else 'failed';save()
    if phase['exit_code']:
        report['status']='failed';save()
        print(Path(phase['log']).read_text()[-4000:],flush=True)
        raise RuntimeError((label,phase['exit_code']))
    print('FULL_LIGHTING_PHASE_PASS',label,flush=True)
blender='/Applications/Blender.app/Contents/MacOS/Blender'
native=[blender,'--background','--threads','8','--python-exit-code','1','--python']
try:
    run('ordinary',native+[str(ROOT/'scripts/bake_lightmaps.py'),'--','--site','all',
                           '--samples',str(options.samples),'--size',str(options.size)])
    run('backdrop-wash',native+[str(ROOT/'scripts/bake_backdrop_wash.py'),'--',
                               '--samples',str(options.samples),'--size','512'])
    run('native-pixels',native+[str(ROOT/'scripts/inspect_lightmap_pixels.py')])
    run('coverage',[sys.executable,str(ROOT/'scripts/verify_lightmaps.py'),'--current','--require-all'])
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    coverage=json.loads((ROOT/'export/lightmaps-coverage.json').read_text())
    assert coverage['expected_meshes']==coverage['baked_meshes']==124 and not coverage['missing']
    report['status']='source_complete';report['coverage']=coverage
    report['finished_at']=datetime.now(timezone.utc).isoformat();save()
    print('FULL_SOURCE_LIGHTING_REFRESH_PASS',digest,'124 ordinary maps plus native wash',flush=True)
except BaseException as error:
    report['status']='failed';report['error']=str(error);save()
    raise
