"""Use compressed mipmapped 512px imports for the seven new painted titles."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
records = json.loads((root/'export/painted-signs.json').read_text())['placements']
for record in records:
    path = root/'godot/assets'/('garden-of-dreams_'+record['site']+'-title.png.import')
    text = path.read_text()
    for key, value in [('compress/mode', '2'), ('process/size_limit', '512'), ('mipmaps/generate', 'true')]:
        text, count = re.subn('^'+re.escape(key)+'=.*$', key+'='+value, text, flags=re.MULTILINE)
        assert count == 1, (path, key)
    path.write_text(text)
print('GARDEN_SIGN_IMPORTS_CONFIGURED', len(records))
