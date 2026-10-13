"""Verify the actual embedded paint and atlas sizes in standalone stage GLBs."""
from pathlib import Path
import argparse,hashlib,io,json,struct
from PIL import Image

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=root)
parser.add_argument('--output',type=Path)
args=parser.parse_args();root=args.root
variants=['cyclorama_moonlit','cyclorama_dusk','cyclorama_mist','studio_wall','floor_boards','fog_plane','gel_frame']
expected_files={f'KIT_stage_{name}{lod}.glb' for name in variants for lod in ['', '_LOD1']}
assert {p.name for p in (root/'export/kits/stage').glob('KIT_stage_*.glb')}==expected_files
files=[root/'export/kits/stage'/name for name in sorted(expected_files)]
files += [root/'export/kits/KIT_stage.glb',root/'export/kits/KIT_stage_LOD1.glb']
assert len(files)==16,'Expected fourteen variants/LODs and two legacy aliases'
rows=[];failures=[];paint_count=0
for path in files:
 data=path.read_bytes();assert struct.unpack_from('<4sII',data)==(b'glTF',2,len(data))
 size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 doc=json.loads(data[20:20+size]);binary=data[28+size:]
 for material in doc.get('materials',[]):
  name=material.get('name','')
  if name.startswith('MAT_stage_cyclorama_'):
   pbr=material['pbrMetallicRoughness'];base=pbr['baseColorTexture']['index'];emission=material['emissiveTexture']['index']
   assert doc['textures'][base]['source']==doc['textures'][emission]['source'],'Paint must be shared by base and emission'
   indexes=[base];expected=(2048,2048);paint_count+=1
  elif name.startswith('MAT_stage_atlas'):
   pbr=material['pbrMetallicRoughness'];indexes=[pbr['baseColorTexture']['index'],pbr['metallicRoughnessTexture']['index']];expected=(2048,2048)
  elif name.startswith('MAT_stage_fog'):
   indexes=[material['pbrMetallicRoughness']['baseColorTexture']['index']];expected=(512,512)
  else:continue
  for index in indexes:
   image=doc['images'][doc['textures'][index]['source']];view=doc['bufferViews'][image['bufferView']]
   raw=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
   with Image.open(io.BytesIO(raw)) as original:original.load();dimensions=original.size
   row={'file':str(path.relative_to(root)),'material':name,'size':list(dimensions),'expected':list(expected),'image_sha256':hashlib.sha256(raw).hexdigest()};rows.append(row)
   if dimensions!=expected:failures.append(row)
assert paint_count==8,'Expected six cyclorama variants/LODs plus two aliases'
report={'status':'failed' if failures else 'passed','paint_material_count':paint_count,'files_checked':len(files),'rows':rows,'failures':failures,'scope':'Actual embedded standalone stage paints and stock atlases2048; fog mask remains512. Source originals, assembled scene, native art and phone acceptance are separate.'}
out=args.output or root/'export/kits/stage/texture-size-validation.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
assert not failures,('Stage export texture size mismatch',len(failures))
print('STAGE_KIT_TEXTURE_SIZE_PASS',len(files),paint_count)
