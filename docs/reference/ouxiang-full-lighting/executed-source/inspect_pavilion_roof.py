"""Sample roof albedo and native-precision irradiance for a matching GLB/map pair.

This is a centroid diagnostic, not a rendered visibility or art-acceptance test.
Uses installed FFmpeg to retain the RGB16 PNG samples that Pillow would truncate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess

import numpy as np
from PIL import Image

from verify_mountain_export import Glb

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=ROOT / 'export/garden-of-dreams.glb')
parser.add_argument('--maps', type=Path, default=ROOT / 'godot/lightmaps')
parser.add_argument('--output', type=Path, default=ROOT / 'export/pavilion-roof-source-diagnosis.json')
args = parser.parse_args()
glb = Glb(args.source)
name = 'SITE_qinfang-ting_MAT_pavilion_atlas'
node = next(n for n in glb.doc['nodes'] if n.get('name') == name)
# Node rotation is solely around world up, so local normal Y is world normal Y.
assert node['rotation'][0] == node['rotation'][2] == 0
primitive = glb.doc['meshes'][node['mesh']]['primitives'][0]
attributes = {k: glb.accessor(v) for k, v in primitive['attributes'].items()}
indices = glb.accessor(primitive['indices']).ravel().reshape(-1, 3)
positions = attributes['POSITION'][indices]
normal = np.cross(positions[:, 1] - positions[:, 0], positions[:, 2] - positions[:, 0])
area = np.linalg.norm(normal, axis=1)
normal /= np.maximum(area[:, None], 1e-8)
smooth = attributes['NORMAL'][indices].mean(axis=1)
uv = attributes['TEXCOORD_0'][indices].mean(axis=1)
uv2 = attributes['TEXCOORD_1'][indices].mean(axis=1)
atlas = json.loads((ROOT / 'textures/atlases/pavilion/atlas.json').read_text())
x, y, w, h = atlas['uv_regions']['MAT_rooftile']
roof = (uv[:, 0] > x) & (uv[:, 0] < x + w) & (uv[:, 1] > 1 - y - h) & (uv[:, 1] < 1 - y)
record = json.loads((args.maps / (name + '.json')).read_text())
assert record['source_glb_sha256'] == hashlib.sha256(glb.bytes).hexdigest(), 'Use a matching source/map pair'
material = glb.doc['materials'][primitive['material']]
assert material['pbrMetallicRoughness'].get('baseColorFactor', [1] * 4) == [1] * 4
paint = np.asarray(Image.open(ROOT / 'textures/atlases/pavilion/pavilion_basecolor.png').convert('RGB'), dtype=float) / 255
path = args.maps / record['texture']
width, height, depth, color, _, _, interlace = struct.unpack('>IIBBBBB', path.read_bytes()[16:29])
assert depth == 16 and color == 2 and interlace == 0
decoded = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-i', str(path),
                          '-f', 'rawvideo', '-pix_fmt', 'rgb48le', '-'], check=True, capture_output=True).stdout
irradiance = np.frombuffer(decoded, dtype='<u2').reshape(height, width, 3).astype(float) / 65535


def sample(image, coords):
    yy = np.clip((coords[:, 1] * image.shape[0]).astype(int), 0, image.shape[0] - 1)
    xx = np.clip((coords[:, 0] * image.shape[1]).astype(int), 0, image.shape[1] - 1)
    return image[yy, xx]


albedo = sample(paint, uv)
albedo = np.where(albedo <= .04045, albedo / 12.92, ((albedo + .055) / 1.055) ** 2.4)
light = sample(irradiance, uv2) * record['scale']
weights = np.asarray([.2126, .7152, .0722])
report = {'scope': 'CPU roof triangle-centroid samples of matching source/native RGB16 irradiance. Omits realtime practicals, tone mapping, visibility and filtering; not final art acceptance.',
          'source_glb_sha256': hashlib.sha256(glb.bytes).hexdigest(),
          'lightmap_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
          'irradiance_bit_depth': depth, 'mesh': name, 'roof_triangle_count': int(roof.sum()), 'bins': {}}
for label, mask in {'upward': roof & (normal[:, 1] > .25),
                    'downward': roof & (normal[:, 1] < -.25),
                    'edge': roof & (abs(normal[:, 1]) <= .25)}.items():
    if not mask.any():
        report['bins'][label] = {'triangles': 0}
        continue
    a, light_samples = albedo[mask], light[mask]
    luminance = (a * light_samples * np.pi) @ weights
    report['bins'][label] = {'triangles': int(mask.sum()),
        'mean_linear_albedo_rgb': np.average(a, axis=0, weights=area[mask]).tolist(),
        'median_irradiance_rgb': np.median(light_samples, axis=0).tolist(),
        'baked_diffuse_luminance_quantiles': np.quantile(luminance, [0, .25, .5, .75, 1]).tolist(),
        'zero_light_fraction': float((light_samples.max(axis=1) == 0).mean()),
        'opposing_shading_normals_fraction': float(((smooth[mask] * normal[mask]).sum(axis=1) < 0).mean())}
args.output.write_text(json.dumps(report, indent=2) + '\n')
print('PAVILION_ROOF_DIAGNOSIS', json.dumps(report['bins']))
