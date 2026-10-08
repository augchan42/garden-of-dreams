from pathlib import Path
import hashlib,json,re,subprocess,shutil
root=Path(json.loads(Path('/tmp/garden-oux-native-source.json').read_text())['folder']).resolve();gd=root/'godot';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=json.loads((root/'actual-import-comparison.json').read_text());assert prior['status']=='actual_import_checks_complete_visual_review_pending'
params=gd/'tests/oux-chart-lightmap.png.import';shutil.copy2(root/'actual-lossless512.png.import',params)
script=(root/'diagnose_oux_chart_candidate.gd').read_text().replace('["portrait","desktop","roof-close","portrait-water"]','["portrait-water"]')
script=script.replace('var target=Vector3(-23,1.0,0)','var target=Vector3(-23,0.5,0)').replace('target)*1.75','target)*2.0').replace('tests/diagnose_oux_chart_candidate.gd','tests/diagnose_oux_portrait512.gd').replace('four views, fresh candidate','one portrait framing view, fresh candidate')
script=script.replace('No old map relabelling, whole-candidate lighting, production adoption, traversal, final art or performance claim.','Only the alternative portrait camera is used (target height0.5, distance multiplier2.0). No old map relabelling, whole-candidate lighting, production adoption, traversal, final art or performance claim.')
(root/'diagnose_oux_portrait512.gd').write_text(script);(gd/'tests/diagnose_oux_portrait512.gd').write_text(script)
report={'status':'running','scope':'The second Ouxiang portrait-water camera proposal with actual lossless512, candidate geometry/map swap only; no canonical runtime camera or scene install.','phases':[]}
def save():(root/'portrait512-phases.json').write_text(json.dumps(report,indent=2)+'\n')
try:
 godot='/Applications/Godot.app/Contents/MacOS/Godot'
 for label,command in [('import',[godot,'--headless','--path',str(gd),'--editor','--import']),('render',[godot,'--path',str(gd),'--script','res://tests/diagnose_oux_portrait512.gd','--','--output='+str(root/'portrait512-captures')])]:
  log=root/('portrait512-'+label+'.log');row={'name':label,'command':command,'log':str(log),'status':'running'};report['phases'].append(row);save()
  with log.open('w') as out:result=subprocess.run(command,cwd=gd,stdout=out,stderr=subprocess.STDOUT)
  row['exit_code']=result.returncode;row['log_sha256']=sha(log);save();text=log.read_text(errors='replace')
  assert result.returncode==0 and not re.search(r'(?m)^(?:SCRIPT ERROR:|ERROR:|.*Parse Error:|.*Assertion failed)',text),text[-3000:]
  row['status']='passed';save()
 d=json.loads((root/'portrait512-captures/report.json').read_text());assert d['status']=='passed' and len(d['views'])==1
 assert d['candidate_import']['width']==512 and d['candidate_import']['data_bytes']==786432 and d['candidate_import']['format']==4
 cases=d['views']['portrait-water']['cases'];assert cases['baseline']['sha256']==cases['baseline-again']['sha256']
 comparison=json.loads((root/'compressed256-captures/report.json').read_text());assert cases['baseline']['sha256']==comparison['views']['portrait-water']['cases']['baseline']['sha256']
 for c in cases.values():assert sha(c['path'])==c['sha256']
 report['status']='technical_checks_complete_visual_review_pending';save();print('OUX_PORTRAIT512_PROPOSAL_PASS',root)
except BaseException as error:
 report['status']='failed';report['error']=str(error);save();raise
