"""Apply the tested supplemental runtime/test pair with rollback and native reproduction."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
repo=Path('/Users/auchan/projects/garden-of-dreams');work=repo/'.superpowers/sdd/2026-09-23-garden-completion/hengwu-arrival-overview'
root=Path('/tmp/garden-hengwu-arrival-20261010');game=root/'godot';review=root/'narrow-final';out=work/'adoption-narrow';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not out.exists();proof=json.loads((review/'pipeline.json').read_text());assert proof['status']=='supplemental_native_checks_passed' and len(proof['phases'])==12 and proof['original_count']==154 and proof['unchanged_original_count']==120
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()=='b07a64cde9bcb52886713a4a745033667541a565'
assert subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()=='codex/hengwu-overview-low'
assert sha(repo/'godot/runtime/entry_route.gd')=='56813eb7405d428209b268bec5365e670a33701fea22afbddfd159c3434281a8'
assert sha(repo/'blender/authoring.blend')=='7eba169a1252dcad46aff5ad76906e4ce75ab009103fb98e586cc0c367897b8a'
assert sha(repo/'godot/assets/garden-of-dreams.glb')=='ba40866e18f9ab3dcb0263855020099b7eedce70243c6a37e4d50c5f74c0e4f2'
assert all(sha(game/n)==h for n,h in proof['frozen_inputs'].items())
files=['runtime/entry_route.gd','tests/test_hengwu_overview.gd'];unchanged={}
for folder in ['runtime','assets','lightmaps']:
 for p in (repo/'godot'/folder).rglob('*'):
  if p.is_file() and p.suffix!='.uid' and str(p.relative_to(repo/'godot')) not in files:
   name=str(p.relative_to(repo/'godot'));unchanged[name]=sha(p);assert sha(game/name)==unchanged[name],name
out.mkdir();items=[]
for name in files:
 saved=out/'backup'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/'godot'/name,saved);items.append({'name':name,'before_sha256':sha(saved),'candidate_sha256':sha(game/name)})
r={'status':'applying','items':items,'unchanged_inputs':unchanged,'checks':[],'review_pipeline_sha256':sha(review/'pipeline.json')}
def write(): (out/'application.json').write_text(json.dumps(r,indent=2)+'\n')
write()
try:
 for name in files:
  p=repo/'godot'/name;t=p.with_name(p.name+'.narrow-staged');shutil.copyfile(game/name,t);os.replace(t,p)
 for phase in proof['phases']:
  name=phase['name'];command=[a.replace(str(game),str(repo/'godot')).replace(str(review),str(out)) for a in phase['command']];check={'name':name,'command':command,'status':'running'};r['checks'].append(check);write();print('NARROW_INSTALLED_START',name,flush=True)
  log=out/(name+'.log')
  with log.open('w') as stream:
   child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT);check['pid']=child.pid;write()
   try:check['exit_code']=child.wait(timeout=300)
   except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);check['exit_code']=124
  text=log.read_text(errors='replace');okay=check['exit_code']==0 and phase['marker'] in text and not re.search(r'(?m)^(SCRIPT ERROR:|ERROR:|.*Parse Error:|Traceback)',text);check.update(status='passed' if okay else 'failed',log_sha256=sha(log));write();assert okay,(name,text[-3000:]);print('NARROW_INSTALLED_PASS',name,flush=True)
 equality={}
 for p in sorted(review.rglob('*.png')):
  q=out/p.relative_to(review);assert q.exists() and sha(p)==sha(q),(str(p),str(q));equality[str(q.relative_to(out))]=sha(q)
 assert len(equality)==154
 assert all(sha(repo/'godot'/n)==h for n,h in unchanged.items())
 assert all(sha(repo/'godot'/i['name'])==i['candidate_sha256'] for i in items)
 assert sha(repo/'blender/authoring.blend')=='7eba169a1252dcad46aff5ad76906e4ce75ab009103fb98e586cc0c367897b8a'
 r.update(status='supplemental_installed_checks_passed',installed_original_count=154,installed_originals_byte_exact=equality,installed_runtime_sha256=sha(repo/'godot/runtime/entry_route.gd'));write();print('NARROW_INSTALLED_REPRODUCTION_PASS 154',flush=True)
except BaseException as error:
 for item in items:shutil.copyfile(out/'backup'/item['name'],repo/'godot'/item['name'])
 r.update(status='rolled_back',error=repr(error));write();raise
