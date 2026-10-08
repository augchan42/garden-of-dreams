from pathlib import Path
import hashlib,json,urllib.request,datetime,concurrent.futures
root=Path('/tmp/garden-moon-gate-reference-candidates');root.mkdir(exist_ok=True)
items=[('sohu-moon-gate.jpeg','https://5b0988e595225.cdn.sohucs.com/images/20190922/060d5b51cc0645b784e5b81aa13fb22e.jpeg'),('yuanye-moon-gate.jpg','https://www.yuanyebei.com/bbs/data/attachment/forum/202411/06/162053nszlkoslses6t2ll.jpg'),('sohu-source.html','https://www.sohu.com/picture/342607749'),('yuanye-source.html','https://www.yuanyebei.com/bbs/forum.php?mod=viewthread&tid=26589')]
def fetch(pair):
 name,url=pair
 row={'file':name,'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url,timeout=25) as r:
   data=r.read();row.update({'http_status':r.status,'response_url':r.url,'headers':dict(r.headers),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
  (root/name).write_bytes(data)
 except Exception as e:row['error']=str(e)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,items))
(root/'download-provenance.json').write_text(json.dumps({'scope':'Reference candidates only; not accepted slots until direct original-image and source review. Original response bytes retained without edits.','rows':rows},indent=2)+'\n')
print(json.dumps(rows,indent=2))
