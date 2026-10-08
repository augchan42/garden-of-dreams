"""Generate original, deterministic low-volume sound cues for the first-reading demo."""

from pathlib import Path
import math
import random
import struct
import wave

RATE = 22050
OUT = Path(__file__).resolve().parents[1] / "godot" / "audio" / "demo"
OUT.mkdir(parents=True, exist_ok=True)


def write(name, seconds, fn):
    rng = random.Random(2817)
    count = int(seconds * RATE)
    path = OUT / f"{name}.wav"
    with wave.open(str(path), "wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(RATE)
        frames = bytearray()
        for i in range(count):
            t = i / RATE
            sample = max(-1.0, min(1.0, fn(t, rng)))
            frames.extend(struct.pack("<h", int(sample * 32767)))
        sound.writeframes(frames)
    print(path.name, path.stat().st_size)


write("crt", 1.6, lambda t, r: (0.25 * math.sin(2 * math.pi * 60 * t) + 0.06 * (r.random() * 2 - 1)) * min(1, t * 10) * min(1, (1.6 - t) * 5))
write("lanterns", 5.0, lambda t, r: 0.13 * math.sin(2 * math.pi * 110 * t) * (0.7 + 0.3 * math.sin(2 * math.pi * .2 * t)) + 0.018 * (r.random() * 2 - 1))
write("water", 5.0, lambda t, r: 0.08 * (r.random() * 2 - 1) * (0.6 + 0.4 * math.sin(2 * math.pi * .4 * t)) + 0.06 * math.sin(2 * math.pi * 52 * t))
write("tunnel", 4.0, lambda t, r: (0.11 * math.sin(2 * math.pi * (72 + 10 * t / 4) * t) + 0.025 * (r.random() * 2 - 1)) * min(1, t * 3) * min(1, (4 - t) * 2))
write("reveal", 4.0, lambda t, r: (0.16 * math.sin(2 * math.pi * 220 * t) + 0.10 * math.sin(2 * math.pi * 330 * t) + 0.08 * math.sin(2 * math.pi * 440 * t)) * min(1, t * 2) * min(1, (4 - t) * 2))
write("cast", 1.2, lambda t, r: (0.3 * math.sin(2 * math.pi * (480 - 110 * t) * t) + 0.12 * (r.random() * 2 - 1)) * math.exp(-4 * t))
