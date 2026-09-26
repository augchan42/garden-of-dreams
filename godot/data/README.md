# Local hexagram catalog

`hexagrams.json` contains the 64 King Wen patterns used by the offline first-reading demo. Lines are stored bottom to top (`0` broken, `1` solid), following `getHexagramLines` in the sister application at `../8bitoracle-next/src/lib/hexagramDerivations.ts`. Numbers, names, meanings and trigram pairs come from `../8bitoracle-next/src/constants/hexagrams.ts`, SHA256 `134637e2fb107ff3a7f09199aa2aafeb9cabd03bb20db410d248bad072188aa9`.

Regenerate with `python3 scripts/build_demo_hexagram_catalog.py` when that sibling repository is available. The checked-in JSON lets Godot run independently. It contains pattern metadata, not private readings or AI-generated interpretation.
