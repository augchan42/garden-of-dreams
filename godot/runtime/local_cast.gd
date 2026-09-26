extends RefCounted
## Offline three-coin casting. Each line is bottom-to-top and sums three coin values (2 or 3).
const DATA_PATH="res://data/hexagrams.json"
var by_pattern: Dictionary={}

func _init() -> void:
 var parsed=JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
 if typeof(parsed)!=TYPE_ARRAY or parsed.size()!=64:push_error("Hexagram catalog is missing or incomplete");return
 for row in parsed:
  if typeof(row)!=TYPE_DICTIONARY or not row.has("lines"):push_error("Invalid hexagram catalog row");by_pattern.clear();return
  var key=str(row.lines)
  if key.length()!=6 or by_pattern.has(key):push_error("Duplicate hexagram pattern");by_pattern.clear();return
  by_pattern[key]=row

func lookup(lines: Array) -> Dictionary:
 if lines.size()!=6:return {}
 var key=""
 for value in lines:
  if typeof(value)!=TYPE_INT or (value!=0 and value!=1):return {}
  key+=str(value)
 return by_pattern.get(key,{})

func from_coin_values(values: Array) -> Dictionary:
 if values.size()!=6 or by_pattern.size()!=64:return {}
 var primary=[];var transformed=[];var moving=[]
 for i in range(6):
  var value=values[i]
  if typeof(value)!=TYPE_INT or value<6 or value>9:return {}
  var bit=1 if value%2==1 else 0
  primary.append(bit)
  transformed.append(1-bit if value==6 or value==9 else bit)
  if value==6 or value==9:moving.append(i+1)
 var first=lookup(primary);var second=lookup(transformed)
 if first.is_empty() or second.is_empty():return {}
 return {"coin_values":values.duplicate(),"primary_lines":primary,"transformed_lines":transformed,"moving_lines":moving,"primary":first,"transformed":second}

func cast(rng: RandomNumberGenerator) -> Dictionary:
 var values=[]
 for i in range(6):
  var sum=6
  for coin in range(3):sum+=rng.randi_range(0,1)
  values.append(sum)
 return from_coin_values(values)
