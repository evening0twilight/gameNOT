"""Original, deterministic synthesized cues; no recordings, samples or external assets."""
from pathlib import Path
import math, random, wave, struct, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'game/assets/audio_p4'
RATE=22050
CUES={
 'ui_focus':(660,.06),'ui_confirm':(880,.12),'ui_cancel':(440,.1),'ui_error':(160,.18),'ui_page':(520,.1),'ui_save':(1046,.15),
 'move':(330,.09),'attack':(120,.14),'push':(190,.18),'stabilize':(740,.18),'pickup':(390,.12),'work':(240,.17),'drop':(280,.12),'extract':(660,.28),
 'machine_scout':(240,.23),'machine_welder':(110,.3),'machine_hauler':(90,.3),'machine_skimmer':(510,.23),'machine_relay':(920,.22),'machine_sentinel':(70,.35),
 'objective':(784,.32),'injury':(140,.3),'end_round':(360,.22),'ending':(523,.7),
}
def write(name,samples,loop=False):
 p=OUT/(name+'.wav')
 with wave.open(str(p),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
  w.writeframes(b''.join(struct.pack('<h',int(max(-.9,min(.9,v))*32767)) for v in samples))
 return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'duration_seconds':len(samples)/RATE,'loop':loop}
def cue(freq,duration,seed):
 rng=random.Random(seed);result=[]
 for i in range(int(RATE*duration)):
  t=i/RATE;phase=t/duration;envelope=min(1,t/.008)*(1-phase)**2
  tone=math.sin(2*math.pi*freq*t*(1-.08*phase))+.2*math.sin(2*math.pi*freq*2*t)
  result.append(.2*envelope*(tone+.08*rng.uniform(-1,1)))
 return result
records=[]
for i,(name,(freq,duration)) in enumerate(CUES.items()):records.append(write(name,cue(freq,duration,i)))
for mode,notes in [('camp',[146.83,174.61,220,261.63]),('field',[110,130.81,164.81,196])]:
 duration=16;result=[];rng=random.Random(1804)
 for i in range(RATE*duration):
  t=i/RATE;v=0
  for j,f in enumerate(notes):
   # Integer cycle counts make the generated loop periodic; quiet sustained harmonic bed.
   f=round(f*duration)/duration
   v+=.025*math.sin(2*math.pi*f*t)*(.65+.35*math.sin(2*math.pi*t/16+j)**2)
  v+=.016*math.sin(2*math.pi*round(notes[0]/2*duration)/duration*t)
  result.append(v)
 records.append(write('ambient_'+mode,result,True))
manifest={'created':'2026-11-06','method':'Original deterministic PCM synthesis using tools/generate_audio_p4.py; no external samples, copied composition, voice, purchase or commissioned material.','license':'Project-authored audio; no third-party audio license required.','review':'Generated candidate audio; human listening acceptance pending.','sample_rate':RATE,'assets':records}
(ROOT/'docs/p4-audio-assets.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('AUDIO_P4_GENERATED',len(records))
