from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design';V='0.17-training-value'
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'work/growth-identity-review/relationships.py';s=p.read_text()
s=s.replace('self.pact_revision_days={}','self.pact_revision_days={};self.training_completed={}') if 'self.training_completed={}' not in s else s
a=s.index(' def training_slots(self,a):') if ' def training_slots(self,a):' in s else s.index(' def mentor_candidates(self):');b=s.index(' def dispatch_options(self,party):')
s=s[:a]+''' def training_slots(self,a):
  # Chapters unlock curriculum stages. Unused stages persist; pre-join stages
  # are represented by the recruit's existing XP and cannot be purchased again.
  if a not in self.crew:return 0
  unlocked=max(0,(min(self.day,23)-1)//6-(CHARS[a]['join']-1)//6+1)
  return max(0,unlocked-self.training_completed.get(a,0))
 def training_available(self,a):
  return self.phase=='camp' and 1<=self.day<=23 and self.healthy(a) and a not in self.used and self.crew[a]['xp']<100 and self.crew[a]['fatigue']+6<=100 and self.training_slots(a)>0
 def mentor_candidates(self):
  out=[];chapter=(self.day-1)//6
  for mentor,learner in itertools.permutations(self.crew,2):
   if not self.training_available(learner) or not self.healthy(mentor) or mentor in self.used or self.crew[mentor]['fatigue']+6>100:continue
   amount=min(24,self.crew[mentor]['xp']-self.crew[learner]['xp'],100-self.crew[learner]['xp'])
   if amount<=min(12,100-self.crew[learner]['xp']) or (learner,chapter) in self.apprentices or not self.pact_for([mentor,learner]):continue
   out.append((mentor,learner,amount))
  return out
 @atomic_identity
 def mentor(self,mentor,learner):
  options=self.mentor_candidates();assert (mentor,learner) in [(m,l) for m,l,v in options]
  amount=next(v for m,l,v in options if (m,l)==(mentor,learner));assert self.projects<2 and self.resources['supplies']>=2
  self.claim_project([mentor,learner]);self.spend(supplies=2)
  for a in [mentor,learner]:self.crew[a]['fatigue']+=6
  self.crew[learner]['xp']+=amount;self.apprentices.add((learner,(self.day-1)//6));self.training_completed[learner]=self.training_completed.get(learner,0)+1
  self.receipt('mentorship',mentor=mentor,learner=learner,xp=amount,projects=1,supplies=2,fatigue_each=6,stage_used=self.training_completed[learner],history=self.pair_history([mentor,learner]))
  self.receipt('training_gain',actors=[learner],gains={learner:amount},source='mentorship')
 @atomic_identity
 def train(self,actors,protocol=None):
  assert protocol is None and 1<=len(actors)<=2 and all(self.training_available(a) for a in actors)
  self.claim_project(actors);self.spend(supplies=len(actors));gains={}
  for a in actors:
   gains[a]=min(12,100-self.crew[a]['xp']);self.crew[a]['xp']+=gains[a];self.crew[a]['fatigue']+=6;self.training_completed[a]=self.training_completed.get(a,0)+1
  self.receipt('training',actors=actors,protocol=None,rule='stage12_carry',xp=gains,fatigue=6,supplies=len(actors),projects=1,stages={a:self.training_completed[a] for a in actors})
  self.receipt('training_gain',actors=actors,gains=gains,source='solo')
''' +s[b:];p.write_text(s)
normal='阶段训练：每人1物资，1–2人合用1项目，各+min(12,100-当前经验)、+6疲劳，同人每晚仍限1项目。每章开放1个训练阶段，未用阶段保留可后补；入队前章节不补发，已体现在入队基础经验。普通训练与关系带教共用学员阶段，满100经验不收款，不能在第24日虚构营地。'
mentor='共同带教：1项目、2物资，两人各+6疲劳；学员+min(24,导师经验−学员经验,100−学员经验)，导师不获经验。仅实际收益高于此刻普通训练时提供。消耗学员1个训练阶段，且每学员每章最多1次带教。仍需已有关系约定、两次真实共同任务贡献与当前同意；不发好感，不修复旧怨，不教授导师专属技能。'
p=F/'growth_identity_contract.json';d=json.loads(p.read_text());d['version']=V;d['training'].update(normal=normal,purpose='用一次明确投资提前取得专长，或让实际准备上场的替补补课。自然出勤经验、后勤经验、等级阈值、入队经验全部保持不变。',presentation='同时显示实际XP增量、跨级能力、尚余训练阶段与未用阶段保留、今晚/次晨疲劳、下一次计划出勤是否可用。若没有已计划出勤，显示“这次培养尚无已确认使用机会”。不保证训练自动带来更多奖励。',recommendation='建议须有下一次已公开任务用途；并排显示不训练、普通训练、符合条件的带教和休息。阶段不在章末失效，不用红点催促花完。未发生的任务XP只显示为估计，不能当成既得经验。');d['positive_relationships']['mentorship']=mentor;d['ordinary_growth_findings']='0.17以所有8角色、主力/轮换/后备、主线/支线出勤、普通/最高难度及环境变体继续复核。旧3XP/8疲劳训练已替换；单次可取得有意义进步，次数受可保留的阶段限制。收益必须看实际提前出勤和战斗结果，不能只看结局等级。';put(p,d)
p=F/'progression_relationship.json';d=json.loads(p.read_text());d['version']=V;d['training_rule']=normal;put(p,d)
p=ROOT/'game/data/rules.json';d=json.loads(p.read_text());d['progression'].update(training_xp=12,training_fatigue=6,training_stages_per_chapter=1,training_unused_stages_carry=True,training_prejoin_stages_granted=False);put(p,d)
p=ROOT/'game/data/campaign_economy_contract.json';d=json.loads(p.read_text());d['version']=V
# Locate the authored training economics without rewriting unrelated balances.
def patch(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='training' and isinstance(v,dict) and 'xp_each' in v:v.update(xp_each=12,fatigue_each=6,stage_rule='1 new stage per chapter since recruitment; unused carry; shared with mentorship')
   else:patch(v)
 elif isinstance(x,list):
  for v in x:patch(v)
patch(d);put(p,d)
p=F/'integration.json';d=json.loads(p.read_text());d['version']=V
# Current economy_growth contract may be nested; replace only that field.
def integration(x):
 if isinstance(x,dict):
  if 'economy_growth' in x:
   z=x['economy_growth'];z['training']=normal+' 四项情境协作仍无需另行购买学习；不得恢复旧协议经验。';z['fatigue']='白天无出勤/后勤可休整-16，睡眠-12；晚间训练另+6，白天休整照常。训练不是出勤，不产生任务、运输、共同保护或履约事实。';z['training_persistence']='保存training_completed按角色计数、apprentices每学员每章带教记录、训练回执及used/project。重谈关系、读档、跨章不能重置；失效操作整笔回滚。'
  for v in x.values():integration(v)
 elif isinstance(x,list):
  for v in x:integration(v)
integration(d);put(p,d)
p=F/'player_choice_contract.json';d=json.loads(p.read_text());d['version']=V
for k,v in d.items():
 if isinstance(v,dict) and 'xp' in v and 'rule' in v and '普通训练' in str(v):v.update(xp='当前阶段训练12经验，不发协作解锁或好感奖励',rule=normal)
put(p,d)
p=F/'design_manifest.json';d=json.loads(p.read_text());d['version']=V;d['domains']['training_value']='training_value_contract.json';put(p,d)
put(F/'training_value_contract.json',dict(version=V,formal_development=False,normal=normal,mentorship=mentor,natural_growth_unchanged=['main XP 5/3/1','side XP 3/1/0','support XP2','levels0/12/28/48/72/100','recruit chapter floors0/12/28/48'],intent='Buy earlier deployable capability, not more mandatory nights. Natural growth stays fully viable.',stage_topics=['基础动作与风险演练','复杂地形及设备处置','多点任务与交接','撤离与应急复盘'],topics_are='章节课程名称，不是新技能树或额外能力门锁；未用课程可补做。'))
# Existing integrated runner must query legal training options, not attempt stale daily purchases.
p=ROOT/'work/ordinary-player-review/campaigns.py';s=p.read_text().replace("g.crew[a]['fatigue']+8<=100 and g.crew[a]['xp']<100","g.training_available(a)").replace("g.crew[a]['xp']+3 for t in [12,28,72]","g.crew[a]['xp']+12 for t in [12,28,72]");p.write_text(s)
print('Applied0.17stage training; naturalgrowthunchanged')

p=ROOT/'work/growth-identity-review/model.py';s=p.read_text();needle="  assert medical_capacity in [2,3]\n"
if "if 'gear' in kw:kw['gear']=deepcopy(kw['gear'])" not in s:s=s.replace(needle,needle+"  if 'gear' in kw:kw['gear']=deepcopy(kw['gear'])\n")
p.write_text(s)
