"""Wait for the current native review, then prepare and bake the atlas revision.

This produces a separate candidate. It never installs scene assets in the repo.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
for flag in ('source-root', 'atlas-root', 'review-report', 'output-root'):
    parser.add_argument('--'+flag, type=Path, required=True)
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
root = args.output_root.resolve()
source = args.source_root.resolve()
atlas = args.atlas_root.resolve()
production = Path('/Users/auchan/projects/garden-of-dreams')
assert root != production and production not in root.parents
assert source != production and source != root and root not in source.parents
root.mkdir(parents=True, exist_ok=False)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected_source = '5ae484f9154861df0f5b0a43865f59ae549d1d9c5cbb255192f0d73f6c4c905f'
expected_author = '42579f68da9d911180d756d5430065df6043adb4ac030f4b303bb137afae2bbb'
assert sha(source/'export/garden-of-dreams.glb') == expected_source
assert sha(source/'blender/authoring.blend') == expected_author
shutil.copytree(repo/'scripts', root/'scripts', ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(atlas/'textures/atlases', root/'textures/atlases')
shutil.copytree(repo/'textures/atlases/pavilion', root/'baseline/textures/atlases/pavilion')
shutil.copytree(repo/'textures/atlases/wall', root/'baseline/textures/atlases/wall')
(root/'input/blender').mkdir(parents=True)
(root/'input/export').mkdir()
shutil.copy2(source/'blender/authoring.blend', root/'input/blender/authoring.blend')
shutil.copy2(source/'export/garden-of-dreams.glb', root/'input/export/garden-of-dreams.glb')
shutil.copytree(source/'export/sites', root/'input/export/sites')
(root/'export/lightmaps').mkdir(parents=True)
(root/'preparation-logs').mkdir()
shutil.copy2(source/'export/site-wash-rig.json', root/'export/site-wash-rig.json')
report = {'status':'preparing_frozen_inputs', 'folder':str(root),
          'orchestrator_pid':os.getpid(), 'started_at':datetime.now(timezone.utc).isoformat(),
          'input_source_sha256':expected_source, 'input_authoring_sha256':expected_author,
          'prior_review_report':str(args.review_report.resolve()), 'phases':[],
          'scope':'Only two architectural atlas color images change on the paving and neutral-material candidate. Sequential native work starts only after the prior complete source bake and native review exit successfully. No production adoption; scene/device/art/service acceptance remains required.'}
report_path = root/'source-preparation.json'
def save():
    temporary = report_path.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2)+'\n')
    temporary.replace(report_path)
save()
pointer = {'folder':str(root), 'orchestrator_pid':os.getpid(), 'report':str(report_path)}
Path('/tmp/garden-neutral-atlas-full-source.json').write_text(json.dumps(pointer, indent=2)+'\n')


def run(name, command, marker):
    log = root/'preparation-logs'/(name+'.log')
    phase = {'name':name, 'command':command, 'status':'running', 'log':str(log)}
    report['phases'].append(phase)
    save()
    print('NEUTRAL_ATLAS_PHASE_START', name, flush=True)
    with log.open('w') as out:
        child = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT, cwd=root)
        phase['pid'] = child.pid
        save()
        phase['exit_code'] = child.wait()
    phase['log_sha256'] = sha(log)
    text = log.read_text(errors='replace')
    assert phase['exit_code'] == 0 and marker in text, text[-4000:]
    assert not re.search(r'(?m)^(Error:|Traceback|SCRIPT ERROR:|ERROR:)|AssertionError:', text), text[-4000:]
    phase['status'] = 'passed'
    save()
    print('NEUTRAL_ATLAS_PHASE_PASS', name, flush=True)


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def read_report(path):
    # The preceding runners write JSON directly; a read can coincide with a write.
    for attempt in range(5):
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            if attempt == 4:
                raise
            time.sleep(.1)


try:
    py = sys.executable
    run('candidate-atlas-preservation', [py, str(root/'scripts/verify_neutral_architecture_atlases.py'),
        '--baseline-root', str(root/'baseline'), '--candidate-root', str(root),
        '--output', str(root/'atlas-preservation.json')], 'NEUTRAL_ATLAS_PRESERVATION_PASS')
    prepared_inputs = {'input_source_sha256':expected_source, 'input_authoring_sha256':expected_author,
                      'files':{str(p.relative_to(root)):sha(p) for folder in ('scripts', 'textures', 'baseline', 'input')
                               for p in sorted((root/folder).rglob('*')) if p.is_file()}}
    (root/'queued-inputs.json').write_text(json.dumps(prepared_inputs, indent=2)+'\n')
    report['status'] = 'waiting_for_prior_native_review_exit'
    save()
    print('NEUTRAL_ATLAS_WAITING_FOR_PRIOR_REVIEW', args.review_report, flush=True)
    while True:
        previous = read_report(args.review_report)
        bake = read_report(source/'export/full-lighting-refresh.json')
        assert previous['source_glb_sha256'] == expected_source and bake['source_glb_sha256'] == expected_source
        assert previous['status'] != 'failed' and bake['status'] != 'failed', 'Prior native pipeline failed; do not start new graphics work'
        if previous['status'] == 'technical_checks_complete_visual_review_pending':
            assert bake['status'] == 'source_complete'
            assert len(bake['phases']) == 6 and all(p['status'] == 'passed' and p['exit_code'] == 0 for p in bake['phases'])
            assert len(previous['phases']) == 37 and all(p['status'] == 'passed' for p in previous['phases'])
            if not alive(previous['orchestrator_pid']) and not alive(bake['orchestrator_pid']):
                prior_source = json.loads((source/'source-preparation.json').read_text())
                assert prior_source['status'] == 'complete_source_bake_passed_native_review_pending'
                if not alive(prior_source['orchestrator_pid']):
                    break
        elif not alive(previous['orchestrator_pid']):
            raise RuntimeError('Prior review exited without its successful terminal report')
        time.sleep(5)
    assert sha(source/'export/garden-of-dreams.glb') == expected_source
    assert sha(source/'blender/authoring.blend') == expected_author
    assert all(sha(root/name) == digest for name,digest in prepared_inputs['files'].items()), 'Frozen queued input changed'
    (root/'prior-native-release.json').write_text(json.dumps({'review':previous, 'bake':bake,
        'scope':'Prior native review and both source orchestration processes exited before this candidate started native work.'}, indent=2)+'\n')
    report['status'] = 'preparing_native_source'
    save()
    blender = '/Applications/Blender.app/Contents/MacOS/Blender'
    run('atlas-source-export', [blender, '--background', str(root/'input/blender/authoring.blend'),
        '--python-exit-code', '1', '--python', str(root/'scripts/apply_garden_architecture_atlases.py'),
        '--', '--baseline-root', str(root/'baseline'), '--candidate-root', str(root),
        '--output-root', str(root), '--before-export', str(root/'input/export/garden-of-dreams.glb')],
        'GARDEN_ARCHITECTURE_ATLAS_SOURCE_PASS')
    candidate_source = sha(root/'export/garden-of-dreams.glb')
    candidate_author = sha(root/'blender/authoring.blend')
    report.update(source_glb_sha256=candidate_source, authoring_sha256=candidate_author)
    save()
    # Check every site too: atlas users may span more than one room.
    sys.path.insert(0, str(root/'scripts'))
    from verify_garden_atlas_export import compare
    site_report = {}
    old_sites = {p.name:p for p in (root/'input/export/sites').glob('*.glb')}
    new_sites = {p.name:p for p in (root/'export/sites').glob('*.glb')}
    assert old_sites.keys() == new_sites.keys() and len(old_sites) == 15
    for name, old in old_sites.items():
        new = new_sites[name]
        if old.read_bytes() == new.read_bytes():
            site_report[name] = {'byte_identical':True, 'sha256':sha(new)}
        else:
            # The full comparator expects both atlases; single-atlas sites
            # are checked against the same generic contract with their inventory.
            site_report[name] = compare(old, new, root/'baseline', root, require_both=False)
    (root/'export/atlas-site-preservation.json').write_text(json.dumps(site_report, indent=2)+'\n')
    text = (root/'scripts/prepare_candidate_libraries.py').read_text()
    old_assert = "assert root!=repo and repo not in root.parents,'Use a separate candidate tree'"
    assert old_assert in text
    text = text.replace(old_assert, "assert root==repo and root!=Path('/Users/auchan/projects/garden-of-dreams'), 'Frozen separate source only'")
    (root/'scripts/prepare_candidate_libraries_frozen.py').write_text(text)
    native = [blender, '--background', '--threads', '8', '--python-exit-code', '1', '--python']
    run('site-libraries', native+[str(root/'scripts/prepare_candidate_libraries_frozen.py'), '--', '--root', str(root)], 'CANDIDATE_LIBRARIES_PREPARED')
    run('wash-receivers', native+[str(root/'scripts/package_site_washes.py'), '--', '--portable-master'], 'SITE_WASH')
    assert sha(root/'blender/authoring.blend') == candidate_author
    assert not any((root/'export/lightmaps').iterdir())
    frozen = {'source_glb_sha256':candidate_source, 'authoring_sha256':candidate_author,
              'master_sha256':sha(root/'blender/master.blend'),
              'files':{str(p.relative_to(root)):sha(p) for folder in ('blender/sites', 'export/sites', 'scripts', 'textures')
                       for p in sorted((root/folder).rglob('*')) if p.is_file()},
              'empty_lightmaps_before_refresh':True}
    report['status'] = 'prepared_frozen_complete_source'
    save()
    shutil.copy2(report_path, root/'source-preparation-snapshot.json')
    frozen['source_preparation_snapshot_sha256'] = sha(root/'source-preparation-snapshot.json')
    (root/'full-refresh-inputs.json').write_text(json.dumps(frozen, indent=2)+'\n')
    report['status'] = 'full_source_bake_running'
    save()
    run('full-lighting', [py, str(root/'scripts/refresh_full_lighting.py'), '--samples', '128', '--size', '1024'], 'FULL_SOURCE_LIGHTING_REFRESH_PASS')
    assert sha(root/'blender/authoring.blend') == candidate_author
    assert sha(root/'export/garden-of-dreams.glb') == candidate_source
    report['status'] = 'complete_source_bake_passed_native_review_pending'
    save()
    print('NEUTRAL_ATLAS_FULL_SOURCE_COMPLETE', root, flush=True)
except BaseException as error:
    report['status'] = 'failed'
    report['error'] = str(error)
    save()
    raise
