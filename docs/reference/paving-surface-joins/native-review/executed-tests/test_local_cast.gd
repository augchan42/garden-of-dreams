extends SceneTree
func _initialize() -> void:call_deferred("run")
func fail(message:String) -> void:push_error(message);quit(1)
func run() -> void:
 var model=load("res://runtime/local_cast.gd").new()
 if model.by_pattern.size()!=64:fail("Catalog must contain 64 patterns");return
 for row in model.by_pattern.values():
  var bits=[]
  for character in str(row.lines):bits.append(int(character))
  if model.lookup(bits).number!=row.number:fail("Catalog round trip failed");return
 if model.lookup([1,1,1,1,1,1]).number!=1 or model.lookup([0,0,0,0,0,0]).number!=2 or model.lookup([1,0,0,0,1,0]).number!=3:
  fail("King Wen mapping or bottom-to-top order is wrong");return
 var stable=model.from_coin_values([7,8,7,8,7,8])
 if stable.moving_lines.size()!=0 or stable.primary.number!=stable.transformed.number:fail("Stable cast mismatch");return
 var changing=model.from_coin_values([6,7,8,9,6,9])
 if changing.moving_lines!=[1,4,5,6] or changing.primary_lines!=[0,1,0,1,0,1] or changing.transformed_lines!=[1,1,0,0,1,0]:
  fail("Moving line transformation is wrong");return
 for bad in [[],[7,7,7,7,7,10],[7,7,7,7,7,7.0],[7,7,7,7,7,"8"]]:
  if not model.from_coin_values(bad).is_empty():fail("Invalid cast accepted");return
 var rng=RandomNumberGenerator.new();rng.seed=2817
 for i in range(100):
  var cast_result=model.cast(rng)
  if cast_result.is_empty() or cast_result.coin_values.size()!=6 or cast_result.primary_lines.size()!=6:
   fail("Random cast produced invalid result");return
  for value in cast_result.coin_values:
   if value<6 or value>9:fail("Coin outcome outside 6..9");return
 print("LOCAL_CAST_PASS: 64 canonical patterns, bottom-to-top mapping, moving lines and seeded draws")
 quit(0)
