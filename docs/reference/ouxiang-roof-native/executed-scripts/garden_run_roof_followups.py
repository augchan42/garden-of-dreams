"""Sequential native follow-ups after the completed full imperial review."""
from pathlib import Path
import json,hashlib,os,shutil,subprocess,sys,re
from datetime import datetime,timezone
repo=Path('/Users/auchan/projects/garden-of-dreams')
review=Path(json.loads(Path('/tmp/garden-imperial-chart-full-review.json').read_text())['folder']).resolve()
source=Path(json.loads(Path('/tmp/garden-imperial-full-source.json').read_text())['folder']).resolve()
root=Path(json.loads(Path('/tmp/garden-oux-native-source.json').read_text())['folder']).resolve()
probe=Path(json.loads(Path('/tmp/garden-oux-roof-probe.json').read_text())['folder']).resolve()
exporter=Path(json.loads(Path('/tmp/garden-imperial-default-export.json').read_text())['folder']).resolve()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
completed=json.loads((review/'review-resume-pipeline.json').read_text())
assert completed['status']=='technical_checks_complete_visual_review_pending' and all(p['status']=='passed' for p in completed['phases'])
try:os.kill(completed['orchestrator_pid'],0)
except ProcessLookupError:pass
else:raise RuntimeError('The preceding native review is still alive')
assert sha(source/'export/garden-of-dreams.glb')==completed['source_glb_sha256']
expected='be80374cbc0959830205af0efbe198f044ec25df15e7933c91178d0ecf516e5a'
assert sha(root/'export/garden-of-dreams.glb')==expected
logs=root/'native-logs';logs.mkdir(exist_ok=False)
report={'status':'running','source_glb_sha256':expected,'baseline_glb_sha256':completed['source_glb_sha256'],'orchestrator_pid':os.getpid(),'started_at':datetime.now(timezone.utc).isoformat(),'phases':[], 'scope':'Default imperial export equality, read-only saved Ouxiang ownership, fresh Ouxiang roof-only bake, matching RGB16 samples and native fixed-clock roof/framing comparisons. No complete Ouxiang lighting, production adoption, final art or device acceptance.'}
def save():(root/'native-phases.json').write_text(json.dumps(report,indent=2)+'\n')
def run(label,command,marker=None):
 phase={'name':label,'command':command,'log':str(logs/(label+'.log')),'status':'running'};report['phases'].append(phase);save();print('ROOF_PHASE_START',label,flush=True)
 with open(phase['log'],'w') as log:
  child=subprocess.Popen(command,cwd=repo,stdout=log,stderr=subprocess.STDOUT);phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 phase['log_sha256']=sha(phase['log']);save();text=Path(phase['log']).read_text(errors='replace')
 assert phase['exit_code']==0,(label,phase['exit_code'],text[-3000:])
 assert not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed|Traceback)',text),(label,text[-3000:])
 if marker:assert marker in text,(label,'missing marker',text[-3000:])
 phase['status']='passed';save();print('ROOF_PHASE_PASS',label,flush=True)
try:
 save();blender='/Applications/Blender.app/Contents/MacOS/Blender';godot='/Applications/Godot.app/Contents/MacOS/Godot'
 run('imperial-default-export',[blender,'--background',str(repo/'blender/authoring.blend'),'--python-exit-code','1','--python',str(exporter/'scripts/export_garden.py'),'--','--output-root',str(exporter)])
 checks={}
 for path in [Path('export/garden-of-dreams.glb'),*[p.relative_to(source) for p in sorted((source/'export/sites').glob('*.glb'))]]:
  assert sha(exporter/path)==sha(source/path),str(path);checks[str(path)]=sha(exporter/path)
 assert len(checks)==16
 report['default_export_equality']=checks;save()
 run('oux-saved-source',[blender,'--background',str(repo/'blender/authoring.blend'),'--python-exit-code','1','--python',str(probe/'garden_inspect_oux_source.py')],'OUX_SOURCE_GEOMETRY_PASS')
 run('oux-roof-bake',[blender,'--background','--threads','8','--python-exit-code','1','--python',str(root/'scripts/bake_lightmaps.py'),'--','--mesh','SITE_ouxiang-xie_MAT_rooftile','--samples','128','--size','1024'])
 run('oux-baked-export-sampling',[sys.executable,str(probe/'garden_diagnose_oux_export.py'),'--source',str(root/'export/garden-of-dreams.glb'),'--maps',str(root/'export/lightmaps'),'--output',str(root/'candidate-component-sampling.json')],'OUX_EXPORT_COMPONENT_DIAGNOSIS')
 gd=root/'godot';shutil.copytree(review/'godot',gd,ignore=shutil.ignore_patterns('.godot','acceptance-captures','captures'))
 name='SITE_ouxiang-xie_MAT_rooftile'
 for src,dst in [(root/'export/garden-of-dreams.glb',gd/'tests/oux-chart-candidate.glb'),(root/'export/lightmaps'/(name+'.png'),gd/'tests/oux-chart-lightmap.png'),(root/'export/lightmaps'/(name+'.json'),gd/'tests/oux-chart-lightmap.json'),(root/'diagnose_oux_chart_candidate.gd',gd/'tests/diagnose_oux_chart_candidate.gd')]:shutil.copy2(src,dst)
 shutil.copy2(gd/'lightmaps'/(name+'.png'),root/'source-control-roof.png')
 report['runtime_inputs_sha256']={str(p.relative_to(gd)):sha(p) for p in sorted(gd.rglob('*')) if p.is_file() and p.suffix in ('.gd','.gdshader','.tscn','.godot')};save()
 head=[godot,'--headless','--path',str(gd)]
 run('oux-comparison-import',head+['--editor','--import'])
 path=gd/'tests/oux-chart-lightmap.png.import';s=path.read_text()
 for key,value in {'compress/mode':'0','process/size_limit':'512','mipmaps/generate':'false'}.items():
  s,count=re.subn(r'^'+re.escape(key)+r'=.*$',key+'='+value,s,flags=re.M);assert count==1
 path.write_text(s)
 run('oux-comparison-lossless-import',head+['--editor','--import'])
 run('oux-native-comparison',[godot,'--path',str(gd),'--script','res://tests/diagnose_oux_chart_candidate.gd','--','--output='+str(root/'native-captures')],'OUX_CHART_NATIVE_COMPARISON_PASS')
 captures=json.loads((root/'native-captures/report.json').read_text())
 assert captures['status']=='passed' and captures['candidate_glb_sha256']==expected and captures['source_glb_sha256']==completed['source_glb_sha256']
 assert len(captures['views'])==4
 for view,row in captures['views'].items():
  assert row['cases']['baseline']['sha256']==row['cases']['baseline-again']['sha256'],view
  for case in row['cases'].values():assert sha(case['path'])==case['sha256']
 report['status']='native_checks_complete_visual_review_pending';report['finished_at']=datetime.now(timezone.utc).isoformat();save();print('ROOF_FOLLOWUPS_TECHNICAL_PASS',root,flush=True)
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
