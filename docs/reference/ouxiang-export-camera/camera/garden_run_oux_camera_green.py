from pathlib import Path
import hashlib,json,re,subprocess
root=Path(json.loads(Path('/tmp/garden-oux-camera-review.json').read_text())['folder']).resolve();gd=root/'godot'
report={'status':'running','phases':[],'scope':'Native changed portrait camera, tea/look, actual western/nunnery physics routes and existing density UI regression; final art and phone acceptance remain separate.'}
def save():(root/'green-phases.json').write_text(json.dumps(report,indent=2)+'\n')
commands=[('new-framing',['--script','res://tests/test_oux_portrait_framing.gd','--','--output='+str(root/'new-framing')]),('density-framing',['--script','res://tests/test_oux_portrait_framing.gd','--','--density','--output='+str(root/'density-framing')]),('western-route',['--headless','--script','res://tests/test_western_route.gd']),('nunnery-route',['--headless','--script','res://tests/test_nunnery_route.gd']),('mobile-ui',['--headless','--script','res://tests/test_mobile_ui_scaling.gd'])]
try:
 for label,args in commands:
  command=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(gd),*args]
  log=root/(label+'.log');row={'name':label,'command':command,'log':str(log),'status':'running'};report['phases'].append(row);save()
  with log.open('w') as out:
   p=subprocess.Popen(command,cwd=gd,stdout=out,stderr=subprocess.STDOUT);row['pid']=p.pid;save();row['exit_code']=p.wait()
  row['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest();save();text=log.read_text(errors='replace')
  assert row['exit_code']==0 and not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:)',text),text[-4000:]
  marker={'new-framing':'OUXIANG_FRAMING_PASS','density-framing':'OUXIANG_FRAMING_PASS','western-route':'WESTERN_ROUTE_PASS','nunnery-route':'NUNNERY_ROUTE_PASS','mobile-ui':'MOBILE_UI_SCALE_PASS'}[label]
  assert marker in text,text[-4000:]
  row['status']='passed';save()
 old=json.loads((root/'old-framing/report.json').read_text());new=json.loads((root/'new-framing/report.json').read_text())
 assert new['status']=='passed'
 protected=[]
 for a,b in zip(old['views'],new['views'],strict=True):
  assert a['requested_size']==b['requested_size'] and a['viewport']==b['viewport']
  for room in a['poses']:
   if room!='ouxiang_xie' or a['requested_size'][0]>a['requested_size'][1]:
    assert a['poses'][room]==b['poses'][room],(room,a['requested_size'])
    protected.append({'room':room,'size':a['requested_size']})
 report['unchanged_camera_checks']=protected;report['status']='technical_checks_complete_visual_review_pending';save();print('OUX_CAMERA_GREEN_VERIFIED',root)
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
