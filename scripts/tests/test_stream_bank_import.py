"""The repaired small bank charts must survive runtime texture import."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
NAME = 'SITE_qinfang-ting_MAT_pavilion_atlas'
UV = 'e1952d9274d5e60ba949b334873e59b93ab621ed62f19f0f64733b4ac169562b'


class StreamBankImport(unittest.TestCase):
    def test_repaired_bank_charts_keep_the_reviewed_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'scripts').mkdir()
            maps = root/'godot/lightmaps'
            maps.mkdir(parents=True)
            shutil.copy2(ROOT/'scripts/configure_lightmap_imports.py', root/'scripts')
            (maps/'full-index.json').write_text(json.dumps({NAME: {'uv_sha256': UV}}))
            sidecar = maps/(NAME+'.png.import')
            sidecar.write_text('[params]\ncompress/mode=2\ncompress/high_quality=false\nprocess/size_limit=256\nmipmaps/generate=false\n')
            subprocess.run([sys.executable, root/'scripts/configure_lightmap_imports.py', '--size-limit', '256'], check=True, capture_output=True)
            self.assertIn('process/size_limit=1024', sidecar.read_text())
            self.assertIn('compress/mode=0', sidecar.read_text())


if __name__ == '__main__':
    unittest.main()
