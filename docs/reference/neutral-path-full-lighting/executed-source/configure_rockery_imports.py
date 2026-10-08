"""Enable full-resolution compressed atlas imports for standalone rockery."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
paths=list((R/'godot/assets/kits/rockery').glob('*_pavilion_*.png.import'))
assert len(paths)==36,len(paths)
for path in paths:
 text=path.read_text()
 for key,value in {'compress/mode':'2','compress/high_quality':'false','process/size_limit':'0','mipmaps/generate':'true'}.items():
  text,count=re.subn('^'+re.escape(key)+'=.*$',key+'='+value,text,flags=re.M);assert count==1,(path,key)
 path.write_text(text)
print('ROCKERY_GPU_COMPRESSION_CONFIGURED',len(paths))
