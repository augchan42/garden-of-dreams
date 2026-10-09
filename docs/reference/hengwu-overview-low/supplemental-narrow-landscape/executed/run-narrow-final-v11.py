"""Run the final small-landscape correction on frozen isolated inputs."""
from pathlib import Path
import hashlib,json,re,subprocess
repo=Path('/Users/auchan/projects/garden-of-dreams');work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-arrival-overview'
root=Path('/tmp/garden-hengwu-arrival-20261010');game=root/'godot';out=root/'narrow-final-v11'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not out.exists();out.mkdir()
frozen={str(p.relative_to(game)):sha(p) for folder in ['runtime','assets','lightmaps','tests'] for p in (game/folder).rglob('*') if p.is_file() and p.suffix!='.uid'}
r={'status':'running','frozen_inputs':frozen,'phases':[],'comparison_to_v6':{},'scope':'Supplemental narrow/short landscape correction. Prior V6 broad tests remain historical; current fixed-clock originals at their covered sizes must reproduce exactly. Not physical device or final art acceptance.'}
def write(): (out/'pipeline.json').write_text(json.dumps(r,indent=2)+'\n')
native=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(game),'--windowed','--resolution','1410x600'];head=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(game),'--headless']
commands=[]
for mode,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
 commands.append(('overview-'+mode,native+['--script','res://tests/test_hengwu_overview.gd','--','--output='+str(out/('overview-'+mode)),*flags],f'HENGWU_OVERVIEW_RESULT {10 if mode=="density" else 35} originals; 0 failures',root/('overview-v6-'+mode)))
for mode,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
 commands.append(('detail-'+mode,native+['--script','res://tests/test_hengwu_detail_framing.gd','--','--output='+str(out/('detail-'+mode)),*flags],'HENGWU_DETAIL_FRAMING_RESULT 10 captures; 0 failures',root/('detail-final-'+mode+'-repeat1')))
commands.append(('visibility',native+['--script','res://tests/test_hengwu_native_visibility.gd','--','--output='+str(out/'visibility')],'HENGWU_NATIVE_VISIBILITY_RESULT 16 originals; 0 failures',root/'native-visibility'))
for mode,flags in [('desktop',[]),('portrait',['--mobile'])]:
 commands.append(('arrivals-'+mode,native+['--script','res://tests/render_entry_route.gd','--','--views-only','--fixed-clock','--output-directory='+str(out/('arrivals-'+mode)),*flags],'ROUTE_RENDER_SAVED',root/'review-captures'/('arrivals-'+mode)))
for name,script,marker in [('entry','test_entry_route.gd','ENTRY_ROUTE_PASS'),('demo','test_first_reading_demo.gd','FIRST_READING_DEMO_PASS'),('surface','test_surface_materials.gd','SURFACE_MATERIAL_PASS')]:commands.append((name,head+['--script','res://tests/'+script],marker,None))
for name,command,marker,old in commands:
 phase={'name':name,'command':command,'marker':marker,'status':'running'};r['phases'].append(phase);write();print('NARROW_FINAL_START',name,flush=True)
 log=out/(name+'.log')
 with log.open('w') as stream:
  child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT);phase['pid']=child.pid;write()
  try:phase['exit_code']=child.wait(timeout=300)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);phase['exit_code']=124
 text=log.read_text(errors='replace');okay=phase['exit_code']==0 and marker in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|Traceback)',text)
 phase.update(status='passed' if okay else 'failed',log_sha256=sha(log));write();assert okay,(name,text[-4000:])
 if old:
  prior=sorted(old.glob('*.png'));assert prior
  for p in prior:
   q=out/name/p.name;assert q.exists() and sha(p)==sha(q),(str(p),str(q));r['comparison_to_v6'][str(q.relative_to(out))]=sha(q)
 print('NARROW_FINAL_PASS',name,flush=True);write()
assert all(sha(game/n)==h for n,h in frozen.items())
assert len(r['comparison_to_v6'])==120
r.update(status='supplemental_native_checks_passed',original_count=len(list(out.rglob('*.png'))),unchanged_original_count=120);write();print('NARROW_FINAL_PASS_ALL',r['original_count'],flush=True)
