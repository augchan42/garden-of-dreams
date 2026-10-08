"""Prove that only two moon material factors change in an actual export."""
import argparse
import copy
from collections import Counter
import hashlib
import json
from pathlib import Path

from verify_canopy_candidate import Document

MATERIAL='MAT_painted_moon'

def compare(before_path:Path, after_path:Path, atlas:dict) -> dict:
    before,after=Document(before_path),Document(after_path)
    assert Counter(n['name'] for n in before.data['nodes'])==Counter(n['name'] for n in after.data['nodes'])
    assert all(count==1 for count in Counter(n['name'] for n in after.data['nodes']).values())
    for key in ['asset','extensionsUsed','extensionsRequired','extensions','scene','scenes','cameras']:
        assert before.data.get(key)==after.data.get(key),('Scene/camera/light contract changed',key)
    previous={m['name']:i for i,m in enumerate(before.data['materials'])}
    current={m['name']:i for i,m in enumerate(after.data['materials'])}
    assert previous.keys()==current.keys()
    old_moon=before.material(previous[MATERIAL])
    new_moon=after.material(current[MATERIAL])
    pbr=new_moon['pbrMetallicRoughness']
    assert pbr['baseColorTexture']['index']==new_moon['emissiveTexture']['index']
    assert pbr['baseColorTexture']['index']['image_sha256']==atlas['png_sha256']
    assert all(abs(v-atlas['base_factor'])<1e-6 for v in pbr['baseColorFactor'][:3])
    strength=new_moon.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength',1)
    assert all(abs(v*strength-atlas['emission_factor']*atlas['emission_strength'])<1e-6 for v in new_moon['emissiveFactor'])
    assert pbr['baseColorFactor'][:3]!=old_moon['pbrMetallicRoughness']['baseColorFactor'][:3]
    assert new_moon['emissiveFactor']!=old_moon['emissiveFactor']
    # Replace just the two allowed RGB arrays before complete comparison.
    normalized=copy.deepcopy(new_moon)
    normalized['pbrMetallicRoughness']['baseColorFactor'][:3]=old_moon['pbrMetallicRoughness']['baseColorFactor'][:3]
    normalized['emissiveFactor']=old_moon['emissiveFactor']
    assert normalized==old_moon,'Moon texture/sampler/alpha/sidedness/roughness contract changed'
    for name in previous:
        if name!=MATERIAL:assert before.material(previous[name])==after.material(current[name]),('Unrelated material changed',name)
    changed=[]
    for name in before.nodes:
        a,b=before.node(name),after.node(name)
        for primitive in b.get('mesh',[]):
            if primitive.get('material',{}).get('name')==MATERIAL:
                primitive['material']=copy.deepcopy(old_moon)
                changed.append(name)
        assert a==b,('Geometry/UV/index/camera/light/extras/transform contract changed',name)
    assert set(changed)=={'SITE_stage_MAT_painted_moon'}
    return {'source_before_sha256':hashlib.sha256(before.blob).hexdigest(),'candidate_sha256':hashlib.sha256(after.blob).hexdigest(),'complete_node_contracts_checked':len(before.nodes),'unchanged_materials':len(previous)-1,'original_paint_sha256':atlas['png_sha256'],'base_factor':atlas['base_factor'],'emission_factor':atlas['emission_factor'],'target_mean_luminance_ratio':atlas['target_mean_luminance_ratio']}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--before-root',type=Path,required=True)
    parser.add_argument('--candidate-root',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    atlas=json.loads((args.candidate_root/'textures/backdrops/moon-paint/atlas.json').read_text())
    report=compare(args.before_root/'export/garden-of-dreams.glb',args.candidate_root/'export/garden-of-dreams.glb',atlas)
    report['stage']=compare(args.before_root/'export/sites/SITE_stage.glb',args.candidate_root/'export/sites/SITE_stage.glb',atlas)
    identical=[]
    for old in sorted((args.before_root/'export/sites').glob('SITE_*.glb')):
        if old.name=='SITE_stage.glb':continue
        assert old.read_bytes()==(args.candidate_root/'export/sites'/old.name).read_bytes(),old.name
        identical.append(old.name)
    assert len(identical)==14
    report.update(status='scratch_export_verified',byte_identical_other_site_exports=identical,scope='Actual whole/stage export preserves every complete resolved node contract, both UV channels, embedded image/sampler and other materials. Only moon base/emission RGB factors change. Not fresh lighting, installation or art/performance acceptance.')
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print('MOON_CONTRAST_EXPORT_PRESERVATION_PASS',report['complete_node_contracts_checked'],len(identical))

if __name__=='__main__':main()
