"""Read the reviewed palette and texture expectations from an actual scene GLB."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
from garden_material_palette import COMMON_BASE_COLORS
from verify_mountain_export import Glb


def build(source, atlas_root):
    glb = Glb(source)
    materials = {m['name']:m for m in glb.doc['materials']}
    counts = Counter()
    for node in glb.doc['nodes']:
        if 'mesh' in node and not node.get('name', '').startswith('COL_'):
            for primitive in glb.doc['meshes'][node['mesh']]['primitives']:
                counts[glb.doc['materials'][primitive['material']]['name']] += 1
    plain = {}
    for name, rgb in COMMON_BASE_COLORS.items():
        material = materials[name]
        pbr = material['pbrMetallicRoughness']
        rgba = pbr.get('baseColorFactor', [1, 1, 1, 1])
        assert np.allclose(rgba, [*rgb, 1], atol=1e-7, rtol=0), ('Wrong plain palette', name)
        assert 'baseColorTexture' not in pbr and material.get('emissiveFactor', [0, 0, 0]) == [0, 0, 0]
        assert counts[name] > 0
        plain[name] = {'base_color_linear_rgba':rgba, 'source_surface_count':counts[name],
                       'roughness':pbr.get('roughnessFactor', 1), 'metallic':pbr.get('metallicFactor', 1)}
    atlases = {}
    for kind in ('pavilion', 'wall'):
        name = 'MAT_'+kind+'_atlas'
        material = materials[name]
        folder = atlas_root/'textures/atlases'/kind
        config = json.loads((folder/'atlas.json').read_text())
        assert 'base_colors_linear' in config, ('Reviewed atlas palette missing', kind)
        color_file = folder/(kind+'_basecolor.png')
        expected_hash = hashlib.sha256(color_file.read_bytes()).hexdigest()
        actual = glb.texture(material['pbrMetallicRoughness']['baseColorTexture']['index'])
        assert actual['source'] == expected_hash, ('Wrong embedded atlas color image', name)
        for channel, slot in [('normal', material['normalTexture']),
                              ('orm', material['pbrMetallicRoughness']['metallicRoughnessTexture'])]:
            assert glb.texture(slot['index'])['source'] == hashlib.sha256((folder/f'{kind}_{channel}.png').read_bytes()).hexdigest()
        swatches = {}
        for swatch, uv in config['uv_regions'].items():
            if swatch in COMMON_BASE_COLORS:
                assert config['base_colors_linear'][swatch] == list(COMMON_BASE_COLORS[swatch])
                swatches[swatch] = {'uv_region':uv, 'expected_linear_rgb':config['base_colors_linear'][swatch]}
        assert len(swatches) == 3 and counts[name] > 0
        atlases[name] = {'color_png_sha256':expected_hash,
                        'base_color_linear_rgba':material['pbrMetallicRoughness'].get('baseColorFactor', [1, 1, 1, 1]),
                        'source_surface_count':counts[name], 'swatches':swatches}
    return {'status':'reviewed_garden_palette_source_contract',
            'source_glb_sha256':hashlib.sha256(glb.bytes).hexdigest(),
            'plain_materials':plain, 'atlas_materials':atlases,
            'scope':'Actual GLB plain factors, embedded atlas hashes and non-collision source surface counts. Native import, shader bindings, decoded atlas colors and visual acceptance remain separate.'}


def main():
    parser = argparse.ArgumentParser()
    for flag in ('source', 'atlas-root', 'output'):
        parser.add_argument('--'+flag, type=Path, required=True)
    args = parser.parse_args()
    report = build(args.source, args.atlas_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('GARDEN_PALETTE_SOURCE_CONTRACT_PASS', report['source_glb_sha256'])


if __name__ == '__main__':
    main()
