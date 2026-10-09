from pathlib import Path
import json,shutil,subprocess,hashlib,re,struct
r=Path('/Users/auchan/projects/garden-of-dreams');w=Path(json.loads(Path('/tmp/garden-ziling-source-art.json').read_text())['root']);f=Path(json.loads(Path('/tmp/garden-ziling-framing.json').read_text())['folder'])/'godot';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();out=w/'waterline-native-comparison';assert not out.exists();out.mkdir()
for name in ['runtime/entry_route.gd','garden_preview.tscn','materials/water.tres','shaders/pond_reflection.gdshader']:shutil.copyfile(r/'godot'/name,f/name)
shutil.copyfile('/tmp/garden_render_stream_waterline.gd',f/'tests/render_stream_waterline.gd');p={'status':'running','phases':[],'fixture':str(f),'scope':'Two sequential native no-bake geometry comparisons, before any fresh source lighting or production adoption.'}
def save():(out/'pipeline.json').write_text(json.dumps(p,indent=2)+'\n')
def run(name,cmd,marker=None):
 log=out/(name+'.log')
 with log.open('w') as stream:
  try:res=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,timeout=130);code=res.returncode
  except subprocess.TimeoutExpired:code=124
 text=log.read_text();ok=code==0 and not re.search(r'(SCRIPT ERROR:|Parse Error:|^ERROR:|Assertion failed)',text,re.M) and (marker is None or marker in text)
 p['phases'].append({'name':name,'command':cmd,'exit_code':code,'log':str(log),'log_sha256':sha(log),'status':'passed' if ok else 'failed'});save();print('STREAM_COMPARE',name,'passed' if ok else 'failed',flush=True)
 if not ok:p['status']='failed';save();print(text[-2500:]);raise SystemExit(1)
g='/Applications/Godot.app/Contents/MacOS/Godot'
for variant,source in [('baseline',r/'godot/assets/garden-of-dreams.glb'),('candidate',w/'waterline/export/garden-of-dreams.glb')]:
 shutil.copyfile(source,f/'assets/garden-of-dreams.glb');assert sha(source)==sha(f/'assets/garden-of-dreams.glb')
 run(variant+'-import',[g,'--headless','--path',str(f),'--editor','--import'])
 run(variant+'-captures',[g,'--path',str(f),'--windowed','--resolution','1410x600','--script','res://tests/render_stream_waterline.gd','--','--output='+str(out/variant),'--variant='+variant,'--source='+sha(source)],'STREAM_WATERLINE_NATIVE_RESULT '+variant+' 9 originals')
 data=json.loads((out/variant/'report.json').read_text());assert len(data['rows'])==9 and data['source_glb_sha256']==sha(source)
 for row in data['rows']:
  path=Path(row['capture']);assert sha(path)==row['sha256'];assert list(struct.unpack('>II',path.read_bytes()[16:24]))==row['pixels']
p['status']='unbaked_geometry_comparison_phases_passed';save();print('STREAM_WATERLINE_COMPARISON_PASS',flush=True)
