from pathlib import Path
import subprocess, json, hashlib, shutil, datetime

repo = Path('/Users/auchan/projects/garden-of-dreams')
work = Path(__file__).resolve().parent
candidate = work / 'candidate-godot'
final = work / 'final-v2'
installed = repo / 'godot'
out = work / 'installed-v2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
targets = ['runtime/entry_route.gd', 'tests/test_yihong_framing.gd',
           'tests/test_yihong_framing.gd.uid', 'tests/test_portrait_architecture.gd',
           'tests/portrait-architecture-contract.json']
assert not out.exists()
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=repo, text=True).strip() == 'codex/courtyard-portrait-framing'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip() == '5dc918b9b29eee695f3a71a9ff875921df731dbc'
fixture = json.loads((work / 'fixture.json').read_text())
assert sha(installed / targets[0]) == fixture['runtime']
assert sha(installed / 'assets/garden-of-dreams.glb') == sha(repo / 'export/garden-of-dreams.glb') == fixture['source']
assert len(fixture['lighting_pngs']) == 141
for name, digest in fixture['lighting_pngs'].items():
    assert sha(installed / name) == digest, name
frozen = json.loads((final / 'frozen-inputs.json').read_text())
for name, digest in frozen.items():
    assert sha(candidate / name) == digest, name
    if name not in targets and (installed / name).is_file():
        assert sha(installed / name) == digest, ('Unexpected existing fixture difference', name)
pipeline = json.loads((final / 'pipeline.json').read_text())
assert len(pipeline['phases']) == 32
for row in pipeline['phases']:
    assert row['status'] == 'passed' and row['exit_code'] == 0
    assert sha(row['log']) == row['log_sha256']
    if row.get('native_report'):
        assert sha(row['native_report']) == row['native_report_sha256']
visual = json.loads((final / 'visual-review.json').read_text())
assert visual['direct_file_count'] == 25
for name, digest in visual['directly_inspected'].items():
    assert sha(final / 'review-captures' / name) == digest
for mode in ['desktop', 'portrait']:
    tour = json.loads((final / 'review-captures' / ('tour-' + mode) / 'report.json').read_text())
    assert len(tour['legs']) == 26 and len(tour['visited_rooms']) == 14 and not tour['floor_failures']
    for row in tour['captures']:
        assert sha(final / 'review-captures' / ('tour-' + mode) / row['file']) == row['sha256']
contract = json.loads((candidate / targets[4]).read_text())
before = json.loads((installed / targets[4]).read_text())
# The only contract additions concern the imperial composition. Existing rooms and limits stay intact.
def remove_added(value):
    if isinstance(value, dict):
        return {k: remove_added(v) for k, v in value.items() if k not in ['minimum_height_fraction', 'maximum_top_fraction']}
    if isinstance(value, list):
        return [remove_added(v) for v in value]
    return value
assert remove_added(contract) == before
out.mkdir()
report = {'status': 'staging', 'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'targets': {}, 'phases': [], 'source_glb_sha256': fixture['source'],
          'runtime_sha256': sha(candidate / targets[0]), 'rollback': False}
def save():
    (out / 'adoption.json').write_text(json.dumps(report, indent=2) + '\n')
for name in targets:
    dst = installed / name
    old = sha(dst) if dst.exists() else None
    report['targets'][name] = {'before_sha256': old, 'after_sha256': sha(candidate / name)}
    if old:
        backup = out / 'backup' / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, backup)
save()
try:
    for name in targets:
        dst = installed / name
        staged = dst.with_name(dst.name + '.camera-staged')
        shutil.copy2(candidate / name, staged)
        staged.replace(dst)
        assert sha(dst) == report['targets'][name]['after_sha256']
    report['status'] = 'installed_native_checks_running'
    save()
    names = ['final-import', 'native-source-contract', 'full-lighting',
             'yihong-normal', 'yihong-touch', 'yihong-density',
             'architecture-normal', 'architecture-touch', 'architecture-density',
             'arrivals-desktop', 'arrivals-portrait']
    by_name = {r['name']: r for r in pipeline['phases']}
    for name in names:
        old = by_name[name]
        cmd = [s.replace(str(candidate), str(installed)).replace(str(final), str(out)) for s in old['command']]
        row = {'name': name, 'command': cmd, 'status': 'running', 'log': str(out / (name + '.log'))}
        report['phases'].append(row)
        with Path(row['log']).open('w') as f:
            child = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
            row['pid'] = child.pid
            save()
            try:
                code = child.wait(timeout=old['timeout'])
            except subprocess.TimeoutExpired:
                child.terminate()
                try: child.wait(timeout=10)
                except subprocess.TimeoutExpired: child.kill(); child.wait()
                raise
        row['exit_code'] = code
        row['log_sha256'] = sha(row['log'])
        log = Path(row['log']).read_text()
        assert code == 0 and 'ERROR:' not in log and 'SCRIPT ERROR:' not in log, log[-3000:]
        row['status'] = 'passed'
        save()
    compared = []
    for name in names:
        directory = final / 'review-captures' / name
        if directory.exists():
            for path in sorted(directory.glob('*.png')):
                target = out / 'review-captures' / name / path.name
                assert sha(target) == sha(path), ('Installed image differs', str(target))
                compared.append({'file': str(target.relative_to(out)), 'sha256': sha(target)})
    assert len(compared) == 98, len(compared)
    for name, row in report['targets'].items():
        assert sha(installed / name) == row['after_sha256']
    for name, digest in fixture['lighting_pngs'].items():
        assert sha(installed / name) == digest
    assert sha(installed / 'assets/garden-of-dreams.glb') == fixture['source']
    report.update(status='installed_checks_and98_original_reproductions_passed',
                  reproduced_originals=compared, finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print('INSTALLED_CAMERA_PASSED', len(names), len(compared), flush=True)
except BaseException as error:
    for name, row in report['targets'].items():
        dst = installed / name
        if row['before_sha256']:
            shutil.copy2(out / 'backup' / name, dst)
            assert sha(dst) == row['before_sha256']
        elif dst.exists():
            dst.unlink()
    report.update(status='failed_rolled_back', rollback=True, error=str(error))
    save()
    raise
