from pathlib import Path
import json,hashlib,shutil,gzip
from PIL import Image
r=Path('/Users/auchan/projects/garden-of-dreams');p=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-desktop-framing';a=p/'archive-prepared'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert json.loads((p/'installed-pipeline.json').read_text())['status']=='installed_checks_passed'
assert json.loads((p/'green-pipeline.json').read_text())['status']=='focused_checks_passed'
assert not a.exists(),'Archive is immutable; do not overwrite'
a.mkdir(parents=True)
for folder in ['green-normal','green-touch','green-density','installed-normal','installed-western','comparison-originals']:
 shutil.copytree(p/folder,a/folder)
for name in ['native-input-cpu-proposals.json','touch-cpu-proposals.json','compact-cpu-proposals.json','input-fixture.json','input-collection-pipeline.json','first-baseline-rejection.json','draw-wait-diagnosis.json','green-pipeline.json','installed-pipeline.json','green-normal.log','green-touch.log','green-density.log','western-route.log','installed-normal.log','installed-western.log','cold-import.log','extract-native-inputs.log','executed-input-collector.gd','executed-native-measure.py','first-executed-measure.py','executed-red-test.gd','executed-comparison-renderer.gd','executed-green-test.gd','production-before-entry_route.gd','production-before-test_ziling_framing.gd']:
 shutil.copy2(p/name,a/name)
for name in ['red-normal','first-green-touch','rejected-density','timeout-green-touch','before-draw-fix-green-touch']:
 source=p/name;target=a/'rejected'/name;target.mkdir(parents=True)
 if (source/'report.json').exists():shutil.copy2(source/'report.json',target/'report.json')
 if (source/'arrival-desktop.png').exists() and name in ['red-normal','first-green-touch']:shutil.copy2(source/'arrival-desktop.png',target/'arrival-desktop.png')
for name in ['first-green-touch.log','timeout-green-touch.log','before-draw-fix-green-touch.log','first-green-pipeline.json','timeout-green-pipeline.json']:
 if (p/name).exists():shutil.copy2(p/name,a/'rejected'/name)
for name in ['garden_measure_native_ziling_desktop.py','garden_search_compact_desktop.py','garden_check_desktop_framing.py','garden_resume_desktop_framing.py','garden_check_installed_desktop.py','garden_render_western_framing.gd']:
 shutil.copy2(Path('/tmp')/name,a/name)
(a/'native-inputs.json.gz').write_bytes(gzip.compress((p/'native-inputs.json').read_bytes(),mtime=0))
# All 13 installed normal originals must reproduce the isolated fixture exactly.
assert all(sha(f)==sha(p/'green-normal'/f.name) for f in (p/'installed-normal').glob('*.png'))
for mode in ['normal','touch','density']:
 d=json.loads((p/('green-'+mode)/'report.json').read_text());assert not d['errors'];assert d['route_sha256']==sha(r/'godot/runtime/entry_route.gd');assert d['test_sha256']==sha(r/'godot/tests/test_ziling_framing.gd')
 for row in d['rows']:
  f=Path(row['capture']);assert sha(f)==row['sha256'];assert list(Image.open(f).size)==row['pixels']
print('ARCHIVE_PREPARED',len(list(a.rglob('*'))))
