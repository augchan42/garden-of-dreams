"""Inspect the actual shared native rig used by terminal indirect-spill bakes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from native_wash_scene import isolated_wash_scene

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,required=True)
parser.add_argument('--receivers',type=int,required=True,choices=[5,6])
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
rig=isolated_wash_scene(args.root.resolve(),128)
bpy.context.view_layer.update()
assert len(rig['receivers'].objects)==args.receivers
assert bpy.data.objects['SITE_qinfang-ting_MAT_plaster_rock'] not in list(rig['receivers'].objects)
for saved in rig['lighting']['lights']:
    light=bpy.data.objects[saved['name']]
    assert light.data.type=='AREA' and not light.hide_render
    assert set(light.light_linking.receiver_collection.objects)==set(rig['receivers'].objects)
    assert np.allclose(light.matrix_world,saved['matrix'],atol=1e-6)
    for key in ['shape','size','size_y','energy','color']:
        actual=getattr(light.data,key)
        assert actual==saved[key] if isinstance(actual,str) else np.allclose(actual,saved[key],atol=1e-6)
report={key:rig[key] for key in ['source_hash','stage_hash','authoring_hash','site_hashes','lighting','shadow_intent']}
report.update(scope='Actual native shared bake setup, receiver geometry/UV and exact reconstructed Area properties. No bake pixels or final art acceptance.',
              expected_receiver_count=args.receivers,receiver_count=len(rig['receivers'].objects),
              test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              helper_sha256=hashlib.sha256((Path(__file__).parent/'native_wash_scene.py').read_bytes()).hexdigest())
args.output.write_text(json.dumps(report,indent=2)+'\n')
print('NATIVE_SHARED_WASH_SCENE_PASS',args.receivers,'receivers, twelve exact Areas, no building receiver')
