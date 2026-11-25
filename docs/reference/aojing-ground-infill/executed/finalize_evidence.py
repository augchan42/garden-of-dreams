from pathlib import Path
import json,hashlib,shutil
r=Path(__file__).resolve().parent;repo=Path('/Users/auchan/projects/garden-of-dreams');pub=repo/'docs/reference/aojing-ground-infill';arc=repo/'.superpowers/sdd/2026-09-23-garden-completion/aojing-ground-lit-20261013';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((r/'android-full-build.json').read_text());proof=json.loads((r/'android-payload-verification.json').read_text());jobs=json.loads((r/'offline-android-jobs.json').read_text());assert jobs['status']=='full_offline_apk_verified_uninstalled' and proof['status']=='offline_preflight_and_packaged_payloads_passed' and jobs['apk_sha256']==proof['apk_sha256']==build['apk_sha256']==sha(Path(build['apk']))
for n in ['android-full-build.json','android-payload-verification.json','offline-android-jobs.json']:
 shutil.copy2(r/n,pub/'proof'/n)
for n in ['android-full-build.log','android-payload-verification.log','finalize_evidence.py']:
 shutil.copy2(r/n,pub/'executed'/n)
# Retain the current original APK and its exact staged producer/input fixture.
apk=arc/'android'/Path(build['apk']).name;apk.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(Path(build['apk']),apk);assert sha(apk)==build['apk_sha256']
fixture=Path(build['fixture']);names=['phone-profile-build.json','phone_profile.gd','project.godot','export_presets.cfg']
for n in names:
 p=fixture/n
 if p.exists():out=arc/'android/fixture'/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
manifest=json.loads((fixture/'phone-profile-build.json').read_text());print('MANIFEST_KEYS',list(manifest))
for n in ['scripts/build_android_profile.py','scripts/collect_android_profile.py','scripts/android_profile_modes.py','scripts/android_texture_provenance.py','scripts/verify_android_apk_payload.py']:
 p=repo/n;out=arc/'android/producer'/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
for folder in ['installed-validation-logs','installed-native-ground','installed-native-corridor']:
 for p in (r/folder).rglob('*'):
  if p.is_file() and p.suffix in ['.json','.log','.png']:
   out=arc/p.relative_to(r);out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
for p in r.iterdir():
 if p.is_file() and p.suffix in ['.json','.py','.gd','.log']:
  out=arc/p.name;shutil.copy2(p,out)
readme=pub/'README.md';s=readme.read_text();s=s.replace('A current combined offline Android export is running; no APK completion, final art, target-phone,2020 Adreno or sustained-budget acceptance is claimed. The previous offline APK predates both this ground addition and the stage-kit input change and remains uninstalled.',f"The current full diagnostic APK({build['apk_bytes']}bytes, SHA-256`{build['apk_sha256']}`) passes actual offline packaged-payload and current producer/input provenance checks. It remains uninstalled. No final art, target-phone,2020 Adreno or sustained-budget acceptance is claimed. Earlier APKs predate the current inputs.");readme.write_text(s)
for n in ['docs/sites/aojing-guan.md','docs/build-status.md']:
 p=repo/n;s=p.read_text().replace('Current offline export/final branch review pending;', 'Current full offline APK/payload provenance passes, uninstalled; final branch review pending;');p.write_text(s)
for base in [pub,arc]:
 d=json.loads((base/'files.json').read_text());d['files']={str(p.relative_to(base)):sha(p) for p in sorted(base.rglob('*')) if p.is_file() and p!=base/'files.json'};(base/'files.json').write_text(json.dumps(d,indent=2)+'\n')
 for n,h in d['files'].items():assert sha(base/n)==h,n
 print('GROUND_FINAL_HASH_PASS',base,len(d['files']))
print('GROUND_APK_VERIFIED',build['apk_sha256'],build['apk_bytes'])
