"""Original synthesized Foley and impacts for synchronized runtime feedback."""
from pathlib import Path
import math, random, wave, struct, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'game/assets/audio_feedback';OUT.mkdir(exist_ok=True)
RATE=22050
DURATIONS={'move':.13,'attack':.32,'push':.3,'work':.32,'pickup':.3,'drop':.22,'stabilize':.48,'extract':.5,'injury':.28}
records=[]
for seed,(name,duration) in enumerate(DURATIONS.items()):
 rng=random.Random(881+seed);samples=[];filtered=0
 for i in range(int(RATE*duration)):
  t=i/RATE;p=t/duration;noise=rng.uniform(-1,1);filtered=.7*filtered+.3*noise
  env=min(1,t/.004)*(1-p)**2
  if name=='move':v=(.5*filtered+.3*math.sin(2*math.pi*90*t))*math.exp(-t*28)
  elif name in ('attack','drop','injury'):v=(.5*noise+.5*math.sin(2*math.pi*(100-45*p)*t))*env
  elif name in ('push','pickup'):v=(.6*filtered+.15*math.sin(2*math.pi*150*t))*math.sin(math.pi*p)**2
  elif name=='work':v=(.55*noise+.3*math.sin(2*math.pi*1300*t))*env*(1 if int(t/.08)%2==0 else .15)
  else:
   frequencies=[523.25,659.25,783.99] if name=='extract' else [659.25,783.99]
   v=sum(math.sin(2*math.pi*f*t) for f in frequencies)/len(frequencies)*math.sin(math.pi*p)**2*.6
  samples.append(int(max(-.9,min(.9,v*.38))*32767))
 path=OUT/(name+'.wav')
 with wave.open(str(path),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
 records.append({'path':str(path.relative_to(ROOT)),'duration':duration,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(ROOT/'docs/p4-feedback-audio.json').write_text(json.dumps({'method':'Original deterministic synthesis: filtered noise footsteps, cloth, impacts, tool strikes and harmonic rescue cues. No external samples.','assets':records,'listening_acceptance':False},ensure_ascii=False,indent=2)+'\n')
print('FEEDBACK_AUDIO_GENERATED',len(records))
