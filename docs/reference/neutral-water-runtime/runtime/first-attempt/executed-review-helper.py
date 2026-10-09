from pathlib import Path
import json,hashlib,subprocess,re,datetime,struct,shutil
r=Path('/Users/auchan/projects/garden-of-dreams');w=r/'.superpowers/sdd/2026-09-23-garden-completion/water-palette-runtime';w.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((r/'.superpowers/sdd/2026-09-23-garden-completion/qiushuang-runtime/source-preservation.json').read_text())
assert sha(r/'blender/authoring.blend')==prior['source']['authoring']
for n in ['export/garden-of-dreams.glb','godot/assets/garden-of-dreams.glb']:assert sha(r/n)==prior['source']['export_glb']
for n,h in prior['source']['lighting_pngs'].items():assert sha(r/n)==h
(w/'source-preservation.json').write_text(json.dumps(prior,indent=2)+'\n')
engine='/Applications/Godot.app/Contents/MacOS/Godot';base=[engine,'--headless','--path',str(r/'godot')];native=[engine,'--path',str(r/'godot'),'--windowed','--resolution','1410x600']
commands=[('cold-import',base+['--editor','--import'],None,100),('source-contract',base+['--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(w/'production-source-contract.json')],'IMPORT_SOURCE_CONTRACT_PASS',60)]
for name,script,marker in [('surface-bindings','test_surface_materials.gd','SURFACE_MATERIAL_PASS'),('reflection-bindings','test_planar_reflection.gd','PLANAR_REFLECTION_PASS'),('reflection-alignment','test_reflection_camera_alignment.gd','REFLECTION_CAMERA_ALIGNMENT_PASS'),('mobile-ui','test_mobile_ui_scaling.gd','MOBILE_UI_SCALE_PASS')]:commands.append((name,base+['--script','res://tests/'+script],marker,90))
commands.extend([('all-room-arrivals',native+['--script','res://tests/render_dynamic_palette.gd','--','--output='+str(w/'all-arrivals')],'DYNAMIC_PALETTE_CAPTURE_RESULT 28 originals',130),('surface-motion',native+['--script','res://tests/render_surfaces.gd','--','--output='+str(w/'surface-motion')],'SURFACE_RENDERS_SAVED',70),('surface-pixels',['python3',str(r/'scripts/verify_surface_animation.py'),'--directory',str(w/'surface-motion'),'--output',str(w/'surface-motion/pixel-validation.json')],'SURFACE_ANIMATION_PASS',60),('reflection-controls',native+['--script','res://tests/render_reflection_validation.gd','--','--output='+str(w/'reflection-controls')],'REFLECTION_CAPTURE_VALIDATION',100),('reflection-pixels',['python3',str(r/'scripts/verify_reflection.py'),'--directory',str(w/'reflection-controls'),'--output',str(w/'reflection-controls/pixel-validation.json')],None,60)])
files=['godot/garden_preview.tscn','godot/materials/water.tres','godot/shaders/pond_reflection.gdshader','godot/runtime/entry_route.gd','godot/tests/render_dynamic_palette.gd','godot/tests/render_surfaces.gd','godot/tests/render_reflection_validation.gd','scripts/verify_surface_animation.py','scripts/verify_reflection.py']
report={'status':'running','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':sha(r/'godot/assets/garden-of-dreams.glb'),'files':{n:sha(r/n) for n in files},'phases':[],'scope':'Installed runtime dynamic palette: source preserved, actual water/fog/reflection bindings, projection and mobile UI invariants, fourteen-room desktop/portrait arrival captures and separate native fixed-clock surface/reflection pixel controls. No new full physics walk or physical-device/final-art acceptance.'}
def save():(w/'review-pipeline.json').write_text(json.dumps(report,indent=2)+'\n')
save()
for name,cmd,marker,timeout in commands:
 log=w/(name+'.log')
 with log.open('w') as f:
  try:code=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout).returncode
  except subprocess.TimeoutExpired:code=1
 text=log.read_text();ok=code==0 and not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:|Assertion failed)',text,re.M) and (marker is None or marker in text)
 report['phases'].append({'name':name,'command':cmd,'exit_code':code,'log':str(log),'log_sha256':sha(log),'status':'passed' if ok else 'failed'});save();print('WATER_PALETTE_REVIEW',name,'passed' if ok else 'failed',flush=True)
 if not ok:report['status']='failed';save();print(text[-5000:]);raise SystemExit(1)
for name,h in report['files'].items():assert sha(r/name)==h,name
for directory in ['all-arrivals','surface-motion','reflection-controls']:
 data=json.loads((w/directory/'report.json').read_text());assert data['source_glb_sha256']==report['source_glb_sha256']
 for row in data['rows']:
  p=Path(row['capture']);assert sha(p)==row['sha256'] and list(struct.unpack('>II',p.read_bytes()[16:24]))==row['pixels']
report['status']='passed';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('WATER_PALETTE_INSTALLED_REVIEW_PASS',flush=True)
