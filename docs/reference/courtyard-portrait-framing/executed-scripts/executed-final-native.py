from pathlib import Path
import subprocess,json,hashlib,datetime
repo=Path('/Users/auchan/projects/garden-of-dreams');work=Path(__file__).resolve().parent;game=work/'candidate-godot';final=work/'final-native';assert not final.exists();final.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
exe='/Applications/Godot.app/Contents/MacOS/Godot'
old=repo/'.superpowers/sdd/2026-09-23-garden-completion/stage-floor-palette/lit-native-review'
prior=json.loads((repo/'docs/reference/stage-floor-palette/native/review-pipeline.json').read_text())
by_name={row['name']:row for row in prior['phases']}
phases=[]
def add(name,cmd,timeout=300,report=None):phases.append({'name':name,'command':cmd,'timeout':timeout,'native_report':str(report) if report else None})
def graphic(script,args):return [exe,'--path',str(game),'--windowed','--resolution','1410x600','--script','res://tests/'+script,'--',*args]
add('final-import',[exe,'--headless','--path',str(game),'--editor','--import'])
for mode,flags in [('normal',[]),('touch',['--touch']),('density',['--density'])]:
 captures=final/'review-captures'/('yihong-'+mode)
 add('yihong-'+mode,graphic('test_yihong_framing.gd',['--output='+str(captures),*flags]),140,captures/'report.json')
for mode,flags in [('normal',[]),('touch',['--touch','--room=daguan_lou']),('density',['--density','--room=daguan_lou'])]:
 captures=final/'review-captures'/('architecture-'+mode)
 add('architecture-'+mode,graphic('test_portrait_architecture.gd',['--output='+str(captures),*flags]),140,captures/'report.json')
for name in ['native-source-contract','full-lighting','wash-normal','wash-demo','spill-normal','spill-demo','western-supported-route','palette-transfer-normal','palette-transfer-demo','ziling-normal','ziling-touch','ziling-density','adjacent-ouxiang','adjacent-hengwu','adjacent-tubi','adjacent-qiushuang','adjacent-pond','texture-memory-normal','texture-memory-demo','arrivals-desktop','arrivals-portrait','full-tour-desktop','full-tour-portrait']:
 cmd=[arg.replace(str(old/'godot'),str(game)).replace(str(old),str(final)) for arg in by_name[name]['command']]
 add(name,cmd,650 if name.startswith('full-tour-') else 300, final/'review-captures'/('tour-'+name.removeprefix('full-tour-'))/'report.json' if name.startswith('full-tour-') else None)
for name,script in [('entry-route','test_entry_route.gd'),('first-reading-demo','test_first_reading_demo.gd')]:
 add(name,[exe,'--headless','--path',str(game),'--script','res://tests/'+script])
# Run broad UI/route checks before the expensive full tours.
phases=phases[:-4]+phases[-2:]+phases[-4:-2]
inputs={str(p.relative_to(game)):sha(p) for p in sorted(game.rglob('*')) if p.is_file() and '.godot' not in p.parts and not any(part in ['captures','acceptance-captures'] for part in p.parts)}
(final/'frozen-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
report={'status':'running','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_glb_sha256':sha(game/'assets/garden-of-dreams.glb'),'runtime_sha256':sha(game/'runtime/entry_route.gd'),'planned_phases':len(phases),'phases':[],'scope':'One sequential owned Godot child. Final combined two-room cameras, retained source/lighting/palette/adjacent framing, all arrivals and actual public-command physics tours. Protected user editors untouched. No phone/final-art/service acceptance.'}
out=final/'pipeline.json'
def save():out.write_text(json.dumps(report,indent=2)+'\n')
for phase in phases:
 row={**phase,'status':'running','log':str(final/(phase['name']+'.log'))};report['phases'].append(row)
 with Path(row['log']).open('w') as f:
  child=subprocess.Popen(row['command'],stdout=f,stderr=subprocess.STDOUT);row['pid']=child.pid;save()
  try:code=child.wait(timeout=row['timeout'])
  except subprocess.TimeoutExpired:
   child.terminate()
   try:child.wait(timeout=10)
   except subprocess.TimeoutExpired:child.kill();child.wait()
   row['status']='owned_native_timeout';report['status']='failed';save();raise
 row['exit_code']=code;row['log_sha256']=sha(row['log']);text=Path(row['log']).read_text()
 if code or 'ERROR:' in text or 'SCRIPT ERROR:' in text:
  row['status']='failed';report['status']='failed';save();raise AssertionError(text[-3000:])
 if row['native_report']:
  d=json.loads(Path(row['native_report']).read_text());assert d['status'] in ['passed','yihong_framing_passed','portrait_architecture_behavior_passed'];assert not d.get('errors',[]);row['native_report_sha256']=sha(row['native_report'])
  if row['name'].startswith('yihong-'):assert len(d['rows'])==15 and d['facade_vertex_count']==2744 and d['closed_door_vertex_count']==48
  if row['name'].startswith('architecture-'):assert len(d['rows'])==(15 if row['name']=='architecture-normal' else 5)
  if row['name'].startswith('full-tour-'):assert len(d['visited_rooms'])==14 and len(d['legs'])==26 and len(d['captures'])==139 and not d['floor_failures'] and d['maximum_practicals']<=4
 row['status']='passed';save()
for name,digest in inputs.items():assert sha(game/name)==digest,('Fixture changed during review',name)
report['status']='all_native_checks_passed_direct_original_review_and_adoption_pending';report['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('FINAL_COMBINED_NATIVE_PASSED',len(phases),flush=True)
