from pathlib import Path
import json,shutil,subprocess,hashlib,re,struct
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root']);f=Path(json.loads(Path('/tmp/garden-ziling-framing.json').read_text())['folder'])/'godot';source=w/'reeds-bold/export/garden-of-dreams.glb';out=w/'reed-bold-native-comparison';assert not out.exists();out.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert json.loads((w/'reeds-bold/export-preservation.json').read_text())['status']=='controlled_reed_export_preserved'
shutil.copyfile(source,f/'assets/garden-of-dreams.glb')
for suffix in ['', '_LOD1']:shutil.copyfile(w/'reeds-bold/export/kits/flora'/('KIT_flora_reed'+suffix+'.glb'),f/'assets/kits/flora'/('KIT_flora_reed'+suffix+'.glb'))
shutil.copyfile('/tmp/garden_render_reed_candidate.gd',f/'tests/render_reed_candidate.gd');p={'status':'running','source_glb_sha256':sha(source),'phases':[],'fixture':str(f),'scope':'Sequential native no-bake geometry views of the actual reed source and its explicitly forced LOD1. Source/fresh lighting/route/production acceptance remain separate.'}
def save():(out/'pipeline.json').write_text(json.dumps(p,indent=2)+'\n')
def run(name,cmd,marker=None):
 log=out/(name+'.log')
 with log.open('w') as stream:
  try:res=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=130);code=res.returncode
  except subprocess.TimeoutExpired:code=124
 text=log.read_text();ok=code==0 and not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:|Assertion failed)',text,re.M) and (marker is None or marker in text)
 p['phases'].append({'name':name,'command':cmd,'exit_code':code,'log':str(log),'log_sha256':sha(log),'status':'passed' if ok else 'failed'});save();print('REED_COMPARE',name,'passed' if ok else 'failed',flush=True)
 if not ok:p['status']='failed';save();print(text[-2000:]);raise SystemExit(1)
g='/Applications/Godot.app/Contents/MacOS/Godot';run('import',[g,'--headless','--path',str(f),'--editor','--import'])
for variant,flags in [('full',[]),('forced-lod1',['--force-lod'])]:
 run(variant+'-captures',[g,'--path',str(f),'--windowed','--resolution','1410x600','--script','res://tests/render_reed_candidate.gd','--','--output='+str(out/variant),'--variant='+variant,'--source='+sha(source)]+flags,'REED_NATIVE_RESULT '+variant+' 9 originals')
 data=json.loads((out/variant/'report.json').read_text());assert len(data['rows'])==9 and data['source_glb_sha256']==sha(source)
 for row in data['rows']:
  path=Path(row['capture']);assert sha(path)==row['sha256'];assert list(struct.unpack('>II',path.read_bytes()[16:24]))==row['pixels']
p['status']='unbaked_native_reed_comparison_phases_passed';save();print('REED_NATIVE_COMPARISON_PASS',flush=True)
