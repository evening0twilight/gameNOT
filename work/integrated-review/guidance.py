"""UI-independent scheduling policy. No screen or novice-behavior claims."""
class Guidance:
 def __init__(self,mode='light'):
  assert mode in ['light','off','detailed'];self.mode=mode;self.seen=set();self.pending={};self.counts={};self.round_shown=set();self.log=[];self.suppressed=0;self.warnings=set()
 def offer(self,key,mission,rnd,priority=1,relevant=True,essential=False,decision=None,decision_state=None):
  if essential:
   assert decision is not None
   token=(mission,decision,decision_state)
   if token not in self.warnings:self.warnings.add(token);self.log.append(dict(mission=mission,round=rnd,key=key,kind='decision_confirmation',blocks_only_commit=True))
   return
  if key in self.seen or self.mode=='off' or not relevant:self.suppressed+=1;return
  self.pending[key]=dict(key=key,mission=mission,round=rnd,priority=priority)
 def boundary(self,mission,rnd,relevant_keys):
  # Remove stale targets instead of presenting last turn's invalid explanation.
  self.pending={k:v for k,v in self.pending.items() if k in relevant_keys and v['mission']==mission}
  if not self.pending or (mission,rnd) in self.round_shown:return
  limit=3 if mission=='M01' else 1
  if self.counts.get(mission,0)>=limit:return
  x=sorted(self.pending.values(),key=lambda x:(-x['priority'],x['round'],x['key']))[0]
  self.pending.pop(x['key']);self.seen.add(x['key']);self.counts[mission]=self.counts.get(mission,0)+1;self.round_shown.add((mission,rnd));self.log.append({**x,'round':rnd,'kind':'nonmodal_card','steals_focus':False,'auto_action':False})
 def scene(self,board,trace,restricted=False):
  mid=board['id'];intro={'G02'}
  if any(o.get('opportunity_deadline') for o in board['objectives']):intro.add('G08')
  if any(o['kind']=='channel' for o in board['objectives']):intro.add('G12')
  if mid=='M04':intro.add('G06')
  if mid=='M24':self.offer('G15',mid,1,essential=True,decision='final_route_commit')
  for rnd in sorted({x['round'] for x in trace}):
   keys=set(intro)
   actions=[x for x in trace if x['round']==rnd]
   if any(x['action']=='cooperation_refused' for x in actions):keys.add('G07')
   if any(x['action']=='service_watch' for x in actions):keys.add('G16')
   for action in actions:
    if action['action']=='machine_destroyed':self.offer('G17',mid,rnd,essential=True,decision='destroy:'+action['source'],decision_state='physical_asset_loss')
   if mid=='M17' and any(x.get('target') in ['repair1','repair2','isolate'] and x['action'] in ['interact','protected_work'] for x in actions):self.offer('G13',mid,rnd,essential=True,decision='first_branch_commit')
   if any(x['action']=='move' for x in actions):keys.add('G01')
   if any(x['action'] in ['stabilize','pickup','lin_1','lin_3'] for x in actions):keys.add('G03')
   if any(x['action']=='interact' for x in actions) and any(o['prerequisites'] for o in board['objectives']):keys.add('G05')
   if any(x['action'] in ['protected_work','relay_carry'] for x in actions):keys.add('G10')
   if any(x['action']=='downed' for x in actions):keys.add('G11')
   for key in sorted(keys):self.offer(key,mid,rnd,priority={'G07':4,'G08':3,'G16':3,'G06':2,'G03':2}.get(key,1))
   self.boundary(mid,rnd,keys)
  for card in self.log:
   if card['mission']==mid and card['key']=='G08':
    card['copy']='额外机会：'+'；'.join(o['label']+'需在第'+str(o['opportunity_deadline'])+'轮末前完成' for o in board['objectives'] if o.get('opportunity_deadline'))+'。可以兼顾，也可只完成主目标。'
  self.pending={}
 def camp(self,day,recruit=False):
  mid='camp'+str(day);keys={'G04'}|({'G09'} if recruit else set())
  for key in sorted(keys):self.offer(key,mid,0)
  self.boundary(mid,0,keys);self.pending={}
