import copy,hashlib,json,struct,sys
from pathlib import Path
root=Path('/Users/auchan/projects/garden-of-dreams');sys.path.insert(0,str(root/'scripts'))
from verify_garden_atlas_export import compare
from verify_mountain_export import Glb
from test_garden_atlas_export_rejections import write_glb
c=json.loads(Path('/tmp/garden-kit-neutral-palette.json').read_text());w=Path(c['work']);a=Path(c['baseline']);b=Path(c['candidate']);out=w/'rejections';out.mkdir()
relative=Path('export/kits/pavilion/KIT_pavilion_roof_hex.glb');before=a/relative;after=b/relative;g=Glb(after);cases=[]
def reject(name,doc,binary):
 p=out/(name+'.glb');write_glb(p,doc,binary)
 try:compare(before,p,a,b,require_both=False)
 except AssertionError as error:cases.append({'case':name,'rejected':True,'reason':str(error),'fixture_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 else:raise AssertionError('Unexpected acceptance: '+name)
 p.unlink()
old=Glb(before);reject('old-color',old.doc,old.binary)
for prefix,label in [('PORT_','connector'),('COL_','collision')]:
 bad=copy.deepcopy(g.doc);node=next(n for n in bad['nodes'] if n.get('name','').startswith(prefix));node['translation']=[99,99,99];reject(label,bad,g.binary)
for attribute in ('POSITION','NORMAL','TEXCOORD_0','TEXCOORD_1'):
 bad=bytearray(g.binary);p=next(p for m in g.doc['meshes'] for p in m['primitives'] if attribute in p['attributes']);i=int(g.accessor(p['indices']).ravel()[0]);access=g.doc['accessors'][p['attributes'][attribute]];view=g.doc['bufferViews'][access['bufferView']];cols={'VEC2':2,'VEC3':3}[access['type']];assert access['componentType']==5126
 offset=view.get('byteOffset',0)+access.get('byteOffset',0)+i*view.get('byteStride',cols*4);v=struct.unpack_from('<f',bad,offset)[0];struct.pack_into('<f',bad,offset,v+.25);reject(attribute,bad and g.doc,bad)
for channel in ('normal','orm'):
 bad=bytearray(g.binary);im=next(i for i in g.doc['images'] if i['name']=='pavilion_'+channel);offset=g.doc['bufferViews'][im['bufferView']].get('byteOffset',0);bad[offset+16]^=1;reject(channel+'-image',g.doc,bad)
bad=copy.deepcopy(g.doc);bad['materials'][0]['pbrMetallicRoughness']['baseColorFactor']=[0,1,0,1];reject('color-multiplier',bad,g.binary)
bad=copy.deepcopy(g.doc);bad['samplers'][0]['wrapS']=33071;reject('sampler',bad,g.binary)
(out/'report.json').write_text(json.dumps({'status':'kit_palette_preservation_controls_passed','positive_fixture_sha256':hashlib.sha256(after.read_bytes()).hexdigest(),'cases':cases},indent=2)+'\n')
print('KIT_PALETTE_REJECTIONS_PASS',len(cases))
