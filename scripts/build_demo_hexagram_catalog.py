"""Extract the sister application's authoritative King Wen mapping for the local demo."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
source=R.parent/'8bitoracle-next/src/constants/hexagrams.ts'
s=source.read_text()
start=s.index('export const hexagramData = [')
end=s.index('export const hexagramMapping = {')
metadata=s[start:end]
patterns=s[end:]
trigrams={'Heaven':'111','Earth':'000','Water':'010','Fire':'101','Mountain':'001','Wind':'011','Lake':'110','Thunder':'100'}
rows=[]
for n in range(1,65):
 match=re.search(r'\bnumber:\s*'+str(n)+r'\s*,',metadata)
 assert match, n
 next_match=re.search(r'\bnumber:\s*'+str(n+1)+r'\s*,',metadata[match.end():])
 chunk=metadata[match.start():match.end()+next_match.start()] if next_match else metadata[match.start():]
 def field(key):
  value=re.search(r'\b'+key+r':\s*"([^"]+)"',chunk)
  assert value,(n,key)
  return value.group(1)
 name=field('chinese');meaning=field('meaning');upper=field('topTrigram');lower=field('bottomTrigram')
 pattern=re.search(r'^\s*'+str(n)+r':\s*"([01]{6})"',patterns,re.M)
 assert pattern,n
 bits=trigrams[lower]+trigrams[upper]
 assert bits==pattern.group(1),(n,bits,pattern.group(1))
 rows.append({'number':n,'chinese':name,'meaning':meaning,'lower':lower,'upper':upper,'lines':bits})
assert len(rows)==64 and len({r['lines'] for r in rows})==64
out=R/'godot/data/hexagrams.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('DEMO_HEXAGRAM_CATALOG_PASS: 64 unique bottom-to-top patterns and canonical names')
