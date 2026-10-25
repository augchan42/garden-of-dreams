"""Build the bounded offline demo without changing the working Godot project.

Phases are explicit so native images can be reviewed before archiving:
  prepare -> check -> capture -> launch -> archive
All native jobs are sequential, time limited, and recorded with their actual logs.
The archive phase verifies a clean extraction and its normal application launch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import signal
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORK = ROOT / 'build/demo-handoff-release'
DEMO_SCENE = 'res://runtime/first_reading_demo.tscn'
PRESET = '''[preset.0]
name="macOS Demo"
platform="macOS"
runnable=true
export_filter="all_resources"
include_filter="*.json"
exclude_filter=""
export_path=""
script_export_mode=1

[preset.0.options]
binary_format/architecture="universal"
application/bundle_identifier="com.gardenofdreams.demo"
application/short_version="0.1.0"
application/version="0.1.0"
codesign/codesign=0
'''


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def read_json(path):
    return json.loads(path.read_text())


def project_files(project):
    """Logical source files; import caches and installed Android builds are excluded."""
    return {str(p.relative_to(project)): sha(p) for p in sorted(project.rglob('*'))
            if p.is_file() and '.godot' not in p.relative_to(project).parts
            and not str(p.relative_to(project)).startswith('android/build/')}


def demo_config(text):
    """Refuse ambiguous or missing startup keys rather than silently export exploration."""
    pattern = r'(?m)^run/main_scene\s*=.*$'
    require(len(re.findall(pattern, text)) == 1, 'Expected one project startup setting')
    text = re.sub(pattern, f'run/main_scene="{DEMO_SCENE}"', text)
    # Universal macOS exports require the ARM texture format even when the
    # source editor currently imports only its host format. Keep this staged.
    section = re.search(r'(?m)^\[rendering\][ \t]*$', text)
    setting = 'textures/vram_compression/import_etc2_astc=true'
    if section is None:
        return text.rstrip() + '\n\n[rendering]\n\n' + setting + '\n'
    following = re.search(r'(?m)^\[', text[section.end():])
    end = section.end() + following.start() if following else len(text)
    body = text[section.end():end]
    key_pattern = r'(?m)^textures/vram_compression/import_etc2_astc[ \t]*=.*$'
    require(len(re.findall(key_pattern, body)) <= 1, 'Ambiguous staged texture format setting')
    if re.search(key_pattern, body):
        body = re.sub(key_pattern, setting, body)
    else:
        body = body.rstrip() + '\n' + setting + '\n\n'
    return text[:section.end()] + body + text[end:]


def require_demo_config(text):
    settings = re.findall(r'(?m)^run/main_scene\s*=\s*"([^"]+)"\s*$', text)
    require(settings == [DEMO_SCENE], 'Staged package would start the wrong scene')


def stage_project(source, stage):
    require(source.resolve() != stage.resolve(), 'Source and staging must differ')
    require(not stage.exists(), 'Staging already exists; use a fresh --work directory')
    before = project_files(source)
    def ignore(directory, names):
        return [name for name in names if name == '.godot'
                or (name == 'build' and Path(directory).name == 'android')]
    shutil.copytree(source, stage, ignore=ignore)
    (stage / 'project.godot').write_text(demo_config((stage / 'project.godot').read_text()))
    (stage / 'export_presets.cfg').write_text(PRESET)
    require_demo_config((stage / 'project.godot').read_text())
    require(project_files(source) == before, 'Production project changed during staging')
    copied = project_files(stage)
    allowed = {'project.godot', 'export_presets.cfg'}
    require(copied.keys() == before.keys() | {'export_presets.cfg'}, 'Staging file inventory differs')
    require(all(copied[p] == digest for p, digest in before.items() if p not in allowed),
            'Staging changed a source asset')
    return before


def command(args, name, argv, timeout=300, marker=None, cwd=None):
    log = args.work / 'logs' / f'{name}.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    result = {'name': name, 'argv': [str(v) for v in argv], 'log': str(log),
              'started_unix': started, 'timeout_seconds': timeout, 'status': 'running'}
    report = args.work / 'jobs' / f'{name}.json'
    write_json(report, result)
    with log.open('w') as output:
        proc = subprocess.Popen([str(v) for v in argv], cwd=cwd or args.work,
                                stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        result['pid'] = proc.pid
        write_json(report, result)
        try:
            result['exit_code'] = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            result['exit_code'] = proc.returncode
            result['timed_out'] = True
    content = log.read_text(errors='replace')
    result.update(elapsed_seconds=round(time.time() - started, 3), log_sha256=sha(log),
                  diagnostics=[line for line in content.splitlines()
                               if re.search(r'(?:SCRIPT |USER )?ERROR:', line)],
                  warnings=[line for line in content.splitlines() if 'WARNING:' in line])
    passed = (result['exit_code'] == 0 and not result.get('timed_out')
              and not result['diagnostics'] and (marker is None or marker in content))
    result['status'] = 'passed' if passed else 'failed'
    write_json(report, result)
    require(passed, f'{name} failed; see {log}')
    print(f'DEMO_HANDOFF_PHASE_PASS {name}', flush=True)
    return result


def frozen(args):
    manifest = read_json(args.work / 'prepare.json')
    require(manifest['status'] == 'passed', 'Prepare phase did not pass')
    require(project_files(ROOT / 'godot') == manifest['production_files_sha256'],
            'Production Godot files changed; prepare a fresh staging directory')
    require(project_files(args.work / 'godot') == manifest['staged_files_sha256'],
            'Staged logical files changed after packaging')
    for relative, digest in manifest['producer_files_sha256'].items():
        require(sha(ROOT / relative) == digest, 'Build producer changed: ' + relative)
    require(sha(ROOT / 'export/garden-of-dreams.glb') == manifest['source_glb_sha256'],
            'Canonical export changed after packaging')
    require(sha(args.work / 'GardenOfDreamsDemo.pck') == manifest['pack_sha256'], 'Pack changed')
    app = args.work / 'application' / manifest['app_name']
    require(tree_hashes(app) == manifest['app_files_sha256'], 'Application changed')
    return manifest, app


def tree_hashes(directory):
    return {str(p.relative_to(directory)): sha(p) for p in sorted(directory.rglob('*')) if p.is_file()}


def binary(app):
    info = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
    path = app / 'Contents/MacOS' / info['CFBundleExecutable']
    require(path.is_file() and os.access(path, os.X_OK), 'Application binary is not executable')
    return path


def prepare(args):
    require(not (args.work / 'prepare.json').exists(), 'Prepare already recorded; use another --work')
    stage = args.work / 'godot'
    sources = stage_project(ROOT / 'godot', stage)
    source_hash = sha(ROOT / 'export/garden-of-dreams.glb')
    require(source_hash == sources['assets/garden-of-dreams.glb'], 'Canonical and engine GLBs differ')
    phases = [command(args, 'import', [args.godot, '--headless', '--path', stage,
                                     '--editor', '--import'], timeout=1800)]
    phases.append(command(args, 'export', [args.godot, '--headless', '--path', stage,
                          '--export-release', 'macOS Demo', args.work / 'application-export.zip'], 1800))
    application = args.work / 'application'
    application.mkdir()
    phases.append(command(args, 'extract-application', ['ditto', '-x', '-k',
                          args.work / 'application-export.zip', application]))
    apps = list(application.glob('*.app'))
    require(len(apps) == 1, 'Export must contain one application bundle')
    app = apps[0]
    phases.append(command(args, 'sign-application', ['/usr/bin/codesign', '--force', '--deep',
                          '--sign', '-', app]))
    phases.append(command(args, 'verify-signature', ['/usr/bin/codesign', '--verify', '--deep',
                          '--strict', app]))
    phases.append(command(args, 'verify-universal', ['/usr/bin/lipo', binary(app),
                          '-verify_arch', 'arm64', 'x86_64']))
    packs = list((app / 'Contents/Resources').glob('*.pck'))
    require(len(packs) == 1, 'Export must contain one bundled PCK')
    pack = args.work / 'GardenOfDreamsDemo.pck'
    shutil.copy2(packs[0], pack)
    require(project_files(ROOT / 'godot') == sources, 'Production project changed during prepare')
    require_demo_config((stage / 'project.godot').read_text())
    report = {'status': 'passed', 'source_glb_sha256': source_hash,
              'production_files_sha256': sources, 'staged_files_sha256': project_files(stage),
              'producer_files_sha256': {p: sha(ROOT / p) for p in
                  ['scripts/build_demo_handoff.py', 'scripts/assemble_demo_capture.py']},
              'app_name': app.name, 'app_files_sha256': tree_hashes(app),
              'pack_sha256': sha(pack), 'embedded_pack': str(packs[0].relative_to(app)),
              'startup_scene': DEMO_SCENE, 'architecture': ['arm64', 'x86_64'],
              'signing': 'local ad-hoc; not notarized', 'phases': phases}
    write_json(args.work / 'prepare.json', report)


def check(args):
    manifest, app = frozen(args)
    phases = []
    checks = [('startup', 'test_demo_pack_startup', 'DEMO_PACK_STARTUP_PASS', False, []),
              ('local-cast', 'test_local_cast', 'LOCAL_CAST_PASS', True, []),
              ('route', 'test_first_reading_demo', 'FIRST_READING_DEMO_PASS', False, []),
              ('reading', 'test_demo_reading', 'DEMO_READING_PASS', False, [])]
    for name, script, marker, headless, extra in checks:
        # Release templates omit the --script tool. Installed Godot retains
        # assertions while exercising the exact shipped PCK.
        argv = [args.godot, '--main-pack', args.work / 'GardenOfDreamsDemo.pck']
        if headless:
            argv.append('--headless')
        argv += ['--script', f'res://tests/{script}.gd']
        if name == 'startup':
            extra = ['--screenshots-dir', str(args.work / 'startup-images')]
        if extra:
            argv += ['--'] + extra
        phases.append(command(args, name, argv, timeout=300, marker=marker))
    # The shipped template disables script and path overrides. Its passive
    # child hook inspects the actual default route only for this explicit flag.
    for name, extra in [('input-desktop', []), ('input-portrait', ['--portrait'])]:
        argv = [binary(app), '--', '--demo-acceptance',
                '--screenshots-dir', str(args.work / 'startup-images')] + extra
        phases.append(command(args, name, argv, timeout=300, marker='DEMO_RELEASE_ACCEPTANCE_PASS'))
    frozen(args)
    write_json(args.work / 'checks.json', {'status': 'passed', 'pack_sha256': manifest['pack_sha256'],
               'source_glb_sha256': manifest['source_glb_sha256'], 'phases': phases,
               'startup_images_sha256': tree_hashes(args.work / 'startup-images')})


def capture(args):
    manifest, app = frozen(args)
    frames = args.work / 'frames'
    require(not frames.exists(), 'Frame directory already exists; preserve it and use a fresh --work')
    # The existing recorder saves frames inside assert(); use the debug-capable
    # engine with this exact shipped PCK so the recording call is executed.
    job = command(args, 'capture', [args.godot, '--main-pack', args.work / 'GardenOfDreamsDemo.pck',
                  '--fixed-fps', '30', '--script', 'res://tests/capture_first_reading_demo.gd',
                  '--', '--frames-dir', frames], timeout=1200, marker='DEMO_CAPTURE_PASS')
    capture_data = read_json(frames / 'capture.json')
    count = capture_data['frames']
    originals = sorted(frames.glob('frame-*.png'))
    require(f'DEMO_FRAME_SEQUENCE_PASS {count}' in Path(job['log']).read_text(),
            'Native frame completion marker is missing')
    require(capture_data['fps'] == 30 and count >= 1200 and len(originals) == count,
            'Incomplete native 30 FPS capture')
    require([p.name for p in originals] == [f'frame-{i:05d}.png' for i in range(count)], 'Frame gap')
    require({'crt', 'lanterns', 'tunnel', 'reveal', 'water', 'cast'} <=
            {event['cue'] for event in capture_data['cues']}, 'Missing original audio cue')
    movie = args.work / 'GardenOfDreamsDemo.mp4'
    assembly = command(args, 'assemble', [sys.executable, ROOT / 'scripts/assemble_demo_capture.py',
                                         frames, movie], 1200, marker='DEMO_ASSEMBLY_PASS')
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size',
        '-of', 'json', movie], text=True))
    video = next(s for s in probe['streams'] if s['codec_name'] == 'h264')
    require(any(s['codec_name'] == 'aac' for s in probe['streams']), 'Missing AAC audio')
    require((video['width'], video['height'], video['r_frame_rate'], int(video['nb_frames'])) ==
            (1410, 600, '30/1', count), 'Wrong movie dimensions or frame count')
    require(abs(float(probe['format']['duration']) - count / 30) < .04, 'Wrong movie duration')
    decoded = command(args, 'decode-movie', ['ffmpeg', '-v', 'error', '-xerror', '-i', movie,
                                           '-f', 'null', '-'], 300)
    require(not Path(decoded['log']).read_text().strip(), 'Movie decode reported errors')
    samples = sorted({round((count - 1) * fraction) for fraction in
                      [0, .14, .30, .45, .52, .67, .74, .82, .90, .99]})
    review = args.work / 'review-images'
    review.mkdir()
    for number in samples:
        shutil.copy2(originals[number], review / originals[number].name)
    frozen(args)
    write_json(args.work / 'capture.json', {'status': 'passed', 'pack_sha256': manifest['pack_sha256'],
        'source_glb_sha256': manifest['source_glb_sha256'], 'movie_sha256': sha(movie),
        'native_capture': capture_data, 'movie_probe': probe, 'phases': [job, assembly, decoded],
        'frame_sha256': {p.name: sha(p) for p in originals}, 'review_images_sha256': tree_hashes(review),
        'audio_mix_sha256': sha(frames / 'cue-mix.wav')})


def normal_launch(args, app, name):
    # No --script, scene override, project path, or external pack: the application
    # must find its own embedded pack and configured default scene.
    return command(args, name, [binary(app), '--max-fps', '30', '--quit-after', '180'],
                   timeout=120, cwd=app.parent)


def launch(args):
    manifest, app = frozen(args)
    phase = normal_launch(args, app, 'normal-launch')
    frozen(args)
    write_json(args.work / 'launch.json', {'status': 'passed', 'pack_sha256': manifest['pack_sha256'],
               'scope': 'Normal bundled startup for 180 process frames; scene assertion is in checks.json.',
               'phase': phase})


def archive(args):
    manifest, app = frozen(args)
    require(args.visual_review_note and args.visual_review_note.strip(),
            'Inspect native startup/capture images, then pass --visual-review-note')
    evidence = {key: read_json(args.work / f'{key}.json') for key in ['checks', 'capture', 'launch']}
    for key, report in evidence.items():
        require(report['status'] == 'passed' and report['pack_sha256'] == manifest['pack_sha256'],
                f'{key} evidence does not match this pack')
    require(sha(args.work / 'GardenOfDreamsDemo.mp4') == evidence['capture']['movie_sha256'], 'Movie changed')
    for report in [manifest, *evidence.values()]:
        for phase in report.get('phases', [report.get('phase')]):
            require(phase and sha(phase['log']) == phase['log_sha256'], 'Evidence log changed')
    for name, digest in evidence['checks']['startup_images_sha256'].items():
        require(sha(args.work / 'startup-images' / name) == digest, 'Startup image changed')
    for name, digest in evidence['capture']['review_images_sha256'].items():
        require(sha(args.work / 'review-images' / name) == digest, 'Review image changed')
    payload = args.work / 'GardenOfDreamsDemo'
    require(not payload.exists(), 'Handoff payload already exists; preserve the previous archive')
    payload.mkdir()
    shutil.copytree(app, payload / app.name)
    for name in ['GardenOfDreamsDemo.pck', 'GardenOfDreamsDemo.mp4']:
        shutil.copy2(args.work / name, payload / name)
    shutil.copy2(ROOT / 'docs/demo-run-guide.md', payload / 'README.md')
    write_json(payload / 'SOURCE.json', manifest)
    write_json(payload / 'CHECKS.json', dict(evidence, visual_review_note=args.visual_review_note))
    hashes = tree_hashes(payload)
    (payload / 'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name, digest in hashes.items()))
    archive_path = args.work / 'GardenOfDreamsDemo-macOS.zip'
    command(args, 'archive', ['ditto', '-c', '-k', '--sequesterRsrc', '--keepParent', payload, archive_path], 600)
    with zipfile.ZipFile(archive_path) as zipped:
        require(zipped.testzip() is None, 'Archive CRC failure')
    extracted = args.work / 'clean-extraction'
    require(not extracted.exists(), 'Clean extraction directory already exists')
    command(args, 'extract-handoff', ['ditto', '-x', '-k', archive_path, extracted], 600)
    copy = extracted / payload.name
    require(tree_hashes(copy) == tree_hashes(payload), 'Extracted payload differs')
    extracted_app = copy / app.name
    command(args, 'extracted-signature', ['/usr/bin/codesign', '--verify', '--deep', '--strict', extracted_app])
    clean_start = normal_launch(args, extracted_app, 'extracted-normal-launch')
    frozen(args)
    write_json(args.work / 'handoff.json', {'status': 'passed', 'archive': str(archive_path),
        'archive_sha256': sha(archive_path), 'archive_bytes': archive_path.stat().st_size,
        'pack_sha256': manifest['pack_sha256'], 'source_glb_sha256': manifest['source_glb_sha256'],
        'movie_sha256': evidence['capture']['movie_sha256'], 'payload_files_sha256': tree_hashes(payload),
        'visual_review_note': args.visual_review_note, 'clean_extracted_launch': clean_start,
        'limitations': ['Ad-hoc signed local macOS build; not notarized.',
                        'Native runtime verified only on the host; Intel execution is untested.',
                        'No broad phone, sustained performance, full-garden art or service acceptance.']})
    print('DEMO_HANDOFF_READY', archive_path, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['prepare', 'check', 'capture', 'launch', 'archive'])
    parser.add_argument('--work', type=Path, default=DEFAULT_WORK)
    parser.add_argument('--godot', type=Path, default=Path('/Applications/Godot.app/Contents/MacOS/Godot'))
    parser.add_argument('--visual-review-note')
    args = parser.parse_args()
    from check_asset_checkout import require_assets
    require_assets(ROOT)
    args.work = args.work.resolve()
    require(args.work != ROOT and ROOT / 'godot' not in [args.work, *args.work.parents],
            'Output must be separate from production Godot files')
    args.work.mkdir(parents=True, exist_ok=True)
    globals()[args.phase](args)


if __name__ == '__main__':
    main()
