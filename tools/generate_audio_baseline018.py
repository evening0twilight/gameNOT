"""Six original deterministic musical loops. No external samples or copied melody."""
from pathlib import Path
import math, wave, struct, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'game/assets/audio018';OUT.mkdir(exist_ok=True)
RATE=22050;DURATION=24
SCORES={
 'title':([50,57,60,65],[74,69,72,65,67,69,62,65],.8),
 'briefing':([48,55,58,62],[67,70,74,70,65,67,62,60],.65),
 'battle':([45,52,57,60],[69,64,67,64,62,60,64,57],.45),
 'camp':([53,60,65,69],[77,72,74,69,70,72,65,69],.8),
 'story':([50,57,62,65],[74,72,69,65,67,62,65,69],.6),
 'ending':([48,55,60,64],[72,76,79,76,74,72,67,72],.75),
}
def hz(midi):return 440*2**((midi-69)/12)
records=[]
for name,(chord,melody,intensity) in SCORES.items():
 buf=bytearray();peak=0;first=None;last=0;sq=0
 for i in range(RATE*DURATION):
  t=i/RATE;v=0
  for j,note in enumerate(chord):
   freq=round(hz(note)*DURATION)/DURATION
   v+=.022*math.sin(2*math.pi*freq*t)*(.7+.3*math.cos(2*math.pi*t/DURATION+j))
  step=int(t/3);dt=t%3;freq=hz(melody[step]);env=(1-math.exp(-dt*18))*math.exp(-dt*1.6)
  v+=intensity*.055*env*(math.sin(2*math.pi*freq*dt)+.25*math.sin(2*math.pi*freq*2*dt))
  # Gentle low pulse for planning/field; a cyclic envelope keeps the seam quiet.
  if name in ('battle','briefing'):
   dt=t%.75;v+=.025*math.exp(-dt*14)*math.sin(2*math.pi*55*dt)
  v*=min(1,t/.08,(DURATION-t)/.08)
  peak=max(peak,abs(v));sq+=v*v
  sample=int(max(-1,min(1,v))*32767)
  if first is None:first=sample
  last=sample;buf.extend(struct.pack('<h',sample))
 p=OUT/(name+'.wav')
 with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(buf)
 records.append(dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),seconds=DURATION,peak=peak,rms=math.sqrt(sq/(RATE*DURATION)),seam_difference=abs(first-last),context=name))
(ROOT/'docs/baseline018-audio.json').write_text(json.dumps(dict(method=__doc__,sample_rate=RATE,assets=records,review='Signal integrity checked; subjective listening acceptance pending.'),ensure_ascii=False,indent=2)+'\n')
print('BASELINE018_AUDIO',len(records))
