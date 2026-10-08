"""CLI policy checks; fake source bytes test identity guards, not GLB rendering."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--script', type=Path, default=Path(__file__).with_name('configure_lightmap_imports.py'))
options, remaining = parser.parse_known_args()
TARGET = 'SITE_daguan-lou_MAT_rooftile'
UV = '001c6e9d40bd62cabdb887995a624e9ae5c7edcfddc0351f4016e59fc06f3989'
OTHER = 'SITE_ouxiang-xie_MAT_rooftile'
SETTINGS = 'compress/mode=2\ncompress/high_quality=false\nprocess/size_limit=256\nmipmaps/generate=false\n'

class ImperialImportPolicy(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='garden-import-policy-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ['scripts', 'godot/lightmaps', 'godot/assets', 'export']:
            (self.root / folder).mkdir(parents=True)
        self.script = self.root / 'scripts/configure_lightmap_imports.py'
        shutil.copy2(options.script, self.script)
        data = b'identity-only test fixture, not an actual GLB'
        self.digest = hashlib.sha256(data).hexdigest()
        for path in ['godot/assets/garden-of-dreams.glb', 'export/garden-of-dreams.glb']:
            (self.root / path).write_bytes(data)
        self.catalog = {TARGET: {'uv_sha256': UV, 'texture': TARGET + '.png', 'source_glb_sha256': self.digest}}
        self.save_catalog()
        for name in [TARGET, OTHER]:
            self.import_path(name).write_text(SETTINGS)

    def save_catalog(self):
        (self.root / 'godot/lightmaps/full-index.json').write_text(json.dumps(self.catalog))

    def import_path(self, name):
        return self.root / 'godot/lightmaps' / (name + '.png.import')

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(self.script), '--size-limit', '256', *args], capture_output=True, text=True)

    def test_default_cap_does_not_accept_exception(self):
        (self.root / 'godot/lightmaps/full-index.json').unlink()
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.import_path(TARGET).read_text(), SETTINGS)

    def test_verified_exception_preserves_other_roof(self):
        result = self.run_cli('--imperial-lossless512')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.import_path(TARGET).read_text(), SETTINGS.replace('compress/mode=2', 'compress/mode=0').replace('size_limit=256', 'size_limit=512'))
        self.assertEqual(self.import_path(OTHER).read_text(), SETTINGS)

    def test_wrong_uv_rejected_before_import_mutation(self):
        self.catalog[TARGET]['uv_sha256'] = '0' * 64
        self.save_catalog()
        result = self.run_cli('--imperial-lossless512')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('requires the verified tile charts', result.stderr)
        for name in [TARGET, OTHER]:
            self.assertEqual(self.import_path(name).read_text(), SETTINGS)

    def test_stale_engine_source_rejected_before_import_mutation(self):
        (self.root / 'godot/assets/garden-of-dreams.glb').write_bytes(b'older source')
        result = self.run_cli('--imperial-lossless512')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('catalog/source mismatch', result.stderr)
        for name in [TARGET, OTHER]:
            self.assertEqual(self.import_path(name).read_text(), SETTINGS)

if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *remaining])
