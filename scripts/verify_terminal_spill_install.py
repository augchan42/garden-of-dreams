"""Exercise stale/changed spill rejection through the real installer CLI."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from terminal_spill_catalog import validate_catalog

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'export/lightmaps/terminal-spill'
manifest = json.loads((source / 'manifest.json').read_text())
assert len(validate_catalog(ROOT, source)) == 7


def installed_hashes():
    paths = list((ROOT / 'godot/lightmaps/terminal-spill').iterdir())
    paths.append(ROOT / 'godot/lightmaps/terminal-spill-index.json')
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


before = installed_hashes()
results = []
for change in ('authoring_blend_sha256', 'terminal_blend_sha256', 'uv_sha256', 'png', 'adaptive_sampling'):
    with tempfile.TemporaryDirectory(prefix='garden-spill-rejection-') as folder:
        candidate = Path(folder) / 'spill'
        shutil.copytree(source, candidate)
        bad = copy.deepcopy(manifest)
        last = sorted(bad['records'])[-1]
        if change in ('authoring_blend_sha256', 'terminal_blend_sha256'):
            bad[change] = '0' * 64
        elif change == 'uv_sha256':
            bad['records'][last]['uv_sha256'] = '0' * 64
            (candidate / (last + '.json')).write_text(json.dumps(bad['records'][last]))
        elif change == 'png':
            png = candidate / bad['records'][last]['texture']
            content = bytearray(png.read_bytes())
            content[-1] ^= 1
            png.write_bytes(content)
        else:
            bad['adaptive_sampling'] = True
        (candidate / 'manifest.json').write_text(json.dumps(bad))
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/sync_terminal_spill.py'),
                                 '--source', str(candidate)], cwd=ROOT, text=True, capture_output=True)
        assert result.returncode != 0, ('Installer accepted invalid spill', change)
        assert installed_hashes() == before, ('Rejected spill changed engine files', change)
        results.append({'changed': change, 'rejected': True, 'engine_files_unchanged': True})
for record in manifest['records'].values():
    engine = ROOT / 'godot/lightmaps/terminal-spill' / record['texture']
    assert hashlib.sha256(engine.read_bytes()).hexdigest() == record['png_sha256']
report = {'manifest_sha256': hashlib.sha256((source / 'manifest.json').read_bytes()).hexdigest(),
          'installed_files_checked': len(before), 'negative_checks': results}
(ROOT / 'export/terminal-spill-provenance-check.json').write_text(json.dumps(report, indent=2) + '\n')
print('TERMINAL_SPILL_INSTALL_REJECTION_PASS', len(results), 'cases;', len(before), 'engine files unchanged')
