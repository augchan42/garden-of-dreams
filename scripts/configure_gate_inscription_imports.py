"""Regenerate the aligned lossless gate pair at its current reviewed runtime cap."""
import argparse
from pathlib import Path
from configure_runtime_texture_caps import configure, TARGETS

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=ROOT / 'godot')
    args = parser.parse_args()
    gate_targets = {name: size for name, size in TARGETS.items() if 'gate-inscription' in name}
    configure(args.project, gate_targets)
    print('GATE_INSCRIPTION_IMPORTS_CONFIGURED: aligned lossless 512px color/normal, mipmaps; reimport required')


if __name__ == '__main__':
    main()
