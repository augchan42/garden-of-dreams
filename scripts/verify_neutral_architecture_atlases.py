"""Check candidate atlas palette, UV layout and original PBR surface maps."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from garden_material_palette import COMMON_BASE_COLORS

parser = argparse.ArgumentParser()
parser.add_argument('--baseline-root', type=Path, required=True)
parser.add_argument('--candidate-root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
report = {'status':'candidate_neutral_architecture_atlases_verified_not_installed',
          'scope':'CPU procedural atlas generation only. Scene attachment and native lighting/art acceptance remain required.', 'atlases':{}}
for kind in ['pavilion','wall']:
    old=args.baseline_root/'textures/atlases'/kind
    new=args.candidate_root/'textures/atlases'/kind
    a=json.loads((old/'atlas.json').read_text())
    b=json.loads((new/'atlas.json').read_text())
    assert 'base_colors_linear' in b, 'Palette manifest missing expected colors'
    assert a['size']==b['size']==[2048,2048]
    assert a['uv_regions']==b['uv_regions'] and a['padding_pixels']==b['padding_pixels']==32
    assert a['orm_channels']==b['orm_channels']
    rows={}
    for channel in ['normal','orm']:
        p=old/(kind+'_'+channel+'.png')
        q=new/(kind+'_'+channel+'.png')
        assert p.read_bytes()==q.read_bytes(), ('PBR surface map changed',kind,channel)
        rows[channel]={'byte_identical':True,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
    before=np.asarray(Image.open(old/(kind+'_basecolor.png')))
    after=np.asarray(Image.open(new/(kind+'_basecolor.png')))
    assert before.shape==after.shape==(2048,2048,3)
    assert np.array_equal(before[1024:,1024:],after[1024:,1024:]), ('Bronze/unused quarter changed',kind)
    changed_regions=[]
    for name,uv in b['uv_regions'].items():
        x,y,w,h=uv
        left,right=int(round(x*2048)),int(round((x+w)*2048))
        top,bottom=int(round((1-y-h)*2048)),int(round((1-y)*2048))
        pixels=after[top:bottom,left:right]/255.
        linear=np.where(pixels<=.04045,pixels/12.92,((pixels+.055)/1.055)**2.4)
        target=np.asarray(b['base_colors_linear'][name])
        if name in COMMON_BASE_COLORS:
            assert np.array_equal(target,COMMON_BASE_COLORS[name]), ('Wrong palette',name)
        assert np.max(np.abs(linear.mean(axis=(0,1))-target))<.006, ('Swatch does not match recorded color',kind,name)
        changed=not np.array_equal(before[top:bottom,left:right],after[top:bottom,left:right])
        if name!='MAT_bronze':
            assert changed
            changed_regions.append(name)
        else:
            assert not changed
    assert all(hashlib.sha256((new/name).read_bytes()).hexdigest()==digest for name,digest in b['files'].items())
    rows['basecolor']={'sha256':hashlib.sha256((new/(kind+'_basecolor.png')).read_bytes()).hexdigest(),
                      'changed_swatches':changed_regions,'bronze_or_unused_quarter_unchanged':True}
    report['atlases'][kind]={'size':[2048,2048],'uv_regions_preserved':True,'padding_pixels':32,
                            'base_colors_linear':b['base_colors_linear'],'channels':rows}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('NEUTRAL_ATLAS_PRESERVATION_PASS')
