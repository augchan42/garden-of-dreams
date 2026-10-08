from pathlib import Path
import json,subprocess,hashlib,re
first=Path(json.loads(Path('/tmp/garden-official-trailer-reference.json').read_text())['folder']);night=Path(json.loads(Path('/tmp/garden-official-night-trailer-reference.json').read_text())['folder']);out=night/'selected';out.mkdir()
items={r['name']:(root,r) for root in [first,night] for r in json.loads((root/'report.json').read_text())['items']}
selections=[('daoxiang-cun',1,'come-drink',24.6),('aojing-guan',1,'magic-blade',5.0),('longcui-an',1,'magic-blade',3.0),('qinfang-ting',2,'magic-blade',53.0),('ouxiang-xie',1,'enchanting-shadow',15.0),('daguan-lou',1,'enchanting-shadow',17.0),('tubi-tang',1,'enchanting-shadow',3.0),('ziling-zhou',1,'enchanting-shadow',11.0)]
report={'status':'running','scope':'Distinct full-size decoded trailer frames; no crop/color/scale changes. Exact source stream PTS is logged; no required slot acceptance before original-frame review.','frames':[]}
for site,slot,name,seconds in selections:
 root,row=items[name];path=out/(site+'-night.png');log=out/(site+'-extraction.log')
 cmd=['/opt/homebrew/bin/ffmpeg','-v','info','-threads','1','-i',row['path'],'-map','0:v:0','-vf',f'select=gte(t\\,{seconds}),showinfo','-frames:v','1','-threads','1',str(path)]
 with log.open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0,(site,log.read_text()[-1000:])
 matches=re.findall(r'n:\s+0\s+pts:\s+(\d+)\s+pts_time:([\d.]+)',log.read_text());assert len(matches)==1,site
 record={'site':site,'slot':slot,'trailer':name,'path':str(path),'command':cmd,'actual_stream_pts':int(matches[0][0]),'actual_stream_pts_seconds':float(matches[0][1]),'requested_seconds':seconds,'frame_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_video_sha256':row['sha256'],'log':str(log),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()};report['frames'].append(record)
 (out/'extraction-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('EXTRACTED',site,record['actual_stream_pts_seconds'],flush=True)
report['status']='decoded_frame_review_pending';(out/'extraction-report.json').write_text(json.dumps(report,indent=2)+'\n')
