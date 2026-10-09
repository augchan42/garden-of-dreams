from pathlib import Path
import json,shutil,subprocess,re,hashlib,struct
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root']);f=Path(json.loads(Path('/tmp/garden-ziling-framing.json').read_text())['folder'])/'godot';out=w/'reed-volume-native-review';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
shutil.copyfile('/tmp/garden_reed_volume_physics.gd',f/'tests/test_reed_volume_physics.gd');shutil.copyfile('/tmp/garden_reed_volume_physics.gd',out/'executed-test_reed_volume_physics.gd')
p={'status':'running','source_glb_sha256':sha(f/'assets/garden-of-dreams.glb'),'phases':[]}
def save():(out/'pipeline.json').write_text(json.dumps(p,indent=2)+'\n')
g='/Applications/Godot.app/Contents/MacOS/Godot'
cmds=[('physics',[g,'--headless','--path',str(f),'--script','res://tests/test_reed_volume_physics.gd','--','--output='+str(out/'physics-report.json')],'REED_VOLUME_PHYSICS_PASS'),('flora',[g,'--headless','--path',str(f),'--script','res://tests/test_flora_kit.gd'],'FLORA_RUNTIME_PASS')]
for name,args in [('normal',[]),('touch',['--touch']),('density',['--density'])]:cmds.append((name,[g,'--path',str(f),'--windowed','--resolution','390x844','--script','res://tests/test_reed_volume_framing.gd','--','--output='+str(out/name)]+args,'ZILING_FRAMING_RESULT 10 originals; 0 failures'))
for name,cmd,marker in cmds:
 log=out/(name+'.log')
 with log.open('w') as h:
  try:res=subprocess.run(cmd,stdout=h,stderr=subprocess.STDOUT,timeout=140);code=res.returncode
  except subprocess.TimeoutExpired:code=124
 s=log.read_text();ok=code==0 and marker in s and not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:|Assertion failed)',s,re.M)
 p['phases'].append({'name':name,'command':cmd,'exit_code':code,'log_sha256':sha(log),'status':'passed' if ok else 'failed'});save();print('VOLUME_REVIEW',name,'passed' if ok else 'failed',flush=True)
 if not ok:p['status']='failed';save();print(s[-3500:]);raise SystemExit(1)
 if name in ['normal','touch','density']:
  d=json.loads((out/name/'report.json').read_text());assert not d['errors'] and len(d['rows'])==10
  for row in d['rows']:
   path=Path(row['capture']);assert sha(path)==row['sha256'] and list(struct.unpack('>II',path.read_bytes()[16:24]))==row['pixels']
p['status']='unbaked_geometry_native_physics_flora_and_framing_passed';save();print('VOLUME_NATIVE_REVIEW_PASS',flush=True)
