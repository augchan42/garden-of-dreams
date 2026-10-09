from pathlib import Path
import ast,json,hashlib
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root']);out=w/'source-code-candidates';out.mkdir(exist_ok=True)
s=(r/'scripts/complete_flora_kit.py').read_text();candidate=(w/'executed-helpers/garden_build_reed_volume_candidate.py').read_text();tree=ast.parse(candidate);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build');body=ast.get_source_segment(candidate,fn)
body=body[body.index('\n')+1:];body=body[:body.index(' return g,details')];body=body.replace('rng=random.Random(89);g=Geometry(quality);details=[]','rng=random.Random(89);details=[]')
start=s.index(" elif variant=='reed':");end=s.index('\n else:',start);replacement=" elif variant=='reed':\n"+'\n'.join(' '+line for line in body.splitlines())
s=s[:start]+replacement+s[end:];ast.parse(s)
p=out/'complete_flora_kit.py';assert not p.exists();p.write_text(s)
(out/'generator-preparation.json').write_text(json.dumps({'status':'prepared_unexecuted_generator_candidate','production_script_sha256':hashlib.sha256((r/'scripts/complete_flora_kit.py').read_bytes()).hexdigest(),'candidate_script_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scope':'Only the reed branch receives the inspected volumetric geometry algorithm. All other seven variant branches stay literal. The active bake frozen scripts are untouched. Isolated full regeneration/semantic comparison against all16candidate kit exports is required before adoption.'},indent=2)+'\n');print('PREPARED_REED_GENERATOR_BRANCH',p)
