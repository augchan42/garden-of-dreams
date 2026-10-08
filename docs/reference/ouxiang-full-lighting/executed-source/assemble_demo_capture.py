"""Assemble native Godot frame captures with the original demo cue PCM.

The capture logs actual cue transitions. Mix the same gains and loop/stop rules
as demo_audio.gd; do not use shortened audio from an occluded native movie.
"""
import argparse
import json
from pathlib import Path
import subprocess
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('frames_dir', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
report = json.loads((args.frames_dir / 'capture.json').read_text())
fps, count = report['fps'], report['frames']
assert fps == 30 and count >= 1200, 'Incomplete first-reading route capture'
frames = sorted(args.frames_dir.glob('frame-*.png'))
assert len(frames) == count
assert all(p.name == f'frame-{i:05d}.png' for i, p in enumerate(frames)), 'Frame gap'
cues = report['cues']
assert {'crt', 'lanterns', 'tunnel', 'reveal', 'water', 'cast'} <= {e['cue'] for e in cues}
rate = 22050
samples = count * rate // fps
mix = np.zeros(samples, dtype=np.float64)
for index, event in enumerate(cues):
    cue = event['cue']
    with wave.open(str(ROOT / 'godot/audio/demo' / (cue + '.wav'))) as source:
        assert (source.getnchannels(), source.getsampwidth(), source.getframerate()) == (1, 2, rate)
        pcm = np.frombuffer(source.readframes(source.getnframes()), dtype='<i2').astype(np.float64) / 32768
    start = event['frame'] * rate // fps
    end = samples if cue in ('lanterns', 'water') else min(samples, start + len(pcm))
    stop_cues = {'crt', 'lanterns', 'water', 'tunnel'} if cue == 'lanterns' else ({'crt', 'lanterns', 'water'} if cue == 'water' else ({'reveal'} if cue == 'tunnel' else set()))
    for later in cues[index + 1:]:
        if later['cue'] in stop_cues:
            end = min(end, later['frame'] * rate // fps)
            break
    if end <= start:
        continue
    clip = np.resize(pcm, end - start) if cue in ('lanterns', 'water') else pcm[:end - start]
    gain = 10 ** ((-30 if cue in ('lanterns', 'water') else -22) / 20)
    mix[start:end] += clip * gain
assert np.max(np.abs(mix)) < 1, 'Audio clipping'
audio = args.frames_dir / 'cue-mix.wav'
with wave.open(str(audio), 'wb') as target:
    target.setparams((1, 2, rate, samples, 'NONE', 'not compressed'))
    target.writeframes(np.rint(mix * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-y', '-framerate', str(fps), '-i', str(args.frames_dir / 'frame-%05d.png'), '-i', str(audio), '-frames:v', str(count), '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(args.output)], check=True)
print('DEMO_ASSEMBLY_PASS', count, count / fps, len(cues))
