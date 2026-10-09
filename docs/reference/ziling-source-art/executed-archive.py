from pathlib import Path
import hashlib,json,shutil
r=Path('/Users/auchan/projects/garden-of-dreams');w=r/'.superpowers/sdd/2026-09-23-garden-completion/ziling-source-art';s=w/'reeds-volume';v=w/'lit-native-review';out=r/'docs/reference/ziling-source-art'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cp(p,rel):
 q=out/rel;q.parent.mkdir(parents=True,exist_ok=True)
 if p.is_dir():shutil.copytree(p,q,ignore=shutil.ignore_patterns('__pycache__','*.blend1','*.blend2'))
 else:shutil.copyfile(p,q)
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
a=json.loads((w/'adoption/application.json').read_text());assert a['status']=='working_source_adopted_installed_checks_passed'
assert not out.exists();out.mkdir()
for n in ['candidate-contract-preservation.json','candidate-source-contract.json','reed-dimension-contract.json','saved-source-inventory.json','all-standalone-kit-material-audit.json','standalone-water-all-material-audit.json','standalone-water-material-audit.json','reed-volume-command.json','reed-volume-build.log']:
 cp(w/n,'source/'+n)
cp(w/'executed-helpers','executed-helpers')
for n in ['export-preservation.json','source-review.json']:cp(w/'waterline'/n,'source/waterline-'+n)
for p in (w/'adoption-attempt1-rolled-back').iterdir():
 if p.is_file() or p.name=='installed-ziling':cp(p,'installed-first-timeout-rolled-back/'+p.name)
for n in ['export-preservation.json','reed-source-review.json','lighting-preparation.json','full-lighting-inputs.json','lighting-preparation-logs']:cp(s/n,'source/'+n)
frozen=json.loads((s/'full-lighting-inputs.json').read_text())['files'];locations={}
for rel,h in frozen.items():
 assert sha(s/rel)==h,rel
 if (r/rel).is_file() and sha(r/rel)==h:locations[rel]={'sha256':h,'location':'repository/'+rel}
 else:
  cp(s/rel,'source/frozen-inputs/'+rel);locations[rel]={'sha256':h,'location':'archive/source/frozen-inputs/'+rel}
write(out/'source/frozen-input-byte-locations.json',locations)
b=json.loads((s/'export/full-lighting-refresh.json').read_text())
for p in b['phases']:cp(Path(p['log']),'source/bake-logs/'+p['name']+'.log')
for n in ['water-kit-parity','flora-reexport-debug','flora-collider-preview-repair','flora-saved-source-reexports','flora-saved-source-reexports-repaired','flora-saved-source-reexports-visible','flora-generator-reproduction','saved-source-reproduction']:
 p=w/n
 if p.exists():cp(p,'reproduction/'+n)
for n in ['review-pipeline.json','review-pipeline-resume1.json','review-pipeline-resume2.json','fixture-preparation.json','flora-runtime-atlas-preservation.json','direct-original-visual-review.json','native-import-contract.json','texture-memory-normal.json','texture-memory-demo.json','lit-lod1-terminal-result.json']:
 cp(v/n,'review/'+n)
for n in ['review-logs','review-logs-resume1','review-logs-resume2','review-captures','review-captures-resume2','review-captures-lit-lod1']:cp(v/n,'review/'+n)
for p in v.glob('*.py'):cp(p,'review/executed-helpers/'+p.name)
for p in v.glob('*.gd'):cp(p,'review/executed-helpers/'+p.name)
for n in ['application.json','plan.json','executed-adoption.py','installed-import-contract.json','installed-palette-normal.json','installed-palette-demo.json','installed-ziling']:cp(w/'adoption'/n,'installed/'+n)
for p in (w/'adoption').glob('*.log'):cp(p,'installed/'+p.name)
# Preserve rejected visual treatments, not their abandoned source trees.
for n in ['reed-native-comparison','reed-bold-native-comparison','reed-volume-native-comparison']:
 cp(w/n,'comparisons/'+n)
shutil.copyfile(__file__,out/'executed-archive.py')
# Refresh the current arrival illustration files without relabelling past evidence.
for mode,prefix in [('desktop','route-'),('portrait','route-mobile-')]:
 for p in (v/'review-captures-resume2'/('arrivals-'+mode)).glob('*.png'):
  q=r/'docs/reference'/(p.stem+'-full-baked.png');shutil.copyfile(p,q)
files={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
write(w/'archive-preliminary-index.json',{'files':files,'count':len(files),'pngs':sum(n.endswith('.png') for n in files),'scope':'Preliminary byte copy check; README and final immutable index are written after installed-original review and final documentation.'})
assert all(sha(out/n)==h for n,h in files.items());print('ZILING_ARCHIVE_COPIED',len(files),sum(n.endswith('.png') for n in files))
