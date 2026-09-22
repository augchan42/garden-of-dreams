"""Keep full atlas resolution while enabling GPU compression and mipmaps."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
paths=list((R/'godot/assets/kits/wall').glob('*_wall_*.png.import'))
assert len(paths)==48,len(paths)
paths+=list((R/'godot/assets').glob('garden-of-dreams_wall_*.png.import'))
for path in paths:
 text=path.read_text()
 for key,value in {'compress/mode':'2','compress/high_quality':'false','process/size_limit':'0','mipmaps/generate':'true'}.items():
  text,count=re.subn('^'+re.escape(key)+'=.*$',key+'='+value,text,flags=re.M)
  assert count==1,(path,key)
 path.write_text(text)
print('WALL_GPU_COMPRESSION_CONFIGURED',len(paths))
