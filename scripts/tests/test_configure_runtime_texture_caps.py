"""The cap configurator must preserve source pixels and unrelated cache files."""
from pathlib import Path
import importlib.util
import sys
import tempfile
import subprocess
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class RuntimeCapConfigurationTests(unittest.TestCase):
    def fixture(self, root):
        (root / 'assets').mkdir(); (root / '.godot/imported').mkdir(parents=True)
        for name in ['pavilion_basecolor', 'wall_basecolor', 'gate-inscription', 'gate-inscription-normal']:
            source = root / ('assets/garden-of-dreams_' + name + '.png'); source.write_bytes(b'original pixels')
            stem = source.name + '-abc'
            formats = ['s3tc.ctex', 'etc2.ctex'] if 'basecolor' in name else ['ctex']
            paths = ''.join('path.' + str(i) + '="res://.godot/imported/' + stem + '.' + fmt + '"\n' for i, fmt in enumerate(formats))
            source.with_suffix('.png.import').write_text('[remap]\nimporter="texture"\n' + paths + '\n[params]\ncompress/mode=' + ('2' if 'basecolor' in name else '0') + '\nmipmaps/generate=true\ndetect_3d/compress_to=0\nprocess/size_limit=0\n')
            for ext in formats + ['md5']: (root / '.godot/imported' / (stem + '.' + ext)).write_bytes(b'old generated file')
        (root / '.godot/imported/unrelated.ctex').write_bytes(b'other pixels')

    def configurator(self):
        path = Path(__file__).resolve().parents[1] / 'configure_runtime_texture_caps.py'
        self.assertTrue(path.exists(), 'Runtime cap configurator is not implemented')
        spec = importlib.util.spec_from_file_location('caps', path); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module.configure

    def test_caps_rebuild_only_owned_caches_and_preserve_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.fixture(root); configure = self.configurator(); configure(root)
            for name, size in [('pavilion_basecolor', 1024), ('wall_basecolor', 1024), ('gate-inscription', 512), ('gate-inscription-normal', 512)]:
                source = root / ('assets/garden-of-dreams_' + name + '.png')
                self.assertEqual(source.read_bytes(), b'original pixels')
                self.assertIn('process/size_limit=' + str(size) + '\n', source.with_suffix('.png.import').read_text())
                self.assertEqual(list((root / '.godot/imported').glob(source.name + '-*')), [])
            self.assertEqual((root / '.godot/imported/unrelated.ctex').read_bytes(), b'other pixels')

    def test_legacy_gate_command_uses_current_caps_without_changing_atlases(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.fixture(root)
            script = Path(__file__).resolve().parents[1] / 'configure_gate_inscription_imports.py'
            subprocess.run([sys.executable, str(script), '--project', str(root)],
                           check=True, capture_output=True)
            for name in ['gate-inscription', 'gate-inscription-normal']:
                source = root / ('assets/garden-of-dreams_' + name + '.png')
                self.assertIn('process/size_limit=512\n', source.with_suffix('.png.import').read_text())
                self.assertEqual(list((root / '.godot/imported').glob(source.name + '-*')), [])
            for name in ['pavilion_basecolor', 'wall_basecolor']:
                source = root / ('assets/garden-of-dreams_' + name + '.png')
                self.assertIn('process/size_limit=0\n', source.with_suffix('.png.import').read_text())
                self.assertTrue(list((root / '.godot/imported').glob(source.name + '-*')))

    def test_invalid_fourth_import_causes_no_partial_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.fixture(root); configure = self.configurator()
            bad = root / 'assets/garden-of-dreams_gate-inscription-normal.png.import'
            bad.write_text(bad.read_text().replace('compress/mode=0', 'compress/mode=2'))
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaises(AssertionError): configure(root)
            self.assertEqual({str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}, before)

    def test_cache_path_outside_project_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.fixture(root); configure = self.configurator()
            bad = root / 'assets/garden-of-dreams_pavilion_basecolor.png.import'
            bad.write_text(bad.read_text().replace('res://.godot/imported/', 'res://../outside/'))
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaises(AssertionError): configure(root)
            self.assertEqual({str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}, before)


if __name__ == '__main__': unittest.main()
