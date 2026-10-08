"""Cold-import canonical source twice and verify independent source/physics contracts.

All cache deletion and corruption checks run in a newly created temporary project.
Production Godot assets and the running native lighting source are never modified.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
GODOT = '/Applications/Godot.app/Contents/MacOS/Godot'
fixture = Path(tempfile.mkdtemp(prefix='garden-source-reimport-'))
source = ROOT / 'export/garden-of-dreams.glb'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
report_path = ROOT / 'export/godot-reimport-checks.json'
report = {'status': 'running', 'source_glb_sha256': digest, 'fixture': str(fixture),
          'scope': 'Two forced cold imports: source camera/collider/marker contracts, one actual isolated ray per collider, all render mesh array persistence, calibrated keys and shared painted material/adapter properties. Not final baked lighting, rendered materials, continuous traversal or target-device acceptance.',
          'phases': []}


def save():
    report_path.write_text(json.dumps(report, indent=2) + '\n')


def run(name, arguments, rejection=None):
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest, 'Canonical source changed'
    log = fixture / (name + '.log')
    phase = {'name': name, 'status': 'running', 'log': str(log)}
    report['phases'].append(phase)
    save()
    print('REIMPORT_CHECK_START', name, flush=True)
    with log.open('w') as output:
        process = subprocess.Popen([GODOT, '--headless', '--path', str(fixture), *arguments],
                                   cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        phase['pid'] = process.pid
        save()
        code = process.wait()
    text = log.read_text()
    phase.update(exit_code=code, log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
    if rejection:
        passed = code == 1 and ('ERROR: ' + rejection) in text and 'SCRIPT ERROR:' not in text and 'WARNING:' not in text
    else:
        passed = code == 0 and not re.search(r'(?:SCRIPT )?ERROR:|WARNING:', text)
    phase['status'] = 'passed' if passed else 'failed'
    save()
    if not passed:
        raise RuntimeError(text[-4000:])
    print('REIMPORT_CHECK_PASS', name, flush=True)


try:
    for directory in ('materials', 'shaders'):
        shutil.copytree(ROOT / 'godot' / directory, fixture / directory)
    for material in (fixture / 'materials').rglob('*.tres'):
        for relative in re.findall(r'path="res://([^\"]+)"', material.read_text()):
            original, destination = ROOT / 'godot' / relative, fixture / relative
            if original.exists() and not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, destination)
                if Path(str(original) + '.import').exists():
                    shutil.copy2(str(original) + '.import', str(destination) + '.import')
    (fixture / 'tests').mkdir()
    (fixture / 'runtime').mkdir()
    for name in ('test_import_source_contract.gd', 'test_site_key_import.gd', 'test_mountain_paint.gd'):
        shutil.copy2(ROOT / 'godot/tests' / name, fixture / 'tests' / name)
    shutil.copy2(ROOT / 'godot/runtime/baked_materials.gd', fixture / 'runtime/baked_materials.gd')
    shutil.copy2(ROOT / 'godot/garden_import.gd', fixture / 'garden_import.gd')
    (fixture / 'assets').mkdir(exist_ok=True)
    shutil.copy2(source, fixture / 'assets/garden-of-dreams.glb')
    shutil.copy2(ROOT / 'godot/assets/garden-of-dreams.glb.import', fixture / 'assets/garden-of-dreams.glb.import')
    (fixture / 'project.godot').write_text('config_version=5\n\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    contract = fixture / 'tests/import-source-contract.json'
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_godot_import_contract.py'),
                    '--source', str(source), '--output', str(contract)], check=True, cwd=ROOT)
    report['source_contract_sha256'] = hashlib.sha256(contract.read_bytes()).hexdigest()
    report['test_script_sha256'] = hashlib.sha256((fixture / 'tests/test_import_source_contract.gd').read_bytes()).hexdigest()
    report['import_hook_sha256'] = hashlib.sha256((fixture / 'garden_import.gd').read_bytes()).hexdigest()
    run('first-cold-import', ['--editor', '--import'])
    for stage in ('first', 'second'):
        if stage == 'second':
            shutil.rmtree(fixture / '.godot')
            run('second-cold-import', ['--editor', '--import'])
        output = fixture / (stage + '-contract.json')
        run(stage + '-source-physics', ['--script', 'res://tests/test_import_source_contract.gd', '--',
                                      'res://assets/garden-of-dreams.glb', 'res://tests/import-source-contract.json', str(output)])
        run(stage + '-keys', ['--script', 'res://tests/test_site_key_import.gd', '--', 'res://assets/garden-of-dreams.glb'])
        run(stage + '-paint', ['--script', 'res://tests/test_mountain_paint.gd'])
    first = json.loads((fixture / 'first-contract.json').read_text())
    second = json.loads((fixture / 'second-contract.json').read_text())
    assert first == second, 'Forced reimport changed source/physics/mesh-array state'
    report['snapshot_sha256'] = hashlib.sha256(json.dumps(first['snapshot'], sort_keys=True).encode()).hexdigest()
    report['checked'] = {key: value for key, value in second.items() if key not in ('snapshot', 'scope')}
    for kind, message in (('camera', 'Camera FOV changed:'), ('collider', 'Collider surface changed:'),
                          ('marker', 'Room marker metadata changed:')):
        run('reject-' + kind, ['--script', 'res://tests/test_import_source_contract.gd', '--',
                             'res://assets/garden-of-dreams.glb', 'res://tests/import-source-contract.json',
                             str(fixture / ('negative-' + kind + '.json')), '--corrupt-' + kind], rejection=message)
    report['status'] = 'passed'
    save()
    print('GODOT_FORCED_REIMPORT_PASS', digest, flush=True)
except BaseException as error:
    report['status'] = 'failed'
    report['error'] = str(error)
    save()
    raise
