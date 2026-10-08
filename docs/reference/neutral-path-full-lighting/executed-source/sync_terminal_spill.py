"""Install only a completely validated current-source indirect spill catalog."""
import argparse
import json
from pathlib import Path
import shutil

from terminal_spill_catalog import validate_catalog

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=ROOT / 'export/lightmaps/terminal-spill')
options = parser.parse_args()
records = validate_catalog(ROOT, options.source)
destination = ROOT / 'godot/lightmaps/terminal-spill'
destination.mkdir(parents=True, exist_ok=True)
for record in records.values():
    name = record['mesh']
    for extension in ('.png', '.json'):
        shutil.copy2(options.source / (name + extension), destination / (name + extension))
shutil.copy2(options.source / 'manifest.json', destination / 'manifest.json')
(destination.parent / 'terminal-spill-index.json').write_text(json.dumps(records, indent=2) + '\n')
print('TERMINAL_SPILL_CATALOG_PASS', len(records), 'all source and PNG checks completed before copying')
