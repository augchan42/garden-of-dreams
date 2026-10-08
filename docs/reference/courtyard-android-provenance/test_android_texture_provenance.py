import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from android_texture_provenance import texture_input_snapshot, verify_texture_inputs


class TextureProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        (self.root/'lightmaps').mkdir()
        self.source = self.root/'lightmaps/wall.png'
        self.source.write_bytes(b'unchanged source image')
        self.sidecar = self.source.with_suffix('.png.import')
        self.sidecar.write_text('[remap]\nimporter="texture"\n\n[params]\ncompress/mode=2\nprocess/size_limit=256\n')
        self.expected = texture_input_snapshot(self.root)

    def test_same_inputs_are_accepted(self):
        verify_texture_inputs(self.root, self.expected, 'Production')

    def test_import_change_rejects_even_when_source_is_identical(self):
        self.sidecar.write_text(self.sidecar.read_text().replace('compress/mode=2', 'compress/mode=0'))
        self.assertEqual(texture_input_snapshot(self.root)['lightmaps/wall.png']['source_sha256'],
                         self.expected['lightmaps/wall.png']['source_sha256'])
        with self.assertRaisesRegex(AssertionError, 'texture inputs changed'):
            verify_texture_inputs(self.root, self.expected, 'Production')

    def test_source_change_rejects(self):
        self.source.write_bytes(b'different source image')
        with self.assertRaisesRegex(AssertionError, 'texture inputs changed'):
            verify_texture_inputs(self.root, self.expected, 'Production')

    def test_missing_import_rejects(self):
        self.sidecar.unlink()
        with self.assertRaisesRegex(AssertionError, 'No texture input records'):
            verify_texture_inputs(self.root, self.expected, 'Production')

    def test_added_texture_rejects(self):
        other = self.root/'lightmaps/timber.png'
        other.write_bytes(b'timber source')
        other.with_suffix('.png.import').write_bytes(self.sidecar.read_bytes())
        with self.assertRaisesRegex(AssertionError, 'texture input set changed'):
            verify_texture_inputs(self.root, self.expected, 'Production')

    def test_platform_remap_changes_raw_import_fingerprint(self):
        self.sidecar.write_text(self.sidecar.read_text().replace('[remap]', '[remap]\npath.etc2="res://.godot/imported/wall.etc2.ctex"'))
        actual=texture_input_snapshot(self.root)['lightmaps/wall.png']
        self.assertEqual(actual['parameters_sha256'], self.expected['lightmaps/wall.png']['parameters_sha256'])
        self.assertNotEqual(actual['import_sha256'], self.expected['lightmaps/wall.png']['import_sha256'])
        with self.assertRaisesRegex(AssertionError, 'texture inputs changed'):
            verify_texture_inputs(self.root, self.expected, 'Staged')

    def test_excluded_test_fixture_is_not_an_apk_texture_input(self):
        folder=self.root/'tests/fixtures'
        folder.mkdir(parents=True)
        source=folder/'sun.png'
        source.write_bytes(b'test-only image')
        source.with_suffix('.png.import').write_bytes(self.sidecar.read_bytes())
        verify_texture_inputs(self.root, self.expected, 'Production')


if __name__ == '__main__':
    unittest.main()
