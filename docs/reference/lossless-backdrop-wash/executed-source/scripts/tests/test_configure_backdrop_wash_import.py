"""Changing the wash import must preserve pixels and unrelated generated files."""
from pathlib import Path
import importlib.util
import tempfile
import unittest


NAME = 'SITE_stage_MAT_stage_cyclorama_moonlit_MAT_stage_atlas-front.png'


class BackdropWashImportTests(unittest.TestCase):
    def fixture(self, root):
        source = root / 'lightmaps/backdrop-wash' / NAME
        source.parent.mkdir(parents=True)
        source.write_bytes(b'original native wash pixels')
        caches = root / '.godot/imported'
        caches.mkdir(parents=True)
        stem = NAME + '-abc'
        source.with_suffix('.png.import').write_text(
            '[remap]\npath.s3tc="res://.godot/imported/' + stem + '.s3tc.ctex"\n'
            'path.etc2="res://.godot/imported/' + stem + '.etc2.ctex"\n'
            '\n[params]\ncompress/mode=2\nprocess/size_limit=256\n'
            'mipmaps/generate=false\ndetect_3d/compress_to=1\n')
        for suffix in ['.s3tc.ctex', '.etc2.ctex', '.md5']:
            (caches / (stem + suffix)).write_bytes(b'old generated lighting')
        (caches / 'other.ctex').write_bytes(b'other lighting')
        return source

    def configure(self, root):
        path = Path(__file__).resolve().parents[1] / 'configure_backdrop_wash_import.py'
        self.assertTrue(path.exists(), 'Backdrop lossless import configurator missing')
        spec = importlib.util.spec_from_file_location('wash_import', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.configure(root)

    def test_lossless_reimport_invalidates_only_owned_caches(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            self.configure(root)
            self.assertEqual(source.read_bytes(), b'original native wash pixels')
            parameters = source.with_suffix('.png.import').read_text()
            for setting in ['compress/mode=0', 'process/size_limit=256',
                            'mipmaps/generate=false', 'detect_3d/compress_to=0']:
                self.assertIn(setting + '\n', parameters)
            self.assertEqual(list((root / '.godot/imported').glob(NAME + '-*')), [])
            self.assertEqual((root / '.godot/imported/other.ctex').read_bytes(), b'other lighting')

    def test_malformed_parameter_causes_no_partial_write_or_cache_removal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            sidecar = source.with_suffix('.png.import')
            sidecar.write_text(sidecar.read_text().replace('mipmaps/generate=false\n', ''))
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaises(AssertionError):
                self.configure(root)
            self.assertEqual({str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}, before)

    def test_cache_escape_is_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.fixture(root)
            sidecar = source.with_suffix('.png.import')
            sidecar.write_text(sidecar.read_text().replace('res://.godot/imported/', 'res://../outside/'))
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaises(AssertionError):
                self.configure(root)
            self.assertEqual({str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}, before)


if __name__ == '__main__':
    unittest.main()
