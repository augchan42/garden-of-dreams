"""Set reproducible GPU import settings without modifying source Cycles PNGs.

Run Godot --headless --editor --import afterwards. Size limits are runtime-only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser()
parser.add_argument('--size-limit', type=int, default=512, choices=[0, 256, 512, 1024])
parser.add_argument('--facade-size-limit', type=int, default=512, choices=[0, 256, 512, 1024],
                    help='Runtime cap for the lossless Xiaoxiang wall and timber maps')
parser.add_argument('--uncompressed', action='store_true')
parser.add_argument('--imperial-lossless512', action='store_true',
                    help='Use the verified Daguan tile charts with a lossless 512px roof map')
parser.add_argument('--demo', action='store_true', help='Configure only the first-reading demo maps')
parser.add_argument('--index', choices=['demo-index.json', 'priority2-index.json', 'full-index.json', 'backdrop-wash-index.json', 'terminal-spill-index.json'], help='Configure only a current bake catalog')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
imperial_name = 'SITE_daguan-lou_MAT_rooftile'
if args.imperial_lossless512:
    record = json.loads((root / 'godot/lightmaps/full-index.json').read_text())[imperial_name]
    assert record['uv_sha256'] == '001c6e9d40bd62cabdb887995a624e9ae5c7edcfddc0351f4016e59fc06f3989', 'Imperial import requires the verified tile charts'
    assert record['texture'] == imperial_name + '.png'
    for source in [root / 'export/garden-of-dreams.glb', root / 'godot/assets/garden-of-dreams.glb']:
        assert hashlib.sha256(source.read_bytes()).hexdigest() == record['source_glb_sha256'], 'Imperial catalog/source mismatch'
paths = sorted((root / 'godot/lightmaps').rglob('*.png.import'))
if args.demo or args.index:
    records = json.loads((root / 'godot/lightmaps' / (args.index or 'demo-index.json')).read_text())
    names = {side['texture'] + '.import' for record in records.values()
             for side in record.get('sides', {'front': record}).values()}
    paths = [path for path in paths if path.relative_to(root/'godot/lightmaps').as_posix() in names]
    assert len(paths) == len(names), 'Import every catalog map before configuring it'
assert paths, 'Import the PNGs once before configuring their settings'
settings = {
    'compress/mode': '0' if args.uncompressed else '2',
    'compress/high_quality': 'false',
    'process/size_limit': str(args.size_limit),
    # Keep the baseline filtering while testing compression in isolation.
    'mipmaps/generate': 'false',
}
facade_maps = {
    'SITE_xiaoxiang-guan_MAT_whitewash.png.import',
    'SITE_xiaoxiang-guan_MAT_lattice_wood.png.import',
}
for path in paths:
    contents = path.read_text()
    # RGB blocks visibly dither the broad, dark mountain gradients. BPTC fixes
    # the pattern but this Mac decodes it to RGBA8 anyway. Use lossless import
    # for these nine small maps, keeping the same cap and other maps compressed.
    mountain = path.name.startswith('SITE_stage_MAT_painted_mountains_')
    # Block compression introduces pink checks in these courtyard shadows.
    # Lossless 512 retains the wall detail; the 256px timber source is not enlarged.
    facade = path.name in facade_maps
    imperial = args.imperial_lossless512 and path.name == imperial_name + '.png.import'
    per_map_settings = {
        **settings,
        'compress/mode': '0' if mountain or facade or imperial else settings['compress/mode'],
        'process/size_limit': '512' if imperial else str(args.facade_size_limit) if facade else settings['process/size_limit'],
    }
    for key, value in per_map_settings.items():
        contents, count = re.subn(r'^' + re.escape(key) + r'=.*$', key+'='+value,
                                 contents, flags=re.MULTILINE)
        assert count == 1, (path, key, count)
    path.write_text(contents)
lossless_mountains = sum(path.name.startswith('SITE_stage_MAT_painted_mountains_') for path in paths)
lossless_facades = sum(path.name in facade_maps for path in paths)
lossless_imperial = sum(args.imperial_lossless512 and path.name == imperial_name + '.png.import' for path in paths)
print(f'Configured {len(paths)} lightmaps: {settings}; '
      f'{lossless_mountains} mountain maps use lossless import; '
      f'{lossless_facades} courtyard maps use lossless import with cap {args.facade_size_limit}; '
      f'{lossless_imperial} imperial roof maps use lossless 512px import')
