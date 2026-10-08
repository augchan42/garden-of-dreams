"""Bake the eight later sites and shared stage from the current assembly.

This writes source lightmap data only. Engine installation and visual acceptance
are separate checks; authoring and the canonical GLB are never edited here.
"""
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'export/garden-of-dreams.glb'
DIGEST = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
SITES = ('aojing-guan', 'daoxiang-cun', 'hengwu-yuan', 'longcui-an',
         'ouxiang-xie', 'xiaoxiang-guan', 'yihong-yuan', 'ziling-zhou', 'stage')
for site in SITES:
    print('REMAINING_BAKE_START', site, DIGEST, flush=True)
    with open('/tmp/garden-remaining-bake-' + site + '.log', 'w') as log:
        result = subprocess.run([
            '/Applications/Blender.app/Contents/MacOS/Blender', '--background',
            '--threads', '8', '--python-exit-code', '1', '--python',
            str(ROOT / 'scripts/bake_lightmaps.py'), '--', '--site', site,
            '--size', '1024', '--samples', '128'], cwd=ROOT,
            stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        print('REMAINING_BAKE_FAILED', site, result.returncode, flush=True)
        sys.exit(result.returncode)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == DIGEST, 'Source changed during bake'
    print('REMAINING_BAKE_DONE', site, flush=True)
print('REMAINING_SOURCE_BAKES_COMPLETE', DIGEST, flush=True)
