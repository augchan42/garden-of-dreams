from pathlib import Path
import json,hashlib,re,subprocess,sys,shutil
from importlib.machinery import SourceFileLoader
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path('/tmp/garden-memory-caps-20261010');fixture=root/'phone-godot';oldroot=Path('/tmp/garden-full-phone-20261010');godot='/Applications/Godot.app/Contents/MacOS/Godot';apk=root/'garden-memory-full-profile.apk'
sys.path.insert(0,str(repo/'scripts'));from android_texture_provenance import texture_input_snapshot,verify_texture_inputs
caps=SourceFileLoader('caps',str(root/'configure-caps.py')).load_module()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((oldroot/'build-report.json').read_text());assert sha(Path(old['apk']))==old['apk_sha256']
state={'status':'preparing','scope':'Only four runtime size caps in isolated current-source full garden profile. No production adoption.','fixture':str(fixture),'apk':str(apk),'source_glb_sha256':old['source_glb_sha256'],'phases':[]}
def save():(root/'phone-build-report.json').write_text(json.dumps(state,indent=2)+'\n')
save();subprocess.run(['/bin/cp','-cR',str(oldroot/'godot'),str(fixture)],check=True)
manifest=json.loads((fixture/'phone-profile-build.json').read_text());verify_texture_inputs(repo/'godot',manifest['production_texture_inputs'],'Production')
assert sha(fixture/'tests/profile_android.gd')==manifest['profile_script_sha256']==sha(oldroot/'profile_full_garden_android.gd')
assert sha(fixture/'tests/demo_profile_base.gd')==manifest['demo_base_script_sha256']==sha(repo/'godot/tests/profile_android.gd')
state['configuration']=caps.configure(fixture);save()
shutil.copy2(root/'test_memory_caps.gd',fixture/'tests/test_memory_caps.gd')
def run(name,args):
 log=root/(name+'.log');row={'name':name,'status':'running','log':str(log)};state['phases'].append(row);state['status']='running';save()
 with log.open('w') as f:
  child=subprocess.Popen([godot,'--headless','--path',str(fixture),*args],stdout=f,stderr=subprocess.STDOUT);row['pid']=child.pid;save();row['exit_code']=child.wait(timeout=180)
 row['engine_diagnostics']=re.findall(r'^(?:SCRIPT ERROR|ERROR|WARNING):.*$',log.read_text(),re.M);row['log_sha256']=sha(log);row['status']='passed' if row['exit_code']==0 and not row['engine_diagnostics'] else 'failed';save();assert row['status']=='passed',log.read_text()[-4000:];print(name,'passed',flush=True)
run('phone-import',['--editor','--import'])
manifest['staged_texture_inputs']=texture_input_snapshot(fixture)
for path,data in manifest['production_texture_inputs'].items():assert manifest['staged_texture_inputs'][path]['source_sha256']==data['source_sha256']
run('phone-cap-resource-check',['--script','res://tests/test_memory_caps.gd','--','--output='+str(root/'phone-cap-resources.json')])
run('phone-moon-resource-check',['--script','res://tests/test_moon_runtime_import.gd','--','--output='+str(root/'phone-moon-resources.json')])
actual=json.loads((root/'phone-cap-resources.json').read_text());assert actual['status']=='passed' and not actual['errors']
manifest['memory_cap_configuration']=state['configuration'];manifest['memory_cap_resource_check']=actual;manifest['memory_cap_script_sha256']=sha(fixture/'tests/test_memory_caps.gd')
manifest['moon_runtime_import']=json.loads((root/'phone-moon-resources.json').read_text());assert manifest['moon_runtime_import']['status']=='passed'
manifest['inscription_import_sha256']=[sha(fixture/'assets'/('garden-of-dreams_gate-inscription'+suffix+'.png.import')) for suffix in ['', '-normal']]
(fixture/'phone-profile-build.json').write_text(json.dumps(manifest,indent=2)+'\n');state['phone_profile_build_sha256']=sha(fixture/'phone-profile-build.json');save()
run('phone-apk-export',['--export-debug','Android Profile',str(apk)])
verify_texture_inputs(repo/'godot',manifest['production_texture_inputs'],'Production');verify_texture_inputs(fixture,manifest['staged_texture_inputs'],'Staged')
assert sha(fixture/'assets/garden-of-dreams.glb')==old['source_glb_sha256']==sha(repo/'godot/assets/garden-of-dreams.glb')
state.update(status='built',apk_sha256=sha(apk),apk_bytes=apk.stat().st_size);save();print('MEMORY_CAP_FULL_APK_BUILT',state['apk_sha256'],flush=True)
