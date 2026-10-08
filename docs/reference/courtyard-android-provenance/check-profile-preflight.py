import json,pathlib,sys
sys.path.insert(0,'scripts')
from collect_android_profile import verify_profile_build
new=json.load(open('/tmp/garden-courtyard-android-build.json'));old=json.load(open('/tmp/garden-current-8d-android-filtered-v2-build.json'))
records=[]
for name,build,remote,expected in [('current-local-and-installed',new,new['apk_sha256'],True),('wrong-installed-apk',new,old['apk_sha256'],False),('old-build-without-texture-provenance',old,old['apk_sha256'],False)]:
 calls=[]
 def fake_adb(*args):
  calls.append(list(args))
  if args==('shell','pm','path','org.godotengine.gardendreams.profile'):return b'package:/data/app/task/base.apk\n'
  if args==('shell','sha256sum','/data/app/task/base.apk'):return (remote+'  /data/app/task/base.apk\n').encode()
  raise AssertionError('Unexpected app data, touch or other phone command')
 try:
  result=verify_profile_build(build,fake_adb);passed=True;reason=''
 except AssertionError as e:passed=False;reason=str(e)
 assert passed==expected,(name,reason)
 if name=='old-build-without-texture-provenance':assert calls==[]
 records.append({'case':name,'accepted':passed,'reason':reason,'mocked_adb_calls':calls})
 print(name,'accepted' if passed else 'rejected')
pathlib.Path('/tmp/garden-courtyard-profile-preflight-checks.json').write_text(json.dumps({'status':'three_preflight_cases_passed','scope':'Actual local build/texture/runtime inputs with mocked installed APK responses; no ADB invocation, phone data, taps or device acceptance.','cases':records},indent=2)+'\n')
