"""Offline 0.8 evaluation adapter; not imported by game runtime.
Inputs are authored factual receipts, not guessed text/LLM interpretation.
"""
from pathlib import Path
from copy import deepcopy
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'system-audit'))
from reference import Direction,value
DATA=json.loads((Path(__file__).resolve().parents[2]/'game/data/final_design/player_experience_contract.json').read_text())
PROFILES={a['id']:a['traits'] for a in DATA['actors']}
FAMILIES={'breach':(12,8,'promise',False),'unfairness':(10,8,'fairness',False),'humiliation':(14,10,'humiliation',False),'concealment':(18,12,'promise',True),'cost_overrun':(6,3,'fairness',False)}
def clamp(x,lo,hi):return max(lo,min(hi,x))

def evaluate(event,observer,target,profile,prior_r,affinities):
 assert event['id'] and event['mission'] and observer!=target
 assert event['outcome'] in ['success','partial','failed']
 assert event['kind'] in [*FAMILIES,'cooperation']
 shares=event.get('responsibility',{})
 assert all(0<=v<=1 for v in shares.values()) and sum(shares.values())<=1+1e-8
 assert 0<=event.get('extra_cost',0)<=3 and 0<=event.get('self_control',0)<=1
 if 'start' in event and 'finish' in event:assert event['finish']>=event['start']
 known=observer in event['known_by']
 witnesses=set(event['witnesses'])&set(event['known_by'])
 focus=sorted([(affinities.get(a,0),a) for a in witnesses if a not in [observer,target]],key=lambda v:(-v[0],v[1]))
 care,who=focus[0] if focus and focus[0][0]>=60 else (0,None)
 salience=profile['face_concern']*care/100
 late=bool((event.get('time_relevant') and event.get('finish',0)>event.get('agreed_finish',float('inf'))) or (event.get('start_relevant') and event.get('start',0)>event.get('agreed_start',float('inf'))))
 # Late start is meaningful only through resulting known cost/commitment, never a second charge.
 weather=bool(event.get('weather_hazard_experienced'))
 stress=min(12,(4 if event['outcome']!='success' else 0)+2*event.get('extra_cost',0)+int(late)+int(weather)) if known else 0
 meaningful=known and target in event.get('contributors',[]) and observer in event.get('contributors',[]) and event.get('voluntary_contribution',False)
 confirmed=known and event.get('evidence')=='verified' and shares.get(target,0)>0 and event['kind'] in FAMILIES
 pending=known and event.get('evidence')=='ambiguous' and event.get('suspect')==target and event.get('visible_cue',False) and event['outcome']!='success'
 suspicion=round(min(4,4*(.25+.5*profile['externalize']+.25*prior_r/100)*(1-.5*profile['evidence_need'])),3) if pending else 0
 bad=event['outcome']!='success' or event.get('extra_cost',0)>0
 self_load=min(6,(4 if event['outcome']!='success' else 0)+event.get('extra_cost',0))*profile['self_demand']*(.25+.75*event.get('self_control',0)) if known and bad else 0
 if self_load and who:self_load=min(6,self_load+salience)
 # Success never cancels an explicit breach, nor credits the same event as reliable.
 positive=meaningful and event['outcome']=='success' and event['kind']=='cooperation' and not event.get('explicit_violation',False)
 trust=2+int(salience>=.5) if positive else 0
 relief=min(3,1+2*profile['repair_openness']+salience) if positive and event.get('relevant_category') else 0
 if confirmed and FAMILIES[event['kind']][3]:expression='calm_firm_boundary'
 elif confirmed and salience>=.5:expression='public_restraint_private_concern'
 elif confirmed:expression='state_specific_objection'
 elif self_load>=2 and profile['self_demand']>=.75:expression='self_questioning_request_review'
 elif suspicion:expression='tentative_question_not_accusation'
 elif self_load>=2:expression='self_questioning_request_review'
 elif positive:expression='shared_relief' if who else 'acknowledge_contribution'
 else:expression='factual_update'
 return dict(known=known,confirmed=confirmed,share=shares.get(target,0),kind=event['kind'],stress=stress,self_load=round(self_load,3),suspicion=suspicion,focus=who,salience=round(salience,3),expression=expression,trust_gain=trust,relief=round(relief,3),relief_category=event.get('relevant_category'),positive=positive)

class Session:
 def __init__(self,observer,profile=None):
  self.observer=observer;self.profile=deepcopy(profile or PROFILES[observer]);self.directions={};self.self_load=0.;self.stress=10.;self.self_band=0;self.seen=set();self.pending={};self.positive_budget={};self.relief_budget={};self.load_budget={};self.stress_budget={};self.calm_budget={};self.rested=set();self.supported=set();self.receipts=[]
 def direction(self,target):return self.directions.setdefault(target,Direction())
 def apply(self,event,affinities=None):
  before=deepcopy(self.__dict__)
  try:return self._apply(event,affinities or {})
  except Exception:self.__dict__=before;raise
 def _apply(self,event,affinities):
  if self.observer not in event['known_by']:return {'unknown':True}
  token=event['id']
  if token in self.seen:return {'duplicate':True}
  targets=set(event.get('responsibility',{}))|set(event.get('contributors',[]))|({event['suspect']} if event.get('suspect') else set())
  targets.discard(self.observer)
  # Evaluate all directions from the SAME pre-event self state.
  prior_stress=self.stress;rows={};evaluations=[]
  for target in sorted(targets):
   d=self.direction(target);before_r=d.resentment(event['day']);before_t=d.trust
   v=evaluate(event,self.observer,target,self.profile,before_r,affinities);evaluations.append(v)
   if v['confirmed']:
    severity,loss,category,severe=FAMILIES[v['kind']]
    d.add(event['id'],event['day'],severity=severity,loss=loss,category=category,severe=severe,share=v['share'],stress=prior_stress,sensitivity=event.get('sensitivity',1),promise=event.get('promise'),warned=event.get('warned',False),deliberate=event.get('deliberate',False),occurrence_day=event.get('occurred_day'))
    self.pending.pop((event['id'],target),None)
   if v['suspicion']:
    existing=sum(x['amount'] for (eid,t),x in self.pending.items() if t==target and x['mission']==event['mission'])
    self.pending[(event['id'],target)]={'amount':min(v['suspicion'],max(0,4-existing)),'mission':event['mission'],'status':'unverified','occurred':event['day'],'stress_at_event':prior_stress}
   key=(event['mission'],target)
   gain=min(v['trust_gain'],max(0,3-self.positive_budget.get(key,0)),100-d.trust)
   d.trust+=gain;self.positive_budget[key]=self.positive_budget.get(key,0)+gain
   amount=min(v['relief'],max(0,6-self.relief_budget.get(key,0)))
   candidates=[m for m in d.memories if m.get('active',True) and not m.get('revoked') and not m['severe'] and m['category']==v['relief_category']]
   spent=0
   for m in sorted(candidates,key=lambda m:(m['day'],str(m['id']))):
    current=value(m,event['day']);cut=min(current,amount-spent)
    if current and cut:m['strength']*=1-cut/current;spent+=cut
    if spent>=amount:break
   self.relief_budget[key]=self.relief_budget.get(key,0)+spent
   rows[target]={**v,'r_before':round(before_r,3),'r_after':round(d.resentment(event['day']),3),'trust_before':before_t,'trust_after':round(d.trust,3),'actual_relief':round(spent,3),'actual_trust_gain':gain}
  # An actor alone or all responsibility on self still receives personal evaluation.
  if not evaluations:evaluations=[evaluate(event,self.observer,'__context__',self.profile,0,affinities)]
  mid=event['mission'];load=min(max(v['self_load'] for v in evaluations),max(0,8-self.load_budget.get(mid,0)))
  stress=min(max(v['stress'] for v in evaluations),max(0,12-self.stress_budget.get(mid,0)))
  calm=min(2 if any(v['positive'] for v in evaluations) else 0,max(0,4-self.calm_budget.get(mid,0)))
  if event.get('personal_effects_accounted',False):load=stress=calm=0
  self.self_load=min(100,self.self_load+load);self.stress=clamp(self.stress+stress-calm,0,100)
  self.load_budget[mid]=self.load_budget.get(mid,0)+load;self.stress_budget[mid]=self.stress_budget.get(mid,0)+stress;self.calm_budget[mid]=self.calm_budget.get(mid,0)+calm
  self.update_band();self.seen.add(token)
  row={'id':event['id'],'mission':mid,'directions':rows,'self_load':round(self.self_load,3),'load_delta':round(load,3),'stress':self.stress,'stress_delta':stress-calm,'self_band':self.self_band,'basic_actions_changed':False}
  self.receipts.append(row);return row
 def update_band(self):
  while self.self_band and self.self_load<({1:30,2:55}[self.self_band]):self.self_band-=1
  while self.self_band<2 and self.self_load>=(40,70)[self.self_band]:self.self_band+=1
 def resolve_pending(self,event_id,target):
  return self.pending.pop((event_id,target),None) # proof closes explanation; no points or pardon reward
 def confirm(self,event):
  """Late verified evidence replaces a provisional explanation, not a second shock."""
  pending=[v for (eid,t),v in self.pending.items() if eid==event['id']]
  if not pending:return False
  assert event['evidence']=='verified' and self.observer in event['known_by'] and event['kind'] in FAMILIES
  shares=event.get('responsibility',{});assert all(0<=v<=1 for v in shares.values()) and sum(shares.values())<=1+1e-8
  severity,loss,category,severe=FAMILIES[event['kind']]
  for target,share in shares.items():
   if target==self.observer or not share:continue
   self.direction(target).add(event['id'],event['day'],severity=severity,loss=loss,category=category,severe=severe,share=share,stress=pending[0]['stress_at_event'],occurrence_day=pending[0]['occurred'],deliberate=False)
  self.pending={k:v for k,v in self.pending.items() if k[0]!=event['id']}
  return True
 def night(self,day,recovery_project=False,meaningful_support=False):
  if day in self.rested:return False
  self.rested.add(day);extra=2 if meaningful_support and day not in self.supported else 0
  if extra:self.supported.add(day)
  self.self_load=max(0,self.self_load-2-4*int(recovery_project)-extra);self.stress=max(0,self.stress-8);self.update_band();return True

def tutorial_gate(secured,goal,chosen_method,skipped=False):
 return bool(skipped or goal in secured) # no prescribed technique or mandatory click history

def usable_hints(candidates,state_version):
 """Candidates must come from current canonical legality query, not static tooltips."""
 return [x for x in candidates if x['legal'] and x['state_version']==state_version][:3]
