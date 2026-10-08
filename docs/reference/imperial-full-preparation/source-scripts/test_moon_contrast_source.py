"""Reopen native source and reject accidental metadata/UV luminance drift."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from moon_paint_contract import OBJECT,check

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,required=True)
parser.add_argument('--report',type=Path,required=True)
parser.add_argument('--expected-target',type=float,default=.45)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=args.root/'blender/authoring.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source))
atlas_path=args.root/'textures/backdrops/moon-paint/atlas.json'
result=check(atlas_path)
atlas=json.loads(atlas_path.read_text())
assert abs(result['target_mean_luminance_ratio']-args.expected_target)<1e-9
assert hashlib.sha256((atlas_path.parent/'moon-paint.png').read_bytes()).hexdigest()==result['texture_sha256']
rejected=[]
def reject(label,function):
    try:function()
    except AssertionError:rejected.append(label)
    else:raise AssertionError(('Accepted accidental moon drift',label))
with tempfile.TemporaryDirectory(prefix='garden-moon-contrast-rejections-') as folder:
    for label,mutate in [
        ('missing lower-luminance intent',lambda a:a.pop('target_mean_luminance_ratio')),
        ('false equal-luminance intent',lambda a:a.update(target_mean_luminance_ratio=1)),
        ('boolean luminance intent',lambda a:a.update(target_mean_luminance_ratio=True)),
        ('wrong packed image',lambda a:a.update(png_sha256='0'*64)),
        ('unrequested image resize',lambda a:a.update(image_size=[512,512])),
        ('wrong base factor',lambda a:a.update(base_factor=a['base_factor']*.8)),
    ]:
        altered=copy.deepcopy(atlas);mutate(altered)
        p=Path(folder)/(label+'.json');p.write_text(json.dumps(altered))
        reject(label,lambda:check(p))
    uv=bpy.data.objects[OBJECT].data.uv_layers[0].data[0].uv
    previous=uv.copy();uv.x+=.01
    reject('moon primary UV drift',lambda:check(atlas_path))
    uv[:]=previous
assert check(atlas_path)==result
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
result.update(status='saved_source_verified',source_sha256=digest,atlas_sha256=hashlib.sha256(atlas_path.read_bytes()).hexdigest(),helper_sha256=hashlib.sha256((Path(__file__).parent/'moon_paint_contract.py').read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rejected=rejected,scope='Actually reopened source and original packed painting, full primary UV mapping and requested source-luminance intent. Rejected metadata/UV corruptions are in-memory or temporary; source unmodified. Not lighting or final art acceptance.')
args.report.write_text(json.dumps(result,indent=2)+'\n')
print('MOON_CONTRAST_SAVED_SOURCE_PASS',len(rejected),'rejections')
