"""Verify a native demo capture and assemble the local five-file release archive.

Requires a passing pack report, matching current source, contiguous native frames,
and a completely decoded H.264/AAC movie before changing release payloads.
This packages a progress checkpoint; it does not establish final art/performance.
"""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import wave
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(args):
    job = json.loads(args.capture_job.read_text())
    checks = json.loads(args.pack_checks.read_text())
    source_hash = sha(ROOT / 'export/garden-of-dreams.glb')
    require(source_hash == sha(ROOT / 'godot/assets/garden-of-dreams.glb'),
            'Engine source differs from canonical source')
    require(job['status'] == 'captured' and job['exit_code'] == 0,
            'Native capture did not complete')
    required_checks = {'test_mountain_paint', 'test_site_key_import', 'test_full_scene_lighting',
                       'test_surface_materials', 'test_baked_backdrop_wash', 'test_terminal_spill',
                       'test_first_reading_demo', 'test_demo_reading', 'test_demo_input_acceptance'}
    require(checks['status'] == 'passed' and required_checks <= {p['name'] for p in checks['phases']}
            and all(p['status'] == 'passed' and p['exit_code'] == 0 and not p.get('diagnostics')
                    for p in checks['phases']),
            'Complete packed demo acceptance is missing')
    profile = json.loads(args.profile.read_text())
    required_runtime = {'runtime/baked_materials.gd', 'shaders/baked_diffuse.gdshader',
                        'runtime/reading_result.gd', 'runtime/demo_finale.gd'} | {
        f'assets/garden-of-dreams_{name}.png.import'
        for name in ('pavilion_normal', 'wall_normal', 'pavilion_orm', 'wall_orm')}
    runtime = job.get('runtime_files_sha256', {})
    require(required_runtime <= runtime.keys(), 'Capture runtime provenance is incomplete')
    require(runtime == checks.get('runtime_files_sha256') == profile.get('runtime_files_sha256'),
            'Pack, capture and profile runtime provenance differs')
    for path, digest in runtime.items():
        require(sha(ROOT / 'godot' / path) == digest, 'Runtime changed after capture: ' + path)
    require(profile['baked_diffuse_shader_sha256'] == runtime['shaders/baked_diffuse.gdshader'],
            'Profile shader differs from captured runtime')
    require(source_hash == job['source_glb_sha256'] == checks['source_glb_sha256']
            == profile['source_glb_sha256'],
            'Source changed after packed checks/capture')
    pack = Path(job['pack'])
    require(sha(pack) == job['pack_sha256'] == checks['pack_sha256'],
            'Packed/captured payload hash differs')
    for phase in checks['phases']:
        require(sha(ROOT / phase['archived_log']) == phase['log_sha256'],
                'Packed check log changed: ' + phase['name'])
    frames_dir = Path(job['frames_dir'])
    capture = json.loads((frames_dir / 'capture.json').read_text())
    require(capture['fps'] == 30 and capture['frames'] >= 1200, 'Incomplete route capture')
    count = capture['frames']
    frames = sorted(frames_dir.glob('frame-*.png'))
    require(len(frames) == count and all(p.name == f'frame-{i:05d}.png'
                                       for i, p in enumerate(frames)), 'Native frame gap')
    cues = capture['cues']
    require({'crt', 'lanterns', 'tunnel', 'reveal', 'water', 'cast'}
            <= {c['cue'] for c in cues}, 'Missing original audio cue')
    require(all(0 <= c['frame'] < count for c in cues)
            and [c['frame'] for c in cues] == sorted(c['frame'] for c in cues),
            'Invalid cue transition times')
    capture_log = Path(job['log'])
    log = capture_log.read_text()
    require('DEMO_CAPTURE_PASS' in log and f'DEMO_FRAME_SEQUENCE_PASS {count}' in log
            and 'ERROR:' not in log and 'WARNING:' not in log, 'Native capture diagnostics')
    assembly_log = args.assembly_log.read_text()
    require(f'DEMO_ASSEMBLY_PASS {count} {count / 30} {len(cues)}' in assembly_log,
            'Assembly completion evidence is missing')
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries',
        'stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration,size',
        '-of', 'json', str(args.movie)], text=True))
    video = next(s for s in probe['streams'] if s['codec_name'] == 'h264')
    require(any(s['codec_name'] == 'aac' for s in probe['streams']), 'Missing AAC audio')
    require((video['width'], video['height'], video['r_frame_rate'], int(video['nb_frames']))
            == (1410, 600, '30/1', count), 'Wrong encoded video dimensions/frame count')
    require(abs(float(probe['format']['duration']) - count / 30) < .001,
            'Wrong encoded duration')
    decoded = subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(args.movie),
                              '-f', 'null', '-'], capture_output=True, text=True)
    require(decoded.returncode == 0 and not decoded.stderr.strip(),
            'Complete movie decode failed: ' + decoded.stderr)
    audio = frames_dir / 'cue-mix.wav'
    with wave.open(str(audio)) as pcm:
        require((pcm.getnchannels(), pcm.getsampwidth(), pcm.getframerate(), pcm.getnframes())
                == (1, 2, 22050, count * 22050 // 30), 'Wrong assembled cue PCM')
        values = array('h', pcm.readframes(pcm.getnframes()))
        if sys.byteorder != 'little':
            values.byteswap()
        peak = max(abs(v) for v in values)
        require(0 < peak < 32767, 'Silent/clipping cue PCM')
    return job, checks, capture, probe, frames, peak


def finalize(args):
    job, checks, capture, probe, frames, peak = validate(args)
    if args.verify_only:
        print('DEMO_CAPTURE_VERIFY_PASS', capture['frames'], probe['format']['duration'])
        return
    evidence = args.evidence_dir
    evidence.mkdir(parents=True, exist_ok=True)
    frames_dir = Path(job['frames_dir'])
    shutil.copy2(Path(job['log']), evidence / 'capture.log')
    shutil.copy2(args.assembly_log, evidence / 'assembly.log')
    shutil.copy2(frames_dir / 'capture.json', evidence / 'native-capture.json')
    frame_hashes = {p.name: sha(p) for p in frames}
    (evidence / 'frame-sha256.json').write_text(json.dumps(frame_hashes, indent=2) + '\n')
    samples = [0, 409, 580, 681, 950, 1010, 1062, 1110, 1230, 1289]
    for frame in samples:
        require(frame < capture['frames'], 'Sample frame outside capture')
        shutil.copy2(frames[frame], evidence / frames[frame].name)
    # Preserve preceding payloads before promoting the verified current source.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    previous = args.output_dir / 'previous-release'
    names = ['GardenOfDreamsDemo.pck', 'GardenOfDreamsDemo.mp4', 'README.md',
             'Run Garden of Dreams.command', 'SHA256SUMS']
    current_inputs = [Path(job['pack']), args.movie, ROOT / 'docs/demo-run-guide.md']
    if any((args.output_dir / name).exists() and sha(args.output_dir / name) != sha(src)
           for name, src in zip(names[:3], current_inputs)):
        previous = previous / sha(args.output_dir / names[0])[:12]
        previous.mkdir(parents=True, exist_ok=True)
        for name in names + ['GardenOfDreamsDemo.zip', 'GardenOfDreamsDemo-macOS.zip']:
            source = args.output_dir / name
            if source.exists() and not (previous / name).exists():
                shutil.copy2(source, previous / name)
    for name, src in zip(names[:3], current_inputs):
        shutil.copy2(src, args.output_dir / name)
    require((args.output_dir / names[3]).is_file(), 'Local launcher is missing')
    payload_hashes = {name: sha(args.output_dir / name) for name in names[:4]}
    (args.output_dir / 'SHA256SUMS').write_text(''.join(
        f'{digest}  {name}\n' for name, digest in payload_hashes.items()))
    archive = args.output_dir / 'GardenOfDreamsDemo.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in names:
            z.write(args.output_dir / name, name)
    with zipfile.ZipFile(archive) as z:
        require(sorted(z.namelist()) == sorted(names) and z.testzip() is None,
                'Archive membership/CRC failure')
        for name, digest in payload_hashes.items():
            with z.open(name) as stream:
                require(hashlib.file_digest(stream, 'sha256').hexdigest() == digest,
                        'Archive payload differs: ' + name)
        require(z.read('SHA256SUMS') == (args.output_dir / 'SHA256SUMS').read_bytes(),
                'Archive checksum manifest differs')
    alias = args.output_dir / 'GardenOfDreamsDemo-macOS.zip'
    shutil.copy2(archive, alias)
    require(sha(alias) == sha(archive), 'Archive aliases differ')
    timeline = dict(capture)
    profile = json.loads(args.profile.read_text())
    for key in ('source_glb_sha256', 'terminal_spill_manifest_sha256',
                'baked_diffuse_shader_sha256', 'mountain_paint_png_sha256',
                'mountain_paint_import_sha256', 'mountain_import_sha256'):
        timeline[key] = profile[key]
    timeline.update(viewport=[1410, 600], pack_sha256=payload_hashes[names[0]],
                    runtime_files_sha256=job['runtime_files_sha256'],
                    movie_sha256=payload_hashes[names[1]], video_codec='h264', audio_codec='aac',
                    backdrop_wash_manifest_sha256=sha(ROOT / 'godot/lightmaps/backdrop-wash/manifest.json'),
                    archive_sha256=sha(archive), payload_sha256=payload_hashes,
                    frame_hashes_sha256=sha(evidence / 'frame-sha256.json'),
                    pcm_peak_s16=peak, cue_mix_sha256=sha(frames_dir / 'cue-mix.wav'),
                    cue_source_sha256={c: sha(ROOT / f'godot/audio/demo/{c}.wav')
                                      for c in sorted({e['cue'] for e in capture['cues']})})
    (ROOT / 'docs/reference/demo-capture-timeline.json').write_text(
        json.dumps(timeline, indent=2) + '\n')
    report = {
        'status': 'passed',
        'scope': 'Current source/runtime native fixed-time capture, assembled original cue PCM and verified local five-file archive. Final art, sustained FPS and full-garden/target-phone acceptance remain open.',
        'source_glb_sha256': job['source_glb_sha256'],
        'runtime_files_sha256': job['runtime_files_sha256'],
        'pack_checks': str(args.pack_checks.resolve().relative_to(ROOT)),
        'capture_log_sha256': sha(evidence / 'capture.log'),
        'assembly_log_sha256': sha(evidence / 'assembly.log'),
        'movie_probe': probe,
        'complete_movie_decode_exit_code': 0,
        'native_frames': len(frames),
        'sample_frame_sha256': {frames[f].name: frame_hashes[frames[f].name] for f in samples},
        'archive_members': names,
        'archive_crc_verified': True,
        'archive_payload_sha256': payload_hashes,
        'archive_sha256': timeline['archive_sha256'],
        'archive_alias_sha256': sha(alias),
        'timeline_sha256': sha(ROOT / 'docs/reference/demo-capture-timeline.json'),
    }
    args.release_report.write_text(json.dumps(report, indent=2) + '\n')
    print('DEMO_RELEASE_PASS', len(frames), timeline['archive_sha256'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-job', required=True, type=Path)
    parser.add_argument('--pack-checks', type=Path, default=ROOT / 'export/roof-current-pack-checks.json')
    parser.add_argument('--profile', type=Path, default=ROOT / 'export/roof-current-demo-profile.json')
    parser.add_argument('--evidence-dir', type=Path, default=ROOT / 'docs/reference/roof-current-runtime/capture')
    parser.add_argument('--release-report', type=Path, default=ROOT / 'export/roof-current-demo-release.json')
    parser.add_argument('--assembly-log', required=True, type=Path)
    parser.add_argument('--movie', required=True, type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build')
    parser.add_argument('--verify-only', action='store_true')
    finalize(parser.parse_args())
