"""Cap the runtime color/normal pair without editing the original gate artwork."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, default=ROOT / 'godot')
    args = parser.parse_args()
    prepared = {}
    for suffix in ('', '-normal'):
        path = args.project / 'assets' / f'garden-of-dreams_gate-inscription{suffix}.png.import'
        contents = path.read_text()
        for key, value in {'compress/mode': '0', 'mipmaps/generate': 'true',
                           'process/size_limit': '1024', 'detect_3d/compress_to': '0'}.items():
            contents, count = re.subn(r'^' + re.escape(key) + r'=.*$', key + '=' + value,
                                     contents, flags=re.MULTILINE)
            assert count == 1, (path, key, count)
        prepared[path] = contents
    for path, contents in prepared.items():
        path.write_text(contents)
    print('GATE_INSCRIPTION_IMPORTS_CONFIGURED: aligned lossless 1024px color/normal, mipmaps')


if __name__ == '__main__':
    main()
