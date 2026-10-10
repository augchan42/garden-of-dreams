"""Run the real profiler writer with concurrent readers in isolated app data."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--godot', default='/Applications/Godot.app/Contents/MacOS/Godot')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    fixture = Path(tempfile.mkdtemp(prefix='garden-report-publication-'))
    (fixture / 'tests').mkdir()
    name = 'Garden Report Publication Regression ' + uuid.uuid4().hex
    (fixture / 'project.godot').write_text(
        'config_version=5\n[application]\nconfig/name="' + name +
        '"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    hashes = {}
    for filename in ['profile_android.gd', 'texture_binding_inventory.gd',
                     'test_profile_report_publication.gd', 'profile_report_store.gd', 'runtime_texture_caps.gd']:
        source = ROOT / 'godot/tests' / filename
        if source.exists():
            shutil.copy2(source, fixture / 'tests' / filename)
            hashes[filename] = hashlib.sha256(source.read_bytes()).hexdigest()
    log = args.output / 'engine.log'
    report = args.output / 'publication.json'
    with log.open('w') as stream:
        result = subprocess.run([args.godot, '--headless', '--path', str(fixture),
                                 '--script', 'res://tests/test_profile_report_publication.gd',
                                 '--', '--output=' + str(report.resolve())],
                                stdout=stream, stderr=subprocess.STDOUT, timeout=60)
    diagnostics = re.findall(r'^(?:SCRIPT ERROR|ERROR|WARNING):.*$', log.read_text(), re.MULTILINE)
    record = {'fixture': str(fixture), 'application_name': name,
              'source_sha256': hashes, 'exit_code': result.returncode,
              'engine_diagnostics': diagnostics,
              'report': json.loads(report.read_text()) if report.exists() else None}
    (args.output / 'run.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record['report']))
    raise SystemExit(result.returncode or bool(diagnostics) or
                     not record['report'] or record['report']['status'] != 'passed')


if __name__ == '__main__':
    main()
