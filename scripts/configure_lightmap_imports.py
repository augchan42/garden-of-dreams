"""Set reproducible GPU import settings without modifying source Cycles PNGs.

Run Godot --headless --editor --import afterwards. Size limits are runtime-only.
"""
import argparse
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser()
parser.add_argument('--size-limit', type=int, default=512, choices=[0, 256, 512, 1024])
parser.add_argument('--uncompressed', action='store_true')
parser.add_argument('--demo', action='store_true', help='Configure only the first-reading demo maps')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
paths = sorted((root / 'godot/lightmaps').glob('*.png.import'))
if args.demo:
    records = json.loads((root / 'godot/lightmaps/demo-index.json').read_text())
    names = {record['texture'] + '.import' for record in records.values()}
    paths = [path for path in paths if path.name in names]
    assert len(paths) == len(records), 'Import every demo map before configuring it'
assert paths, 'Import the PNGs once before configuring their settings'
settings = {
    'compress/mode': '0' if args.uncompressed else '2',
    'compress/high_quality': 'false',
    'process/size_limit': str(args.size_limit),
    # Keep the baseline filtering while testing compression in isolation.
    'mipmaps/generate': 'false',
}
for path in paths:
    contents = path.read_text()
    for key, value in settings.items():
        contents, count = re.subn(r'^' + re.escape(key) + r'=.*$', key+'='+value,
                                 contents, flags=re.MULTILINE)
        assert count == 1, (path, key, count)
    path.write_text(contents)
print(f'Configured {len(paths)} lightmaps: {settings}')
