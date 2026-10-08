"""Keep the three bulletin-hall paintings within the garden texture budget."""

from pathlib import Path
import re


root = Path(__file__).resolve().parents[1]
for name in ("hall-title", "bamboo-scroll", "plum-scroll"):
    path = root / f"godot/assets/garden-of-dreams_{name}.png.import"
    text = path.read_text()
    for key, value in (
        ("compress/mode", "2"),
        ("process/size_limit", "1024"),
        ("mipmaps/generate", "true"),
    ):
        text, count = re.subn(r"^" + re.escape(key) + r"=.*$", f"{key}={value}", text, flags=re.MULTILINE)
        assert count == 1, (path, key, count)
    path.write_text(text)
print("STUDY_TEXTURE_IMPORT_PASS: three paintings use compressed 1024-pixel imports")
