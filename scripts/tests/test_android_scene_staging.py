"""Android staging must retain scripts referenced by the production demo scene."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_android_profile as builder


class AndroidSceneStagingTests(unittest.TestCase):
    def test_staged_demo_keeps_its_referenced_acceptance_script(self):
        stage = getattr(builder, 'stage_tests', None)
        self.assertTrue(callable(stage), 'Android test dependency staging helper is missing')
        source = Path(__file__).resolve().parents[2] / 'godot'
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            stage(source, fixture, 'demo')
            expected = (source / 'tests/demo_release_acceptance.gd').read_bytes()
            self.assertEqual((fixture / 'tests/demo_release_acceptance.gd').read_bytes(), expected)
            self.assertTrue((fixture / 'tests/test_moon_runtime_import.gd').is_file())
            self.assertTrue((fixture / 'tests/profile_android.gd').is_file())
            self.assertFalse((fixture / 'tests/profile_android_full.gd').exists())


if __name__ == '__main__':
    unittest.main()
