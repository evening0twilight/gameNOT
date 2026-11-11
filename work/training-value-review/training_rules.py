from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'work/growth-identity-review'))
from relationships import RelationshipLedger,atomic_identity
RULES={'none':dict(xp=0,fatigue=0,cap=0),'legacy':dict(xp=3,fatigue=8,cap=99),'stage6':dict(xp=6,fatigue=4,cap=1),'stage8':dict(xp=8,fatigue=4,cap=1),'stage12':dict(xp=12,fatigue=6,cap=1)}
class StudyLedger(RelationshipLedger):
 def __init__(self,*args,**kw):super().__init__(*args,**kw);self.training_rule='none';self.training_chapters={}
 def training_available(self,a):
  if self.training_rule=='current':return super().training_available(a)
  d=RULES[self.training_rule];chapter=(self.day-1)//6
  return self.healthy(a) and a not in self.used and self.crew[a]['xp']<100 and self.crew[a]['fatigue']+d['fatigue']<=100 and self.training_chapters.get((a,chapter),0)<d['cap']
 @atomic_identity
 def train(self,actors,protocol=None):
  if self.training_rule=='current':return super().train(actors,protocol)
  assert protocol is None and 1<=len(actors)<=2 and all(self.training_available(a) for a in actors)
  d=RULES[self.training_rule];self.claim_project(actors);self.spend(supplies=len(actors));gains={}
  for a in actors:
   gains[a]=min(d['xp'],100-self.crew[a]['xp']);self.crew[a]['xp']+=gains[a];self.crew[a]['fatigue']+=d['fatigue'];key=(a,(self.day-1)//6);self.training_chapters[key]=self.training_chapters.get(key,0)+1
  self.receipt('training',actors=actors,protocol=None,rule=self.training_rule,xp=gains,fatigue=d['fatigue'],supplies=len(actors),projects=1)
  self.receipt('training_gain',actors=actors,gains=gains)
