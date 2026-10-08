"""Share equivalent moon image slots without changing native material factors."""
import copy,hashlib,struct

def share_moon_texture(document,blob):
 length=struct.unpack_from('<I',blob,12)[0]
 binary=blob[28+length:]
 def signature(index):
  texture=copy.deepcopy(document['textures'][index]);image=document['images'][texture['source']]
  view=document['bufferViews'][image['bufferView']];offset=view.get('byteOffset',0)
  texture['source']=[image.get('mimeType'),hashlib.sha256(binary[offset:offset+view['byteLength']]).hexdigest()]
  if 'sampler' in texture:texture['sampler']=document['samplers'][texture['sampler']]
  return texture
 changed=False
 for material in document.get('materials',[]):
  if material.get('name')!='MAT_painted_moon' or material.get('extras',{}).get('paint_source')!='textures/backdrops/moon-paint/atlas.json':continue
  base=material['pbrMetallicRoughness']['baseColorTexture'];emission=material['emissiveTexture']
  assert {k:v for k,v in base.items() if k!='index'}=={k:v for k,v in emission.items() if k!='index'},'Moon sampler/UV contracts differ'
  assert signature(base['index'])==signature(emission['index']),'Moon base/emission images are not identical'
  if base['index']!=emission['index']:emission['index']=base['index'];changed=True
 return changed
