extends Node

const CUES = {
 "crt": "res://audio/demo/crt.wav",
 "lanterns": "res://audio/demo/lanterns.wav",
 "water": "res://audio/demo/water.wav",
 "tunnel": "res://audio/demo/tunnel.wav",
 "reveal": "res://audio/demo/reveal.wav",
 "cast": "res://audio/demo/cast.wav",
}

var players: Dictionary = {}
var last_cue = ""

func _exit_tree() -> void:
 for player in players.values():player.stop()

func _ready() -> void:
 for cue in CUES:
  var player = AudioStreamPlayer.new()
  player.name = cue.capitalize() + "Audio"
  player.stream = load(CUES[cue])
  if cue in ["lanterns", "water"]:
   player.stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
  player.volume_db = -30.0 if cue in ["lanterns", "water"] else -22.0
  add_child(player)
  players[cue] = player

func enter_room(id: String) -> void:
 for cue in ["lanterns", "water"]:players[cue].stop()
 match id:
  "terminal_room":last_cue = "crt";players.crt.play()
  "rockery_gate":last_cue = "lanterns";players.lanterns.play()
  "qinfang_ting":last_cue = "water";players.water.play()

func start_tunnel() -> void:
 last_cue = "tunnel"
 players.lanterns.stop()
 players.tunnel.play()

func reveal() -> void:
 last_cue = "reveal"
 players.tunnel.stop()
 players.reveal.play()

func cast() -> void:
 last_cue = "cast"
 players.cast.play()
