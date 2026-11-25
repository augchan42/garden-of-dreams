"""Start one fresh ground lighting job only after the existing roof native pipeline."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, subprocess, sys, time

r = Path(__file__).resolve().parent
roof = Path('/tmp/garden-corridor-roof-full-20261011')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-ready-only', action='store_true')
args = parser.parse_args()

def read(path):
    for attempt in range(3):
        try: return json.loads(path.read_text())
        except json.JSONDecodeError:
            if attempt == 2: raise
            time.sleep(.1)

def assert_ready():
    pipeline = read(roof/'isolated-pipeline.json')
    assert pipeline['status'] == 'isolated_source_native_tours_complete_direct_review_adoption_pending', 'Existing roof source/native/tour pipeline is incomplete; do not start ground lighting'
    assert pipeline['source_glb_sha256'] == '7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b'
    assert [p['name'] for p in pipeline['phases']] == ['native','native-originals','tours','tour-originals']
    assert all(p['status']=='passed' and p['exit_code']==0 for p in pipeline['phases'])
    refresh = read(roof/'export/full-lighting-refresh.json')
    assert refresh['status']=='source_complete' and len(refresh['phases'])==6 and all(p['status']=='passed' and p['exit_code']==0 for p in refresh['phases'])

assert sha(r/'blender/authoring.blend') == '9b6c83259f79aeb56bbdc67b1fd939b2e9ff69977bcb941cb8141b2ce329b66e'
assert sha(r/'export/garden-of-dreams.glb') == '09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290'
libs=read(r/'library-preparation.json')
assert libs['status']=='candidate_source_libraries_passed_fresh_lighting_pending'
for n,d in libs['files'].items(): assert sha(r/n)==d,n
assert read(r/'canonical-replay.json')['status']=='canonical_replay_16_glbs_byte_exact'
assert not (r/'export/full-lighting-refresh.json').exists(), 'Inspect the same lighting job instead of restarting it'
assert not (r/'export/lightmaps').exists() or not any((r/'export/lightmaps').iterdir()), 'Fresh candidate must start with no maps'
if args.check_ready_only:
    assert_ready();print('AOJING_FULL_LIGHTING_PREREQUISITES_PASS');sys.exit(0)

state=r/'resumed-queued-full-lighting.json'
assert read(r/'queued-full-lighting.json')['status']=='failed', 'Original queue must be authoritatively terminal'
assert not state.exists(), 'Inspect the existing resumed queue instead of duplicating it'
existing=read(roof/'isolated-pipeline.json');pid=existing['orchestrator_pid']
command=subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip()
assert str(roof/'resume_isolated_pipeline.py') in command, 'Existing roof pipeline is not live'
report={'status':'waiting_on_existing_roof_source_native_tours','pid':os.getpid(),
        'existing_roof_pipeline_pid':pid,'existing_roof_pipeline_command':command,
        'authoring_sha256':sha(r/'blender/authoring.blend'),'source_glb_sha256':sha(r/'export/garden-of-dreams.glb'),
        'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'One fresh isolated source lighting job after existing roof native/tour checks. No native installation, adoption, editor, device or art acceptance.'}
frozen={str(p.relative_to(r)):sha(p) for folder in ['blender','scripts','export/sites','export/kits'] for p in (r/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.suffix!='.blend1'}
for n in ['export/garden-of-dreams.glb','export/site-wash-rig.json']:frozen[n]=sha(r/n)

def save():
    t=state.with_suffix('.new');t.write_text(json.dumps(report,indent=2)+'\n');t.replace(state)

try:
    save();(r/'full-lighting-inputs.json').write_text(json.dumps({'files':frozen,'empty_lightmaps_before_refresh':True},indent=2)+'\n')
    deadline=time.monotonic()+21600
    while True:
        pipeline=read(roof/'isolated-pipeline.json')
        if pipeline['status']=='isolated_source_native_tours_complete_direct_review_adoption_pending':break
        assert pipeline['status'] in ['waiting_on_existing_source_job','source_complete_isolated_checks_running'], pipeline
        command=subprocess.run(['ps','-p',str(pid),'-o','command='],text=True,capture_output=True)
        if command.returncode!=0 or str(roof/'resume_isolated_pipeline.py') not in command.stdout:
            time.sleep(.2);assert_ready();break
        assert time.monotonic()<deadline, 'Observation deadline; inspect existing roof job without restarting it'
        time.sleep(2)
    assert_ready()
    for n,d in frozen.items():assert sha(r/n)==d,n
    assert not (r/'export/full-lighting-refresh.json').exists()
    (r/'export/lightmaps').mkdir(exist_ok=True);assert not any((r/'export/lightmaps').iterdir())
    report['status']='fresh_ground_source_lighting_running';save()
    log=r/'full-lighting-driver.log'
    with log.open('w') as stream:
        child=subprocess.Popen([sys.executable,str(r/'scripts/refresh_full_lighting.py'),'--samples','128','--size','1024'],cwd=r,stdout=stream,stderr=subprocess.STDOUT)
        report['source_refresh_pid']=child.pid;save();report['source_refresh_exit_code']=child.wait()
    text=log.read_text(errors='replace')
    assert report['source_refresh_exit_code']==0 and 'FULL_SOURCE_LIGHTING_REFRESH_PASS' in text and not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:',text),text[-3000:]
    fresh=read(r/'export/full-lighting-refresh.json')
    assert fresh['status']=='source_complete' and fresh['source_glb_sha256']==report['source_glb_sha256'] and len(fresh['phases'])==6 and all(p['status']=='passed' and p['exit_code']==0 for p in fresh['phases'])
    for n,d in frozen.items():assert sha(r/n)==d,n
    report.update(status='fresh_ground_source_lighting_complete_native_review_pending',log_sha256=sha(log));save();print('AOJING_FRESH_FULL_SOURCE_LIGHTING_PASS',flush=True)
except BaseException as error:
    report.update(status='failed',error=str(error));save();raise
