import hashlib,json,pathlib,subprocess,tempfile,zipfile
root=pathlib.Path('/Users/auchan/projects/garden-of-dreams');work=pathlib.Path(tempfile.mkdtemp(prefix='garden-courtyard-apk-rejections-'))
build=json.load(open('/tmp/garden-courtyard-android-build.json')); inventory='/var/folders/gf/s_g2zvzj3jxbylz3ylbc7k4c0000gn/T/garden-roof-detail-yhh1iheu/production-inventory.json'; old='/tmp/garden-current-8d-android-filtered-v2-build.json'
with zipfile.ZipFile(build['apk']) as z:
 names=z.namelist(); payload=next(n for n in names if n.startswith('assets/.godot/imported/SITE_xiaoxiang-guan_MAT_whitewash.png-') and n.endswith('.ctex'))
cases=[('wrong-manifest','assets/phone-profile-build.json','change',None),('missing-wall-import','assets/lightmaps/SITE_xiaoxiang-guan_MAT_whitewash.png.import','remove','Missing bound import'),('changed-wall-payload',payload,'change','Changed bound payload'),('changed-flora-catalog','assets/assets/flora-placements.json','change-json','Changed runtime, shader or catalog')]
records=[]
for name,target,mode,message in cases:
 apk=work/(name+'.apk');report=work/(name+'-build.json');output=work/(name+'-acceptance.json');log=work/(name+'.log')
 with zipfile.ZipFile(build['apk']) as original,zipfile.ZipFile(apk,'w') as changed:
  for info in original.infolist():
   data=original.read(info.filename)
   if info.filename==target:
    if mode=='remove':continue
    if mode=='change-json':data=data+b' '
    else:data=data[:-1]+bytes([data[-1]^1])
   changed.writestr(info,data)
 record={**build,'apk':str(apk),'apk_sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'apk_bytes':apk.stat().st_size,'synthetic_rejection_case':name}
 report.write_text(json.dumps(record,indent=2)+'\n')
 command=['python3',str(root/'scripts/verify_android_profile_inputs.py'),'--build-report',str(report),'--inventory',inventory,'--previous-build-report',old,'--output',str(output)]
 with log.open('w') as f:r=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
 text=log.read_text();assert r.returncode==1 and not output.exists(),(name,r.returncode,text)
 if message:assert message in text,(name,text)
 records.append({'case':name,'status':'rejected_before_acceptance_output','command':command,'exit_code':r.returncode,'acceptance_output_created':False,'changed_entry':target,'mutation':mode,'apk_sha256':record['apk_sha256'],'apk_bytes':record['apk_bytes'],'log':str(log)})
 print(name,'rejected',flush=True)
(work/'report.json').write_text(json.dumps({'status':'four_corrupted_archive_cases_rejected','scope':'Synthetic modified copies of the current actual APK; original APK, fixture and production unchanged. No install or device sampling.','cases':records},indent=2)+'\n')
pathlib.Path('/tmp/garden-courtyard-apk-rejections.json').write_text(json.dumps({'folder':str(work)},indent=2)+'\n')
