from pathlib import Path
import ast
base=Path('/tmp/garden_review_neutral_atlas_full.py').read_text()
base=base.replace("SOURCE=Path(json.loads(Path('/tmp/garden-neutral-atlas-full-source.json').read_text())['folder'])", "SOURCE=Path(json.loads(Path('/tmp/garden-hengwu-compact-rock.json').read_text())['root']).resolve()")
base=base.replace("EXPECTED=hashlib.sha256((SOURCE/'export/garden-of-dreams.glb').read_bytes()).hexdigest()", "EXPECTED='26033c99c82f9609f02ea545d4812b3ce1bd9ea2c9ecdf89a51e3ced03fe3d38'")
base=base.replace("AUTHOR=hashlib.sha256((SOURCE/'blender/authoring.blend').read_bytes()).hexdigest()", "AUTHOR='19eb386d8e93007ebd8e4ae2d9ee59ec7daa07dcd8dbe3c3a88d4ec84b5e5a08'")
base=base.replace('garden-neutral-atlas-full-review-', 'garden-hengwu-full-review-').replace('/tmp/garden-neutral-atlas-full-review.json','/tmp/garden-hengwu-full-review.json').replace('NEUTRAL_ATLAS_FULL_TECHNICAL_REVIEW_COMPLETE','HENGWU_FULL_TECHNICAL_REVIEW_COMPLETE')
base=base.replace(" shutil.copytree(REPO/'docs/sites',ROOT/'docs/sites')", " shutil.copytree(REPO/'docs/sites',ROOT/'docs/sites')\n shutil.copytree(REPO/'textures',ROOT/'textures')")
base=base.replace("  shutil.copy2(SOURCE/'baseline/textures/atlases'/kind/(kind+'_basecolor.png'),GD/'tests/palette-before'/(kind+'_basecolor.png'))", "  previous=Path(json.loads(Path('/tmp/garden-neutral-atlas-full-source.json').read_text())['folder'])/'baseline/textures/atlases'/kind/(kind+'_basecolor.png')\n  shutil.copy2(previous,GD/'tests/palette-before'/(kind+'_basecolor.png'))")
needle=" report['runtime_inputs_sha256']="
index=base.index(needle)
preparation=''' # CPU contracts are derived from the actual exported candidate before native work.
 py=sys.executable
 run('palette-source-contract',[py,str(ROOT/'scripts/build_garden_palette_contract.py'),'--source',str(ROOT/'export/garden-of-dreams.glb'),'--atlas-root',str(ROOT),'--output',str(GD/'tests/garden-palette-contract.json')],'GARDEN_PALETTE_SOURCE_CONTRACT_PASS')
 run('source-import-contract',[py,str(ROOT/'scripts/build_godot_import_contract.py'),'--output',str(GD/'tests/source-contract.json')],'GODOT_IMPORT_SOURCE_CONTRACT')
 sys.path.insert(0,str(ROOT/'scripts'))
 import numpy as np
 from verify_mountain_export import Glb
 before=Glb(REPO/'godot/assets/garden-of-dreams.glb');after=Glb(ROOT/'export/garden-of-dreams.glb')
 assert hashlib.sha256(before.bytes).hexdigest()=='59de1ca29bc9d02235fc29a18b78c7b2c3dfde893a27f3b8fb318af6e042ddc8'
 portrait=json.loads((GD/'tests/portrait-architecture-contract.json').read_text())
 assert portrait['source_glb_sha256']==hashlib.sha256(before.bytes).hexdigest()
 equal_meshes={}
 for room in portrait['rooms'].values():
  for name in room['meshes']:
   old=next(n for n in before.doc['nodes'] if n['name']==name);new=next(n for n in after.doc['nodes'] if n['name']==name)
   assert old==new,name
   a=before.doc['meshes'][old['mesh']]['primitives'];b=after.doc['meshes'][new['mesh']]['primitives'];assert len(a)==len(b)
   hashes=[]
   for p,q in zip(a,b):
    ix=before.accessor(p['indices']).ravel();iy=after.accessor(q['indices']).ravel()
    x=before.accessor(p['attributes']['POSITION'])[ix];y=after.accessor(q['attributes']['POSITION'])[iy];assert np.array_equal(x,y),name
    hashes.append(hashlib.sha256(y.tobytes()).hexdigest())
   equal_meshes[name]=hashes
 portrait['source_glb_sha256']=EXPECTED
 portrait['scope']+=' Candidate contract retains the nine unchanged expanded architecture meshes and node transforms, independently compared to the reviewed 59de source.'
 (GD/'tests/portrait-architecture-contract.json').write_text(json.dumps(portrait,indent=2)+'\\n')
 report['portrait_contract_preservation']={'baseline_source_sha256':hashlib.sha256(before.bytes).hexdigest(),'candidate_source_sha256':EXPECTED,'equal_expanded_position_sha256':equal_meshes}
 shutil.copy2('/tmp/garden_render_hengwu_lit_candidate.gd',GD/'tests/render_hengwu_lit_candidate.gd')
'''
base=base[:index]+preparation+base[index:]
# Wait for the preparation parent to verify its 240 frozen inputs and exit too.
base=base.replace("   if not alive(bake['orchestrator_pid']):break", "   prepared=json.loads((SOURCE/'lighting-preparation.json').read_text())\n   if prepared['status']=='failed':raise RuntimeError(('Source preparation failed',prepared))\n   if prepared['status']=='complete_source_lighting_passed_native_review_pending' and not alive(bake['orchestrator_pid']) and not alive(prepared['orchestrator_pid']):break")
base=base.replace(" report['source_bake_report']=bake", " frozen=json.loads((SOURCE/'full-lighting-inputs.json').read_text())['files']\n for name,digest in frozen.items():assert sha(SOURCE/name)==digest,name\n report['verified_frozen_source_inputs']=len(frozen)\n report['source_preparation_report']=prepared\n report['source_bake_report']=bake")
base=base.replace("'--atlas-root',str(SOURCE)","'--atlas-root',str(ROOT)")
# Contracts were already built; do not rebuild them without need after waiting.
late_start=base.index(" run('palette-source-contract'",base.index(" assert len(pngs)==141"))
late_end=base.index(" godot='/Applications",late_start)
base=base[:late_start]+base[late_end:]
base=base.replace(" cap=ROOT/'review-captures';cap.mkdir()", " reproduce=Path(tempfile.mkdtemp(prefix='garden-hengwu-native-reexport-'))\n run('saved-source-default-reexport',['/Applications/Blender.app/Contents/MacOS/Blender','--background',str(ROOT/'blender/authoring.blend'),'--threads','8','--python-exit-code','1','--python',str(REPO/'scripts/verify_saved_garden_candidate.py'),'--','--source-root',str(ROOT),'--output-root',str(reproduce)],'SAVED_GARDEN_CANDIDATE_PASS')\n report['saved_default_reexport_report']=str(reproduce/'saved-source-verification.json');save()\n cap=ROOT/'review-captures';cap.mkdir()\n run('hengwu-lit-actions',native+['--script','res://tests/render_hengwu_lit_candidate.gd','--','--output='+str(cap/'hengwu-lit-actions')],'HENGWU_LIT_ACTIONS_RECORDED')\n run('portrait-architecture',native+['--script','res://tests/test_portrait_architecture.gd','--','--output='+str(cap/'portrait-architecture')],'PORTRAIT_ARCHITECTURE_PASS')\n for label,script,marker in [('courtyard','test_courtyard_route.gd','COURTYARD_ROUTE_PASS'),('farmhouse','test_farmhouse_route.gd','FARMHOUSE_ROUTE_PASS')]:\n  run('route-'+label,head+['--script','res://tests/'+script],marker)")
# Preserve the exact executed pipeline alongside its reports.
base=base.replace(" save()\n # Static copies", " save()\n shutil.copy2(__file__,ROOT/'executed-review-pipeline.py')\n # Static copies")
ast.parse(base)
Path('/tmp/garden_review_hengwu_full.py').write_text(base)
print('HENGWU_REVIEW_PIPELINE_PREPARED',len(base))
