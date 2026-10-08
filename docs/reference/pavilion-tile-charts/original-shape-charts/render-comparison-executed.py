import pathlib,json,subprocess,re
w=pathlib.Path(json.load(open('/tmp/garden-tile-ridge-candidate.json'))['folder']);f=pathlib.Path(json.load(open('/tmp/garden-roof-detail.json'))['fixture']);engine='/Applications/Godot.app/Contents/MacOS/Godot';phases=[]
def run(name,args,marker=None):
 cmd=[engine,'--path',str(f)]+args
 with (w/(name+'.log')).open('w') as file:r=subprocess.run(cmd,stdout=file,stderr=subprocess.STDOUT,timeout=180)
 log=(w/(name+'.log')).read_text();errors=re.findall(r'^.*(?:SCRIPT ERROR:|ERROR:|Parse Error:|Assertion failed).*$',log,re.M);record={'name':name,'command':cmd,'exit_code':r.returncode,'native_errors':errors,'status':'passed' if r.returncode==0 and not errors and (not marker or marker in log) else 'failed'};phases.append(record);(w/'native-phases.json').write_text(json.dumps(phases,indent=2)+'\n');print(name,record['status'],flush=True);assert record['status']=='passed',record
run('candidate-import',['--headless','--editor','--import'])
old=(f/'lightmaps/SITE_qinfang-ting_MAT_pavilion_atlas.png.import').read_text();target=f/'tests/tile-ridge-lightmap.png.import';text=target.read_text();target.write_text(text.split('[params]')[0]+'[params]'+old.split('[params]')[1])
run('candidate-map-import',['--headless','--editor','--import'])
run('native-comparison',['--script','res://tests/diagnose_tile_ridge_candidate.gd','--','--output='+str(w/'native-captures')],'TILE_RIDGE_NATIVE_COMPARISON_PASS')
