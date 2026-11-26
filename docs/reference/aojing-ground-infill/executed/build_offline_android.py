"""Build and verify a current full diagnostic APK after installed acceptance; no device calls."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path('/private/tmp/garden-aojing-ground-v2-20261011')
expected='09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
installed=root/'installed-validation.json'
if not installed.exists() or json.loads(installed.read_text()).get('status')!='installed_canonical_source_and_engine_checks_passed':raise RuntimeError('Installed ground candidate not accepted; no Android build started')
data=json.loads(installed.read_text());assert data['source_glb_sha256']==expected and data['installed_originals_exact_to_candidate']==14
assert len(data['phases'])==24 and all(p['status']=='passed' and p['exit_code']==0 for p in data['phases'])
assert {p['name'] for p in data['phases']}=={'ground_source','canvas_palette','ground_geometry','stage_kit','native_ground','saved_key','saved_rays','canonical_source','site_sources','uv2','roof_source_uv','sync_full_lightmaps','sync_backdrop_wash','sync_terminal_spill','sync_lightmaps','import_contract','native_import','roof_uv','full_scene','wash','spill','runtime_caps','cold_reimport','native_roof'}
assert data['installed_ground_originals_exact_to_candidate']==8 and data['protected_stage_and_runtime_files_unchanged']==499
assert sha(repo/'export/garden-of-dreams.glb')==sha(repo/'godot/assets/garden-of-dreams.glb')==expected
assert sha(repo/'godot/runtime/entry_route.gd')=='ec42ec55bf382ec314b6da325da741d214d297d81418d4da38bdabe0d017ec87'
assert not (root/'offline-android-jobs.json').exists(),'Resume the recorded job; do not duplicate exports'
report={'status':'running','pid':os.getpid(),'source_glb_sha256':expected,'phases':[],'scope':'Full diagnostic Android export and actual offline packaged-payload/provenance checks. No ADB, installation, device/release or performance acceptance.'}
def save():(root/'offline-android-jobs.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,command,marker,timeout):
 log=root/(name+'.log');phase={'name':name,'status':'running','command':command,'log':str(log)};report['phases'].append(phase);save()
 with log.open('w') as f:
  child=subprocess.Popen(command,cwd=repo,stdout=f,stderr=subprocess.STDOUT);phase['pid']=child.pid;save()
  try:phase['exit_code']=child.wait(timeout=timeout)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=15);phase['status']='timeout';save();raise
 text=log.read_text(errors='replace');assert phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(ERROR:|SCRIPT ERROR:|Traceback)|AssertionError:',text),text[-4000:]
 phase.update(status='passed',log_sha256=sha(log));save()
try:
 save()
 run('android-full-build',[sys.executable,str(repo/'scripts/build_android_profile.py'),'--mode','full','--apk',str(root/'garden-aojing-ground-full.apk'),'--report',str(root/'android-full-build.json')],'ANDROID_PROFILE_APK_BUILT',1200)
 build=json.loads((root/'android-full-build.json').read_text());assert build['status']=='built' and build['source_glb_sha256']==expected and build['profile_mode']=='full' and build['device_tested'] is False
 assert sha(Path(build['apk']))==build['apk_sha256']
 run('android-payload-verification',[sys.executable,str(root/'verify_android_artifact.py'),'--project',str(repo),'--build',str(root/'android-full-build.json'),'--output',str(root/'android-payload-verification.json')],'OFFLINE_APK_PREFLIGHT_PASS',180)
 proof=json.loads((root/'android-payload-verification.json').read_text());assert proof['status']=='offline_preflight_and_packaged_payloads_passed' and proof['apk_sha256']==build['apk_sha256']
 report.update(status='full_offline_apk_verified_uninstalled',apk_sha256=build['apk_sha256'],apk_bytes=build['apk_bytes']);save();print('AOJING_GROUND_OFFLINE_ANDROID_PASS',flush=True)
except BaseException as error:report.update(status='failed',error=str(error));save();raise
