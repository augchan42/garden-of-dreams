from pathlib import Path
import shutil,json,hashlib,sys,subprocess,numpy as np
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art-durable.json').read_text())['root']);source=w/'reeds-volume';root=w/'lit-native-review';assert not root.exists();root.mkdir();g=root/'godot';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=sha(source/'export/garden-of-dreams.glb');old='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38';assert sha(r/'godot/assets/garden-of-dreams.glb')==old
shutil.copytree(source/'blender',root/'blender',ignore=shutil.ignore_patterns('*.blend1','*.blend2'));shutil.copytree(source/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(source/'export',root/'export',ignore=shutil.ignore_patterns('lightmaps','full-lighting-refresh.json','lightmaps-coverage.json','lightmap-pixels.json','terminal-spill-pixels.json'));shutil.copytree(r/'textures',root/'textures');shutil.copytree(r/'docs/sites',root/'docs/sites');shutil.copytree(r/'godot',g,ignore=shutil.ignore_patterns('.godot','lightmaps','acceptance-captures','captures'));(g/'lightmaps').mkdir();shutil.copyfile(source/'export/garden-of-dreams.glb',g/'assets/garden-of-dreams.glb');
for p in (source/'export/kits/flora').iterdir():
 if p.suffix=='.glb' or p.name in ['manifest.json','validation.json']:shutil.copyfile(p,g/'assets/kits/flora'/p.name)
(g/'assets/garden-source.json').write_text(json.dumps({'source_glb_sha256':expected},indent=2)+'\n');shutil.copyfile(w/'candidate-source-contract.json',g/'tests/source-contract.json');shutil.copyfile(r/'textures/backdrops/moon-paint/atlas.json',g/'tests/moon-paint-atlas.json')
sys.path.insert(0,str(r/'scripts'));from verify_mountain_export import Glb
before=Glb(r/'godot/assets/garden-of-dreams.glb');after=Glb(source/'export/garden-of-dreams.glb');portrait=json.loads((g/'tests/portrait-architecture-contract.json').read_text());assert portrait['source_glb_sha256']==old;proof={}
for room in portrait['rooms'].values():
 for name in room['meshes']:
  a=next(n for n in before.doc['nodes'] if n['name']==name);b=next(n for n in after.doc['nodes'] if n['name']==name);assert a==b
  hashes=[]
  for p,q in zip(before.doc['meshes'][a['mesh']]['primitives'],after.doc['meshes'][b['mesh']]['primitives']):
   x=before.accessor(p['attributes']['POSITION'])[before.accessor(p['indices']).ravel()];y=after.accessor(q['attributes']['POSITION'])[after.accessor(q['indices']).ravel()];assert np.array_equal(x,y);hashes.append(hashlib.sha256(y.tobytes()).hexdigest())
  proof[name]=hashes
portrait['source_glb_sha256']=expected;portrait['scope']+=' Candidate source retains all architecture subjects, proven equal to current26033 expanded mesh positions and node records.';(g/'tests/portrait-architecture-contract.json').write_text(json.dumps(portrait,indent=2)+'\n')
modified={}
for name in ['test_hengwu_detail_framing.gd','test_tubi_framing.gd','test_qiushuang_framing.gd','test_ziling_framing.gd','render_dynamic_palette.gd']:
 p=g/'tests'/name;s=p.read_text();assert s.count(old)==1;s=s.replace(old,expected)
 if name=='test_ziling_framing.gd':assert s.count('subjects.reeds.size()==10940')==1;s=s.replace('subjects.reeds.size()==10940','subjects.reeds.size()==48320')
 p.write_text(s);modified[name]={'baseline_sha256':sha(r/'godot/tests'/name),'candidate_sha256':sha(p)}
cmd=[sys.executable,str(root/'scripts/build_garden_palette_contract.py'),'--source',str(root/'export/garden-of-dreams.glb'),'--atlas-root',str(root),'--output',str(g/'tests/garden-palette-contract.json')];result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);assert result.returncode==0,result.stdout
record={'status':'static_fixture_prepared_no_native_import_or_maps_installed','source_root':str(source),'folder':str(root),'source_glb_sha256':expected,'authoring_sha256':sha(source/'blender/authoring.blend'),'production_route_sha256':sha(r/'godot/runtime/entry_route.gd'),'fixture_route_sha256':sha(g/'runtime/entry_route.gd'),'source_guard_changes':modified,'portrait_architecture_expanded_geometry_proof':proof,'source_contract_sha256':sha(g/'tests/source-contract.json'),'scope':'Current production runtime copied literally. Source-specific test guards updated only after controlled ten-reed/stream/lotus comparisons and unchanged camera/collider/marker extraction; nine architecture subject meshes compared independently. Complete source lighting, standalone water synchronization, kit generation/reexport, native import/actions/walks/lit review still pending.'}
assert record['production_route_sha256']==record['fixture_route_sha256'];assert not (g/'.godot').exists() and not list((g/'lightmaps').iterdir());(root/'fixture-preparation.json').write_text(json.dumps(record,indent=2)+'\n');Path('/tmp/garden-ziling-lit-review.json').write_text(json.dumps({'root':str(root),'source':str(source)})+'\n');print('ZILING_LIT_FIXTURE_PREPARED',root)
