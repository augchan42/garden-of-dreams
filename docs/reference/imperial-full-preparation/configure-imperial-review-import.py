"""Configure only the verified imperial receiver in the isolated review tree."""
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
expected='361a67c759974e4fb5897a15d5a7354076ef30392b7a6ed988cca6029f198611'
assert hashlib.sha256((ROOT/'export/garden-of-dreams.glb').read_bytes()).hexdigest()==expected
name='SITE_daguan-lou_MAT_rooftile'
record=json.loads((ROOT/'godot/lightmaps/full-index.json').read_text())[name]
assert record['source_glb_sha256']==expected
path=ROOT/'godot/lightmaps'/(record['texture']+'.import')
assert path.name==name+'.png.import'
before=path.read_text();after=before
for key,value in {'compress/mode':'0','process/size_limit':'512','mipmaps/generate':'false'}.items():
    after,count=re.subn(r'^'+re.escape(key)+r'=.*$',key+'='+value,after,flags=re.M)
    assert count==1,(key,count)
path.write_text(after)
report={'status':'isolated_imperial_import_configured','source_glb_sha256':expected,
        'path':str(path),'before_sha256':hashlib.sha256(before.encode()).hexdigest(),
        'after_sha256':hashlib.sha256(after.encode()).hexdigest(),
        'scope':'Only the current source-matched imperial roof map uses lossless 512px in the separate fixture. Other maps retain the configured 256px baseline and existing courtyard exceptions; actual import/memory/appearance checks remain required.'}
(ROOT/'imperial-import-configuration.json').write_text(json.dumps(report,indent=2)+'\n')
print('IMPERIAL_REVIEW_IMPORT_CONFIGURED')
