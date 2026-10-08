import hashlib,json,shutil,sys,tempfile
from pathlib import Path
root=Path('/Users/auchan/projects/garden-of-dreams')
sys.path.insert(0,str(root/'scripts'))
from verify_mountain_export import Glb
work=Path(tempfile.mkdtemp(prefix='garden-kit-neutral-palette-')).resolve()
baseline=work/'baseline';candidate=work/'candidate';inputs={}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for kit in ('pavilion','corridor','wall','rockery'):
 source=root/f'blender/kits/KIT_{kit}.blend'
 dest=baseline/source.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 for p in sorted((root/f'export/kits/{kit}').glob('*')):
  if not p.is_file():continue
  dest=baseline/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 for suffix in ('','_LOD1'):
  p=root/f'export/kits/KIT_{kit}{suffix}.glb';dest=baseline/p.relative_to(root);shutil.copy2(p,dest)
 for p in [source,*sorted((root/f'export/kits/{kit}').glob('*')),*[root/f'export/kits/KIT_{kit}{s}.glb' for s in ('','_LOD1')]]:
  if p.is_file():inputs[str(p.relative_to(root))]=sha(p)
 (candidate/f'export/kits/{kit}').mkdir(parents=True)
 for name in ('manifest.json',):shutil.copy2(root/f'export/kits/{kit}/{name}',candidate/f'export/kits/{kit}/{name}')
for kind,kit in [('pavilion','pavilion'),('wall','wall')]:
 g=Glb(next((baseline/f'export/kits/{kit}').glob('*.glb')))
 old=baseline/f'textures/atlases/{kind}';old.mkdir(parents=True)
 for image in g.doc['images']:
  v=g.doc['bufferViews'][image['bufferView']];start=v.get('byteOffset',0)
  (old/(image['name']+'.png')).write_bytes(g.binary[start:start+v['byteLength']])
 shutil.copy2(root/f'textures/atlases/{kind}/atlas.json',old/'atlas.json')
 shutil.copytree(root/f'textures/atlases/{kind}',candidate/f'textures/atlases/{kind}')
 for p in sorted((root/f'textures/atlases/{kind}').glob('*')):
  if p.is_file():inputs[str(p.relative_to(root))]=sha(p)
for name in ('verify_garden_atlas_export.py','verify_mountain_export.py','verify_pavilion_atlas.py'):
 inputs['scripts/'+name]=sha(root/'scripts'/name)
checkpoint={'status':'isolated_kit_sources_prepared_native_update_pending','work':str(work),'baseline':str(baseline),'candidate':str(candidate),'inputs':inputs,'scope':'Four standalone sources, 48 variants/LODs and eight legacy aliases. Main garden source and lighting remain separate.'}
(work/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
Path('/tmp/garden-kit-neutral-palette.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps({k:checkpoint[k] for k in ('work','baseline','candidate')}))
