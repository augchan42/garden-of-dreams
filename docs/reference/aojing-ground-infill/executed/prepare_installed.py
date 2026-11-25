from pathlib import Path
import py_compile
r=Path(__file__).resolve().parent;old=Path('/tmp/garden-corridor-roof-full-20261011')
s=(old/'validate_installed.py').read_text().replace(str(old),str(r)).replace('7fb3bbc1df9d45b7de2d0ea37dc93b84d31e53d52d9c730958f4fbff0926787b','09910fbaa40e41f1475759adb46625358ba9a8765e1863b2f583f7943a413290').replace("gate=root/'engine-adoption.json'","gate=root/'adoption.json'").replace('engine_inputs_adopted_native_import_and_installed_checks_pending','ground_source_engine_adopted_installed_checks_pending').replace("for name,h in json.loads(gate.read_text())['files'].items():assert sha(game/name)==h,name","for name,h in json.loads(gate.read_text())['copied_files'].items():assert sha(repo/name)==h,name")
s=s.replace("save()\n run('saved_key'","""save()
 run('ground_source',bpy+[str(repo/'blender/authoring.blend'),'--python',str(repo/'scripts/test_aojing_ground.py'),'--','--report',str(root/'installed-ground-source.json')],'AOJING_GROUND_SOURCE_PASS')
 run('canvas_palette',bpy+[str(repo/'blender/authoring.blend'),'--python',str(repo/'scripts/test_saved_canvas_palette.py'),'--','--report',str(root/'installed-canvas-palette.json')],'SAVED_CANVAS_PALETTE_PASS')
 run('saved_key'""")
s=s.replace("for name,script,marker,args in [('roof_uv'","for name,script,marker,args in [('ground_geometry','test_aojing_ground_native.gd','AOJING_GROUND_NATIVE_PASS',['--output='+str(root/'installed-ground-native.json')]),('stage_kit','test_stage_kit.gd','STAGE_KIT_PASS',[]),('roof_uv'")
pos=s.index(" assert sha(repo/'godot/runtime/entry_route.gd')",s.index("report['installed_originals_exact_to_candidate']"))
s=s[:pos]+""" helper=game/'tests/capture_aojing_lit.gd';assert not helper.exists()
 shutil.copy2(root/'capture_aojing_lit.gd',helper)
 try:run('native_ground',native+['--script','res://tests/capture_aojing_lit.gd','--','--output='+str(root/'installed-native-ground')],'AOJING_LIT_PASS')
 finally:
  helper.unlink(missing_ok=True);Path(str(helper)+'.uid').unlink(missing_ok=True)
 ground_count=0
 for p in (root/'installed-native-ground').glob('*.png'):
  assert p.read_bytes()==(root/'native-lit-ground'/p.name).read_bytes(),p.name;ground_count+=1
 assert ground_count==8;report['installed_ground_originals_exact_to_candidate']=ground_count
 baseline=json.loads((root/'adoption-baseline.json').read_text())
 for n,h in baseline['protected_files'].items():assert sha(repo/n)==h,n
 for n,params in baseline['protected_import_parameters'].items():assert (repo/n).read_text().split('[params]',1)[1]==params,n
 report['protected_stage_and_runtime_files_unchanged']=len(baseline['protected_files'])
 report['preserved_all_kit_and_lightmap_import_parameters']=len(baseline['protected_import_parameters'])
"""+s[pos:]
s=s.replace('CORRIDOR_ROOF_INSTALLED','AOJING_GROUND_INSTALLED');(r/'validate_installed.py').write_text(s);py_compile.compile(str(r/'validate_installed.py'),doraise=True)
print('AOJING_INSTALLED_RUNNER_PREPARED')
