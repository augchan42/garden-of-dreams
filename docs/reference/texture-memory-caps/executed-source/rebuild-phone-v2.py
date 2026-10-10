from pathlib import Path
import json,shutil,hashlib,subprocess,re
root=Path('/tmp/garden-memory-caps-20261010');fixture=root/'phone-godot';godot='/Applications/Godot.app/Contents/MacOS/Godot';apk=root/'garden-memory-full-profile.apk'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((root/'phone-build-report.json').read_text());state={'status':'preparing','scope':'Four runtime caps plus actual-device resource preflight; timed full-tour producer unchanged.','fixture':str(fixture),'apk':str(apk),'source_glb_sha256':old['source_glb_sha256'],'phases':[]}
def save():(root/'phone-build-report.json').write_text(json.dumps(state,indent=2)+'\n')
save();shutil.copy2(fixture/'tests/profile_android.gd',fixture/'tests/full_profile_base.gd');assert sha(fixture/'tests/full_profile_base.gd')==sha(Path('/tmp/garden-full-phone-20261010/profile_full_garden_android.gd'))
shutil.copy2(root/'profile_with_cap_preflight.gd',fixture/'tests/profile_android.gd')
manifest=json.loads((fixture/'phone-profile-build.json').read_text());manifest.update(profile_script_sha256=sha(fixture/'tests/profile_android.gd'),full_base_script_sha256=sha(fixture/'tests/full_profile_base.gd'))
(fixture/'phone-profile-build.json').write_text(json.dumps(manifest,indent=2)+'\n');state['phone_profile_build_sha256']=sha(fixture/'phone-profile-build.json');save()
for name,args in [('phone-v2-import',['--editor','--import']),('phone-v2-cap-check',['--script','res://tests/test_memory_caps.gd','--','--output='+str(root/'phone-v2-cap-resources.json')]),('phone-v2-export',['--export-debug','Android Profile',str(apk)])]:
 log=root/(name+'.log');row={'name':name,'status':'running','log':str(log)};state['phases'].append(row);state['status']='running';save()
 with log.open('w') as f:
  child=subprocess.Popen([godot,'--headless','--path',str(fixture),*args],stdout=f,stderr=subprocess.STDOUT);row['pid']=child.pid;save();row['exit_code']=child.wait(timeout=180)
 row['engine_diagnostics']=re.findall(r'^(?:SCRIPT ERROR|ERROR|WARNING):.*$',log.read_text(),re.M);row['log_sha256']=sha(log);row['status']='passed' if row['exit_code']==0 and not row['engine_diagnostics'] else 'failed';save();assert row['status']=='passed',log.read_text()[-4000:];print(name,'passed',flush=True)
state.update(status='built',apk_sha256=sha(apk),apk_bytes=apk.stat().st_size);save();print('MEMORY_CAP_PREFLIGHT_APK_BUILT',state['apk_sha256'],flush=True)
