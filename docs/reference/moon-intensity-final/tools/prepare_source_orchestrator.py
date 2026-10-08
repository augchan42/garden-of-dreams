from pathlib import Path
import hashlib,json,subprocess,sys,shutil,os
repo=Path('/Users/auchan/projects/garden-of-dreams')
pointer=json.loads(Path('/tmp/garden-moon-intensity-final.json').read_text());root=Path(pointer['folder']);old=Path(pointer['preceding']);context=Path(pointer['context'])
shutil.copytree(old/'textures',root/'textures',dirs_exist_ok=True)
report={'status':'running','scope':'Additional separate authored moon correction from actual full-scene intensity sweep. No canonical adoption or fresh final lighting acceptance.','preceding_authoring_sha256':hashlib.sha256((old/'blender/authoring.blend').read_bytes()).hexdigest(),'preceding_export_sha256':hashlib.sha256((old/'export/garden-of-dreams.glb').read_bytes()).hexdigest(),'selected_multiplier':.45,'absolute_target':.2025,'pid':os.getpid(),'phases':[]}
logs=root/'source-preparation-logs';logs.mkdir(exist_ok=True)
p=root/'source-preparation.json'
def save():p.write_text(json.dumps(report,indent=2)+'\n')
def run(name,command):
 phase={'name':name,'command':command,'status':'running','log':str(logs/(name+'.log'))};report['phases'].append(phase);save();print('NEXT_MOON_SOURCE_START',name,flush=True)
 with open(phase['log'],'w') as log:
  process=subprocess.Popen(command,cwd=root,stdout=log,stderr=subprocess.STDOUT);phase['pid']=process.pid;save();phase['exit_code']=process.wait()
 phase['log_sha256']=hashlib.sha256(Path(phase['log']).read_bytes()).hexdigest();phase['status']='passed' if phase['exit_code']==0 else 'failed';save()
 if phase['exit_code']:raise RuntimeError((name,phase['exit_code'],Path(phase['log']).read_text()[-2000:]))
 print('NEXT_MOON_SOURCE_PASS',name,flush=True)
blender='/Applications/Blender.app/Contents/MacOS/Blender'
def native(script,*args,source=None):
 cmd=[blender,'--background']
 if source:cmd.append(str(source))
 return cmd+['--threads','8','--python-exit-code','1','--python',str(script),'--',*map(str,args)]
try:
 run('author',native(context/'scripts/prepare_moon_contrast_candidate.py','--output-root',root,'--multiplier','.45','--evidence',pointer['evidence'],'--reason','Fresh 45% source lighting still clips the moon. Full-scene additional 0.45 linear intensity counterfactual restores brush detail with zero raw interior clipping. Separate 20.25% source requires fresh matching lighting and visual acceptance.',source=old/'blender/authoring.blend'))
 run('reopen-source',native(repo/'scripts/test_moon_contrast_source.py','--root',root,'--expected-target','.2025','--report',root/'source-contract.json'))
 run('export',native(repo/'scripts/export_garden.py','--output-root',root,source=root/'blender/authoring.blend'))
 run('export-preservation',[sys.executable,str(repo/'scripts/verify_moon_contrast_export.py'),'--before-root',str(old),'--candidate-root',str(root),'--report',str(root/'export-preservation.json')])
 run('export-rejections',[sys.executable,str(repo/'scripts/test_moon_contrast_export.py'),'--before',str(old/'export/garden-of-dreams.glb'),'--candidate',str(root/'export/garden-of-dreams.glb'),'--atlas',str(root/'textures/backdrops/moon-paint/atlas.json'),'--report',str(root/'export-rejections.json')])
 # This copied provisional master belongs only to the new scratch tree.
 (root/'blender/master.blend').unlink()
 run('extract-libraries',native(repo/'scripts/prepare_candidate_libraries.py','--root',root))
 run('package-receivers',native(root/'scripts/package_site_washes.py','--portable-master'))
 run('audit-libraries',native(root/'scripts/audit_site_sources.py'))
 for key in ['authoring','export']:
  relative='blender/authoring.blend' if key=='authoring' else 'export/garden-of-dreams.glb';report[key+'_sha256']=hashlib.sha256((root/relative).read_bytes()).hexdigest()
 assert hashlib.sha256((old/'blender/authoring.blend').read_bytes()).hexdigest()==report['preceding_authoring_sha256']
 assert hashlib.sha256((old/'export/garden-of-dreams.glb').read_bytes()).hexdigest()==report['preceding_export_sha256']
 report['status']='source_and_export_prepared_fresh_lighting_pending';save();print('NEXT_MOON_SOURCE_PREPARED',report['export_sha256'],flush=True)
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
