import hashlib,json,pathlib,tempfile,urllib.parse,urllib.request
root=pathlib.Path(tempfile.mkdtemp(prefix='garden-aojing-material-candidates-'))
names=['Wooden lattice window.jpg','Wooden lattice - Sichuan University Museum - Chengdu, China - DSC06156.jpg']
results=[]
for i,name in enumerate(names):
 params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|sha1|extmetadata','titles':'File:'+name}
 url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
 req=urllib.request.Request(url,headers={'User-Agent':'GardenOfDreamsReferenceReview/1.0'})
 raw=urllib.request.urlopen(req,timeout=45).read(); data=json.loads(raw)
 meta=root/(str(i)+'-metadata.json');meta.write_bytes(raw)
 info=next(iter(data['query']['pages'].values()))['imageinfo'][0]
 req=urllib.request.Request(info['url'],headers={'User-Agent':'GardenOfDreamsReferenceReview/1.0'})
 image=urllib.request.urlopen(req,timeout=45).read();assert hashlib.sha1(image).hexdigest()==info['sha1']
 path=root/(str(i)+'-original.jpg');path.write_bytes(image)
 results.append({'title':name,'file':str(path),'sha256':hashlib.sha256(image).hexdigest(),'commons_sha1':info['sha1'],'source_url':info['url'],'metadata':str(meta),'metadata_sha256':hashlib.sha256(raw).hexdigest(),'extmetadata':info['extmetadata']})
 (root/'results.json').write_text(json.dumps(results,indent=2)+'\n')
 print('ORIGINAL',i,path,flush=True)
pathlib.Path('/tmp/garden-aojing-material-candidates.json').write_text(json.dumps({'folder':str(root)})+'\n')
