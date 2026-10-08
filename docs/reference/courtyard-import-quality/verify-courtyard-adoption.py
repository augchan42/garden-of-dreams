import json,pathlib,re,subprocess
root=pathlib.Path('/Users/auchan/projects/garden-of-dreams'); w=pathlib.Path(json.load(open('/tmp/garden-roof-detail.json'))['folder']);g=root/'godot'
engine='/Applications/Godot.app/Contents/MacOS/Godot'
phases=[]
def run(name,args,marker=None):
 cmd=[engine,'--path',str(g)]+args
 with (w/(name+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 text=(w/(name+'.log')).read_text(); bad=re.findall(r'^.*(?:SCRIPT ERROR:|ERROR:|Parse Error:|Assertion failed).*$' ,text,re.M)
 record={'name':name,'command':cmd,'exit_code':r.returncode,'native_errors':bad,'status':'passed' if r.returncode==0 and not bad and (marker is None or marker in text) else 'failed','log':str(w/(name+'.log'))}
 phases.append(record);(w/'production-phases.json').write_text(json.dumps(phases,indent=2)+'\n'); print(name,record['status'],flush=True)
 assert record['status']=='passed',record
run('production-import',['--headless','--editor','--import'])
run('production-source-contract',['--headless','--script','res://tests/test_import_source_contract.gd','--','res://assets/garden-of-dreams.glb','res://tests/source-contract.json',str(w/'production-source-contract.json')],'IMPORT_SOURCE_CONTRACT_PASS')
run('production-full-lighting',['--headless','--script','res://tests/test_full_scene_lighting.gd'],'FULL_SCENE_LIGHTING_PASS')
for name,script,marker in [('wash','test_baked_backdrop_wash.gd','BAKED_BACKDROP_WASH_PASS'),('spill','test_terminal_spill.gd','TERMINAL_SPILL_PASS')]:
 for mode in ['normal','demo']:
  args=['--headless','--script','res://tests/'+script]
  if mode=='demo':args+=['--','--demo']
  run('production-'+name+'-'+mode,args,marker)
run('production-capture',['--script','res://tests/capture_courtyard_imports.gd','--','--output='+str(w/'production-captures')],'COURTYARD_IMPORT_CAPTURE_PASS')
run('production-inventory',['--script','res://tests/audit_runtime_textures.gd','--','--output='+str(w/'production-inventory.json')],'RUNTIME_TEXTURE_INVENTORY_PASS')
report=json.loads((w/'production-adoption.json').read_text());report['status']='working_import_fix_adopted_checks_passed';report['production_phases']='production-phases.json';(w/'production-adoption.json').write_text(json.dumps(report,indent=2)+'\n')
