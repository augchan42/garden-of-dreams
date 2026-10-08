import subprocess,json,hashlib,re
from pathlib import Path
root=Path('/Users/auchan/projects/garden-of-dreams');godot='/Applications/Godot.app/Contents/MacOS/Godot';folder=root/'docs/reference/moon-paint/current-garden';folder.mkdir(parents=True,exist_ok=True)
report={'status':'running','source_glb_sha256':hashlib.sha256((root/'godot/assets/garden-of-dreams.glb').read_bytes()).hexdigest(),'scope':'Actual installed painted-moon source and fresh lighting runtime checks, isolated native paint transfer and desktop/portrait arrival captures. Known physical floor seams remain; not final full-garden continuous art/device/performance/release acceptance.','phases':[]}
report_path=root/'export/moon-paint-current-runtime.json'
def save():report_path.write_text(json.dumps(report,indent=2)+'\n')
def run(label,script,native=False,args=[]):
 phase={'name':label,'status':'running','log':str(folder/(label+'.log'))};report['phases'].append(phase);save()
 cmd=[godot]+([] if native else ['--headless'])+(['--fixed-fps','60'] if script=='test_entry_route' else [])+['--path',str(root/'godot'),'--script','res://tests/'+script+'.gd']
 if args:cmd+=['--',*args]
 with open(phase['log'],'w') as log:
  child=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT);phase['pid']=child.pid;save();phase['exit_code']=child.wait()
 text=Path(phase['log']).read_text();phase['log_sha256']=hashlib.sha256(Path(phase['log']).read_bytes()).hexdigest()
 phase['status']='passed' if phase['exit_code']==0 and not re.search(r'(?:SCRIPT )?ERROR:|WARNING:',text) else 'failed';save()
 if phase['status']!='passed':raise RuntimeError(text[-4000:])
 print('MOON_CURRENT_PHASE_PASS',label,flush=True)
try:
 for label,script,args in [('full-lighting','test_full_scene_lighting',[]),('wash-normal','test_baked_backdrop_wash',[]),('wash-demo','test_baked_backdrop_wash',['--demo']),('spill-normal','test_terminal_spill',[]),('spill-demo','test_terminal_spill',['--demo']),('entry-physics','test_entry_route',[]),('demo','test_first_reading_demo',[]),('reading','test_demo_reading',[]),('source-keys','test_site_key_import',[])]:run(label,script,args=args)
 run('native-paint-transfer','test_moon_paint_transfer',True,['--source=res://assets/garden-of-dreams.glb','--atlas=res://tests/moon-paint-atlas.json','--output-directory='+str(folder/'paint-transfer')])
 run('portrait-framing','test_pavilion_portrait_framing',True)
 for shape in ['desktop','portrait']:
  run('arrivals-'+shape,'render_entry_route',True,['--views-only','--fixed-clock','--output-directory='+str(folder/shape)]+(['--mobile'] if shape=='portrait' else []))
 assert hashlib.sha256((root/'godot/assets/garden-of-dreams.glb').read_bytes()).hexdigest()==report['source_glb_sha256']
 report['status']='passed';save();print('MOON_CURRENT_RUNTIME_PASS',flush=True)
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
