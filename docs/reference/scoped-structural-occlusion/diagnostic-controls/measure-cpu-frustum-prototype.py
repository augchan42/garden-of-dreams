#!/usr/bin/env python3
"""Measure only the owned native fixture at explicit steady-state phase markers."""
import json,os,selectors,subprocess,time
from pathlib import Path
ROOT=Path('/tmp/garden-occlusion-views-20261010')
command=['/Applications/Godot.app/Contents/MacOS/Godot','--path',str(ROOT/'godot'),'--script','res://tests/benchmark_occlusion_cpu.gd']
process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0)
selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ)
starts={};phases={};deadline=time.monotonic()+200
report={'scope':'Owned native process CPU user+system time from macOS ps, sampled at steady-state fixture phase markers. Includes all process threads; not GPU time, phone or sustained acceptance. CPU time has0.01s resolution; host sampling lag/query cost is retained.','pid':process.pid,'command':command,'phases':phases}
def snapshot():
 start=time.monotonic();raw=subprocess.check_output(['ps','-p',str(process.pid),'-o','time='],text=True).strip();end=time.monotonic()
 parts=[float(p) for p in raw.split(':')];seconds=0.0
 for part in parts:seconds=seconds*60+part
 return {'monotonic_seconds':end,'process_cpu_seconds':seconds,'ps_time':raw,'query_seconds':end-start}
buffer=""
with (ROOT/'cpu-host.log').open('w') as log:
 while True:
  if time.monotonic()>deadline:
   process.terminate();process.wait(timeout=10);raise RuntimeError('Owned CPU diagnostic deadline')
  if not selector.select(timeout=1):
   if process.poll() is not None:break
   continue
  chunk=os.read(process.stdout.fileno(),65536)
  if not chunk:
   if process.poll() is not None:break
   continue
  buffer+=chunk.decode('utf-8')
  while '\n' in buffer:
   line,buffer=buffer.split('\n',1)
   log.write(line+'\n');log.flush()
   if line.startswith('CPU_PHASE_START '):
    label=line.strip().split(' ',1)[1];starts[label]=snapshot()
   elif line.startswith('CPU_PHASE_END '):
    label,native=line.strip().split(' ',2)[1:];end=snapshot();start=starts[label]
    wall=end['monotonic_seconds']-start['monotonic_seconds'];cpu=end['process_cpu_seconds']-start['process_cpu_seconds']
    assert wall>7 and cpu>0
    phases[label]={'start':start,'end':end,'wall_seconds':wall,'process_cpu_seconds':cpu,'cpu_seconds_per_wall_second':cpu/wall,'native':json.loads(native)}
    (ROOT/'cpu-host.json').write_text(json.dumps(report,indent=2)+'\n')
    print('OWNED_CPU_PHASE',label,'cpu_s',round(cpu,3),'wall_s',round(wall,3),'p95_ms',phases[label]['native']['interval_p95_ms'],flush=True)
process.wait(timeout=10)
report['exit_code']=process.returncode
assert process.returncode==0 and len(phases)==9
report['pairs']={}
for room in ('terminal_room','rockery_gate','qinfang_ting'):
 a=phases[room+'-disabled'];b=phases[room+'-enabled'];c=phases[room+'-disabled_repeat'];baseline=(a['cpu_seconds_per_wall_second']+c['cpu_seconds_per_wall_second'])/2
 report['pairs'][room]={'baseline_mean_cpu_seconds_per_wall_second':baseline,'candidate_cpu_seconds_per_wall_second':b['cpu_seconds_per_wall_second'],'candidate_over_baseline':b['cpu_seconds_per_wall_second']/baseline,'baseline_repeat_ratio':c['cpu_seconds_per_wall_second']/a['cpu_seconds_per_wall_second']}
(ROOT/'cpu-host.json').write_text(json.dumps(report,indent=2)+'\n')
print('OWNED_CPU_DIAGNOSTIC_PASS',json.dumps(report['pairs']),flush=True)
