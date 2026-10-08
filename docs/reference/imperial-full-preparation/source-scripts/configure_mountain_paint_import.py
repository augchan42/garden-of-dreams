"""Cap the shared mountain painting after Godot has created its import sidecar."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--project', type=Path, default=ROOT / 'godot')
args = parser.parse_args()
path = args.project / 'materials/stage/mountain-paint.png.import'
contents = path.read_text()
for key, value in {'compress/mode': '0', 'mipmaps/generate': 'true',
                   'process/size_limit': '512', 'detect_3d/compress_to': '0'}.items():
    contents, count = re.subn(r'^' + re.escape(key) + r'=.*$', key + '=' + value, contents, flags=re.MULTILINE)
    assert count == 1, (path, key, count)
path.write_text(contents)
print('MOUNTAIN_PAINT_IMPORT_CONFIGURED: lossless, 512px, mipmaps, no automatic compression')
