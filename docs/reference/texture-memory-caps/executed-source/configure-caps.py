from pathlib import Path
import re,json,hashlib,sys
TARGETS={'garden-of-dreams_pavilion_basecolor.png':1024,'garden-of-dreams_wall_basecolor.png':1024,'garden-of-dreams_gate-inscription.png':512,'garden-of-dreams_gate-inscription-normal.png':512}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def configure(project):
 project=Path(project).resolve();records=[];pending=[]
 for name,size in TARGETS.items():
  png=project/'assets'/name;sidecar=png.with_suffix('.png.import');before=sidecar.read_text()
  caches=re.findall(r'^path(?:\.[^=]+)?="res://([^"\n]+)"$',before,re.M);assert caches
  cachepaths=[(project/p).resolve() for p in caches]
  assert all(p.parent==(project/'.godot/imported').resolve() and p.name.startswith(name+'-') and p.suffix=='.ctex' for p in cachepaths)
  stems=set(re.sub(r'(?:\.(?:s3tc|etc2))?\.ctex$','',p.name) for p in cachepaths);assert len(stems)==1
  common=next(iter(stems));invalidated=[]
  for p in sorted((project/'.godot/imported').glob(common+'.*')):
   assert p.name in [common+'.md5',common+'.ctex',common+'.s3tc.ctex',common+'.etc2.ctex'],p
   invalidated.append({'path':str(p.relative_to(project)),'sha256':sha(p)})
  after,n=re.subn(r'^process/size_limit=\d+$','process/size_limit='+str(size),before,flags=re.M);assert n==1
  for key,value in [('mipmaps/generate','true'),('detect_3d/compress_to','0')]:assert len(re.findall('^'+re.escape(key)+'='+value+'$',after,re.M))==1
  expected_compress='2' if 'basecolor' in name else '0';assert len(re.findall('^compress/mode='+expected_compress+'$',after,re.M))==1
  pending.append((sidecar,after,[project/r['path'] for r in invalidated]))
  records.append({'source':name,'source_sha256':sha(png),'size_limit':size,'old_import_sha256':hashlib.sha256(before.encode()).hexdigest(),'new_import_sha256':hashlib.sha256(after.encode()).hexdigest(),'invalidated_cache':invalidated})
 for path,text,caches in pending:
  path.write_text(text)
  for cache in caches:cache.unlink()
 assert all(sha(project/'assets'/r['source'])==r['source_sha256'] for r in records)
 return {'status':'configured_reimport_required','scope':'Only four runtime size limits; source PNGs and all other parameters retained; bounded same-asset generated cache+MD5 invalidation.','records':records}
if __name__=='__main__':Path(sys.argv[2]).write_text(json.dumps(configure(Path(sys.argv[1])),indent=2)+'\n')
