from pathlib import Path
import hashlib,json,struct,io
from PIL import Image
repo=Path('/Users/auchan/projects/garden-of-dreams');r=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected={
'corridor':'straight corner tee stair',
'pavilion':'roof_hex roof_square post bracket eave_strip bench',
'wall':'bay moon_gate vase_gate window_square window_diamond window_ice window_hex roof_cap',
'rockery':'small medium large arch tunnel cliff',
'water':'stream pond embankment lotus wood_bridge stone_bridge',
'flora':'bamboo_small bamboo_medium bamboo_large plum willow banana reed potted',
'props':'lantern_hanging lantern_standing brazier stone_table stone_stool incense_burner scroll screen folding_chair',
'tech':'crt_amber crt_green monitor_bank cable_run cell_door terminal_desk',
'stage':'cyclorama_moonlit cyclorama_dusk cyclorama_mist studio_wall floor_boards fog_plane gel_frame'}
assert json.loads((r/'report.json').read_text())['status']=='passed'
files={};images={};variants={};runtime_exact=0
for kit,names in expected.items():
 manifest=json.loads((repo/f'export/kits/{kit}/manifest.json').read_text());assert set(manifest['variants'])==set(names.split()),kit
 variants[kit]=names.split()
 for name in names.split():
  for lod in ['', '_LOD1']:
   rel=Path(f'export/kits/{kit}/KIT_{kit}_{name}{lod}.glb');p=repo/rel;blob=p.read_bytes();assert struct.unpack_from('<4sII',blob)==(b'glTF',2,len(blob)),str(rel)
   size,kind=struct.unpack_from('<II',blob,12);assert kind==0x4e4f534a;doc=json.loads(blob[20:20+size]);bs,bk=struct.unpack_from('<II',blob,20+size);binary=blob[28+size:];assert bk==0x004e4942 and len(binary)==bs
   native=repo/'godot/assets/kits'/kit/p.name;assert sha(native)==sha(p),str(native);runtime_exact+=1;files[str(rel)]=sha(p)
   for item in doc.get('images',[]):
    if 'bufferView' in item:
     v=doc['bufferViews'][item['bufferView']];data=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
    else:
     path=p.parent/item['uri'];data=path.read_bytes()
    h=hashlib.sha256(data).hexdigest()
    with Image.open(io.BytesIO(data)) as im:im.load();dimensions=list(im.size);mode=im.mode
    images[h]={'dimensions':dimensions,'mode':mode}
assert runtime_exact==120
assert all(v['dimensions']==[2048,2048] for v in images.values()),images
for n,d in json.loads((r/'inputs.json').read_text())['files'].items():assert sha(repo/n)==d,n
report={'status':'passed','requirements_source':'docs/garden-scene-spec.md section6.1 and section7','kit_count':9,'variants':variants,'variant_count':60,'LOD_export_count':120,'engine_GLBs_byte_exact':runtime_exact,'unique_decoded_embedded_atlases':images,'files':files,'scope':'All named stock variants present with both LODs; nine geometry/UV/connector/collider/LOD verifiers pass; actual120engineGLBs byte-exact; all embedded atlas originals decode at2048. No native shader binding, source-library reproduction, assembled geometry, final art, runtime allocation or physical-phone acceptance.'}
(r/'inventory.json').write_text(json.dumps(report,indent=2)+'\n');print('CURRENT_KIT_INVENTORY_PASS',len(variants),runtime_exact,len(images))
