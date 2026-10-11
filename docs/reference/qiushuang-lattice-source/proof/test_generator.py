"""Exercise the real hall generator's lattice with the saved CRT geometry."""
import ast,bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
repo=Path('/Users/auchan/projects/garden-of-dreams');root=Path('/tmp/garden-qiushuang-lattice-20261010')
sys.path.insert(0,str(root))
from lattice_contract import inspect
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.name.startswith('Garden of Dreams'))
source=Path(bpy.data.filepath);source_bytes=source.read_bytes()
site=bpy.data.collections['SITE_qiushuang-zhai']
bars=lambda:[o for o in site.objects if o.type=='MESH' and 'lattice' in o.name.lower()]
def bounds():
 return sorted(tuple(round(v,5) for v in sum((o.matrix_world@Vector(p) for p in o.bound_box),Vector())/8) for o in bars())
saved=bounds();assert len(saved)==42
helpers=ast.parse((repo/'scripts/build_garden.py').read_text())
env={'bpy':bpy,'C':site}
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['mesh','box']],type_ignores=[]),'real_box','exec'),env)
real_box=env['box']
def noop(*a,**k):pass
def lattice_box(name,*a,**k):
 if name.startswith('KIT_wall_lattice_'):return real_box(name,*a,**k)
env.update({name:noop for name in ['collection','collision','crt','cyl','roof','sign','lantern','empty','camera','light']})
env.update({name:None for name in ['stone','black','plaster','wood','crtamber']});env['box']=lattice_box
rows=[];normal_bounds=[]
for mode,file in [('red',repo/'scripts/complete_garden.py'),('green',root/'canonical_complete_garden.py')]:
 tree=ast.parse(file.read_text());hall=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='hall')
 exec(compile(ast.Module(body=[hall],type_ignores=[]),str(file),'exec'),env)
 for monitors in [True,False]:
  for o in bars():bpy.data.objects.remove(o,do_unlink=True)
  env['hall']('qiushuang-zhai','test',(22,16,0),9,2,monitors)
  bpy.context.view_layer.update()
  if monitors:
   result=inspect();result['mode']=mode;result['generator_sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
   rows.append(result)
   if mode=='red':assert result['blocked_samples']==180,result['blocked_samples']
   else:
    assert result['status']=='passed',result['blocked_samples']
    assert bounds()==saved,'Generated placements do not reproduce the saved source layout'
  else:normal_bounds.append(bounds())
assert normal_bounds[0]==normal_bounds[1],'Non-monitor lattice changed'
assert source.read_bytes()==source_bytes
report={'status':'passed','red_blocked':rows[0]['blocked_samples'],'green_blocked':rows[1]['blocked_samples'],'samples_per_layout':1152,'saved_source_layout_reproduced':True,'non_monitor_layout_preserved':True,'source_file_preserved':True,'results':rows}
(root/'generator-reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
print('QIUSHUANG_GENERATOR_RED_GREEN_PASS',180,0,flush=True)
