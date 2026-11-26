"""Install the reviewed runtime/tests reversibly and prove exact native reproduction."""
from pathlib import Path
import hashlib,json,os,re,shutil,struct,subprocess
repo=Path('/Users/auchan/projects/garden-of-dreams');work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-arrival-overview'
root=Path('/tmp/garden-hengwu-arrival-20261010');game=root/'godot';adoption=work/'adoption';backup=adoption/'backup'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
assert not adoption.exists()
assert load(work/'pre-adoption-validation.json')['status']=='candidate_ready_for_installed_verification'
broad=load(root/'broad-pipeline.json');fixed=load(root/'fixed-detail-pipeline.json')
assert broad['status']=='broad_native_checks_passed_direct_original_review_pending' and len(broad['phases'])==30 and all(p['status']=='passed' for p in broad['phases'])
assert fixed['status']=='fixed_detail_modes_passed_thirty_originals_reproduced_exactly'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()=='38324b66111ae69df72290fe3eae31593f435fbe'
assert subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()=='codex/hengwu-overview-low'
assert sha(repo/'godot/runtime/entry_route.gd')=='7970380d11f8eb59530602e391565f355a844a94e9aa16a369d260a86a434a05'
assert sha(repo/'blender/authoring.blend')=='7eba169a1252dcad46aff5ad76906e4ce75ab009103fb98e586cc0c367897b8a'
for name,digest in broad['frozen_inputs'].items():
 if name=='tests/test_hengwu_detail_framing.gd':continue
 assert sha(game/name)==digest,name
for name,digest in fixed['frozen_inputs'].items():assert sha(game/name)==digest,name
for name,digest in broad['frozen_inputs'].items():
 if name.startswith(('assets/','lightmaps/','runtime/')) and name!='runtime/entry_route.gd':assert sha(repo/'godot'/name)==digest,name
files=['runtime/entry_route.gd','tests/test_hengwu_overview.gd','tests/test_hengwu_detail_framing.gd','tests/test_hengwu_native_visibility.gd','tests/hengwu-arrival-contract.json','tests/hengwu-visibility-probes.json']
uid_targets=[str(Path(p).with_suffix('.gd.uid')) for p in files if p.endswith('.gd')]
adoption.mkdir();backup.mkdir();items=[]
for name in files+uid_targets:
 p=repo/'godot'/name;saved=backup/name;saved.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():shutil.copyfile(p,saved)
 items.append({'name':name,'before_sha256':sha(p) if p.exists() else None,'candidate_sha256':sha(game/name) if (game/name).exists() else None})
report={'status':'applying','items':items,'checks':[],'fixture_runtime_sha256':sha(game/'runtime/entry_route.gd'),'broad_report_sha256':sha(root/'broad-pipeline.json'),'fixed_detail_report_sha256':sha(root/'fixed-detail-pipeline.json')};write(adoption/'application.json',report)
try:
 for name in files:
  destination=repo/'godot'/name;temporary=destination.with_name(destination.name+'.hengwu-staged');shutil.copyfile(game/name,temporary);os.replace(temporary,destination)
 native=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(repo/'godot'),'--windowed','--resolution','1410x600']
 head=['/Applications/Godot.app/Contents/MacOS/Godot','--headless','--path',str(repo/'godot')]
 commands=[('installed-import',head+['--editor','--import'],'Godot Engine')]
 markers={'native-source-contract':'IMPORT_SOURCE_CONTRACT_PASS','full-lighting':'FULL_SCENE_LIGHTING_PASS','wash-normal':'BAKED_BACKDROP_WASH_PASS','wash-demo':'BAKED_BACKDROP_WASH_PASS','spill-normal':'TERMINAL_SPILL_PASS','spill-demo':'TERMINAL_SPILL_PASS','western-supported-route':'WESTERN_ROUTE_PASS'}
 for phase in broad['phases']:
  if phase['name'] in markers:
   command=[a.replace(str(root),str(repo)) for a in phase['command']]
   if phase['name']=='native-source-contract':command[-1]=str(adoption/'installed-import-contract.json')
   commands.append(('installed-'+phase['name'],command,markers[phase['name']]))
 comparison=[]
 for mode,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
  name='installed-overview-'+mode;folder=adoption/name
  commands.append((name,native+['--script','res://tests/test_hengwu_overview.gd','--','--output='+str(folder),*flags],('HENGWU_OVERVIEW_RESULT 10 originals; 0 failures' if mode=='density' else 'HENGWU_OVERVIEW_RESULT 18 originals; 0 failures')));comparison.append((root/('overview-v6-'+mode),folder))
  name='installed-detail-'+mode;folder=adoption/name
  commands.append((name,native+['--script','res://tests/test_hengwu_detail_framing.gd','--','--output='+str(folder),*flags],'HENGWU_DETAIL_FRAMING_RESULT 10 captures; 0 failures'));comparison.append((root/f'detail-final-{mode}-repeat1',folder))
 name='installed-native-visibility';folder=adoption/name
 commands.append((name,native+['--script','res://tests/test_hengwu_native_visibility.gd','--','--output='+str(folder)],'HENGWU_NATIVE_VISIBILITY_RESULT 16 originals; 0 failures'));comparison.append((root/'native-visibility',folder))
 for name,script,source,marker in [('yihong','test_yihong_framing.gd','yihong-normal','YIHONG_FRAMING_RESULT'),('architecture','test_portrait_architecture.gd','architecture-normal','PORTRAIT_ARCHITECTURE_RESULT')]:
  folder=adoption/('installed-'+name);commands.append(('installed-'+name,native+['--script','res://tests/'+script,'--','--output='+str(folder)],marker));comparison.append((root/'review-captures'/source,folder))
 for mode,flags in [('desktop',[]),('portrait',['--mobile'])]:
  folder=adoption/('installed-arrivals-'+mode);commands.append(('installed-arrivals-'+mode,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--fixed-clock','--output-directory='+str(folder),*flags],'ROUTE_RENDER_SAVED'));comparison.append((root/'review-captures'/('arrivals-'+mode),folder))
 for name,script,marker in [('entry-route','test_entry_route.gd','ENTRY_ROUTE_PASS'),('first-reading-demo','test_first_reading_demo.gd','FIRST_READING_DEMO_PASS'),('surface-materials','test_surface_materials.gd','SURFACE_MATERIAL_PASS')]:commands.append(('installed-'+name,head+['--script','res://tests/'+script],marker))
 for mode,flags in [('normal',[]),('demo',['--demo'])]:commands.append(('installed-texture-memory-'+mode,native+['--script','res://tests/audit_runtime_textures.gd','--','--output='+str(adoption/('installed-texture-memory-'+mode+'.json')),*flags],'RUNTIME_TEXTURE_INVENTORY_PASS'))
 assert len(commands)==24
 for name,command,marker in commands:
  print('HENGWU_INSTALLED_START',name,flush=True);log=adoption/(name+'.log');phase={'name':name,'command':command,'log':str(log),'status':'running'};report['checks'].append(phase)
  with log.open('w') as stream:
   child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid;write(adoption/'application.json',report)
   try:phase['exit_code']=child.wait(timeout=300)
   except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);phase['exit_code']=124
  text=log.read_text(errors='replace');okay=phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|Traceback)',text)
  phase.update(status='passed' if okay else 'failed',log_sha256=sha(log));write(adoption/'application.json',report);assert okay,(name,text[-3000:]);print('HENGWU_INSTALLED_PASS',name,flush=True)
 equality={}
 for original,current in comparison:
  originals=sorted(original.glob('*.png'));copies=sorted(current.glob('*.png'));assert len(originals)==len(copies)>0,(str(original),len(originals),len(copies))
  for p in originals:
   q=current/p.name;assert sha(p)==sha(q),(str(p),str(q))
   assert struct.unpack('>II',p.read_bytes()[16:24])==struct.unpack('>II',q.read_bytes()[16:24])
   equality[str(q.relative_to(adoption))]=sha(q)
  for p in [original/'report.json',current/'report.json']:
   if p.exists():assert not load(p)['errors'],str(p)
 for item in items:
  if item['name'] in files:assert sha(repo/'godot'/item['name'])==item['candidate_sha256']
 for name,digest in broad['frozen_inputs'].items():
  if name.startswith(('assets/','lightmaps/','runtime/')) and name!='runtime/entry_route.gd':assert sha(repo/'godot'/name)==digest,name
 assert sha(repo/'blender/authoring.blend')=='7eba169a1252dcad46aff5ad76906e4ce75ab009103fb98e586cc0c367897b8a'
 report.update(status='working_hengwu_overview_adopted_installed_checks_passed',installed_originals_byte_exact=equality,installed_original_count=len(equality),installed_runtime_sha256=sha(repo/'godot/runtime/entry_route.gd'));write(adoption/'application.json',report);print('HENGWU_INSTALLED_REPRODUCTION_PASS',len(equality),'exact_originals',flush=True)
except BaseException as error:
 for item in reversed(items):
  name=item['name'];p=repo/'godot'/name;saved=backup/name
  if saved.exists():shutil.copyfile(saved,p)
  elif p.exists():p.unlink()
 report.update(status='installation_rolled_back',error=repr(error));write(adoption/'application.json',report)
 assert sha(repo/'godot/runtime/entry_route.gd')=='7970380d11f8eb59530602e391565f355a844a94e9aa16a369d260a86a434a05'
 raise
