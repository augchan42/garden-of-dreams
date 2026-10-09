from pathlib import Path
import json,hashlib,subprocess,re
r=Path('/Users/auchan/projects/garden-of-dreams');w=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-source-art';p=r/'export/ziling-source-art-install-scope.json';d=json.loads(p.read_text());d['checks']=[]
for name,args,marker in [('post-cleanup-import',['--editor','--import'],None),('post-cleanup-water',['--script','res://tests/test_water_kit.gd'],'WATER_KIT_PASS')]:
 log=w/(name+'.log');cmd=['/Applications/Godot.app/Contents/MacOS/Godot','--headless','--path',str(r/'godot')]+args
 with log.open('w') as out:result=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=180)
 text=log.read_text();assert result.returncode==0 and not re.search(r'(?m)^(ERROR:|SCRIPT ERROR:|.*Parse Error:|.*Assertion failed)',text)
 assert marker is None or marker in text
 d['checks'].append({'name':name,'exit_code':0,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'log':str(log)});p.write_text(json.dumps(d,indent=2)+'\n');print('INSTALL_SCOPE_CHECK_PASS',name,flush=True)
d['status']='unused_godot_aliases_excluded_post_cleanup_import_water_passed';p.write_text(json.dumps(d,indent=2)+'\n')
