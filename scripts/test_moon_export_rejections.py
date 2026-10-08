"""Exercise moon export preservation against physical/material corruptions."""
import argparse
import copy
import json
import struct
import tempfile
from pathlib import Path

from gltf_paint_contract import share_moon_texture
from verify_moon_export import compare
from verify_mountain_export import Glb

parser = argparse.ArgumentParser()
parser.add_argument('--before', type=Path, required=True)
parser.add_argument('--candidate', type=Path, required=True)
parser.add_argument('--legacy', type=Path)
parser.add_argument('--report', type=Path, required=True)
args = parser.parse_args()
compare(args.before, args.candidate)
candidate = Glb(args.candidate)
cases = []

def write(document, path):
    data = json.dumps(document, separators=(',', ':')).encode()
    data += b' ' * (-len(data) % 4)
    tail = struct.pack('<II', len(candidate.binary), 0x004e4942) + candidate.binary
    path.write_bytes(struct.pack('<III', 0x46546c67, 2, 20 + len(data) + len(tail))
                     + struct.pack('<II', len(data), 0x4e4f534a) + data + tail)

def reject(name, operation):
    try:
        operation()
    except AssertionError as error:
        cases.append({'case': name, 'rejected': True, 'reason': str(error)})
    else:
        raise AssertionError('Accepted corruption: ' + name)

with tempfile.TemporaryDirectory(prefix='garden-moon-export-rejections-') as folder:
    for name in ['camera', 'collider', 'unrelated-material', 'moon-factor']:
        document = copy.deepcopy(candidate.doc)
        if name == 'camera':
            document['cameras'][0]['perspective']['yfov'] += .02
        elif name == 'collider':
            node = next(n for n in document['nodes'] if n.get('name', '').startswith('COL_'))
            if 'matrix' in node:
                node['matrix'][12] += .25
            else:
                node.setdefault('translation', [0, 0, 0])[0] += .25
        elif name == 'unrelated-material':
            material = next(m for m in document['materials'] if m['name'] != 'MAT_painted_moon')
            material['doubleSided'] = not material.get('doubleSided', False)
        else:
            next(m for m in document['materials'] if m['name'] == 'MAT_painted_moon')['emissiveFactor'][0] *= .5
        path = Path(folder) / (name + '.glb')
        write(document, path)
        reject(name, lambda: compare(args.before, path))
    if args.legacy:
        reject('actual-legacy-node-export', lambda: compare(args.before, args.legacy))
    document = copy.deepcopy(candidate.doc)
    moon = next(m for m in document['materials'] if m['name'] == 'MAT_painted_moon')
    index = moon['emissiveTexture']['index']
    other = next(i for i, texture in enumerate(document['textures'])
                 if i != index and texture['source'] != document['textures'][index]['source'])
    moon['emissiveTexture']['index'] = other
    reject('different-shared-image', lambda: share_moon_texture(document, candidate.bytes))
args.report.write_text(json.dumps({
    'scope': 'Injected camera/collision/material/factor/image corruptions reject; optional actual legacy dropped-factor export rejects. Production files unchanged.',
    'cases': cases}, indent=2) + '\n')
print('MOON_EXPORT_REJECTIONS_PASS', len(cases))
