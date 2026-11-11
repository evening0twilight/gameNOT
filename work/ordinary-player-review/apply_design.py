"""Fix observed ordinary-play failure chains and fact/wording mismatches; design only."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design';V='0.16-ordinary-player'
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'work/growth-identity-review/model.py';s=p.read_text();needle=' def working(self,e):'
patch=""" def propagate_unavailable(self):
  changed=True
  while changed:
   changed=False
   for o in self.objects.values():
    if o['done'] or o['secured'] or o['lost']:continue
    blocker=next((d for d in o['prerequisites'] if self.objects[d]['lost'] and not self.objects[d]['done']),None)
    if blocker:
     o['lost']=True;o['dependency_blocked']=True;o['unavailable_reason']=blocker
     self.receipt('objective_unavailable',target=o['id'],source='lost_uncompleted_prerequisite',prerequisite=blocker);changed=True
 def environment(self):
  result=super().environment();self.propagate_unavailable();return result
"""
if ' def propagate_unavailable(self):' not in s:s=s.replace(needle,patch+needle)
# Specialty cargo motion must feed the same loop-erased contribution trail as walking.
old="""  before=deepcopy(self.__dict__)
  try:return self._identity_use(actor,key,target,destination,blocked)
  except Exception:self.__dict__=before;raise"""
new="""  before=deepcopy(self.__dict__)
  try:
   result=self._identity_use(actor,key,target,destination,blocked)
   if key in ['xu_1','jiang_1']:
    old_h=before['h'][actor];cargo=old_h['carry']
    if cargo is not None:
     end=self.h[actor]['p'] if key=='xu_1' else self.h[target]['p'];start=old_h['p']
     if start!=end:
      dx=0 if start[0]==end[0] else 1 if end[0]>start[0] else -1;dy=0 if start[1]==end[1] else 1 if end[1]>start[1] else -1
      path=[(start[0]+dx*i,start[1]+dy*i) for i in range(distance(start,end)+1)]
      self.receipt('transport_path',actor=actor,cargo=cargo,path=path,at=end,via=key)
   return result
  except Exception:self.__dict__=before;raise"""
if old in s:s=s.replace(old,new)
p.write_text(s)
p=ROOT/'work/campaign-review/ledger_review.py';s=p.read_text()
s=s.replace("    if a=='mo':self.receipt('public_record_release',privacy='redacted')", "    # A publication plan is not an actual publication receipt.")
s=s.replace("  else:self.receipt('story_choice',actor=a,node=nid,choice=n['choices'][0]['id'])", "  else:\n   choice=choice_id or n['choices'][0]['id'];assert choice in {x['id'] for x in n['choices']}\n   self.receipt('story_choice',actor=a,node=nid,choice=choice)")
s=s.replace("self.receipt('tool_purchase',item=item,discount_parts=discount)","self.receipt('tool_purchase',item=item,discount_parts=discount,paid_credits=e['price_credits'],paid_parts=e['price_parts']-discount,discount_token=token if discount else None)")
needle=' def current_r(self,pair):'
patch=""" @atomic
 def undo_tool_purchase(self,item):
  assert self.phase in ['briefing','after_main','camp'] and self.active is None and item not in ['crowbar','medkit'] and item in self.tools
  reverted={r['purchase_seq'] for r in self.records if r['kind']=='tool_purchase_undone'}
  purchase=next((r for r in reversed(self.records) if r['kind']=='tool_purchase' and r['item']==item and r['seq'] not in reverted),None)
  assert purchase is not None and not any(r['kind']=='assignment' and r['seq']>purchase['seq'] for r in self.records)
  assert 'paid_credits' in purchase and 'paid_parts' in purchase
  self.tools.remove(item);self.resources['credits']+=purchase['paid_credits'];self.resources['parts']+=purchase['paid_parts']
  if purchase.get('discount_token'):self.discounts.discard(purchase['discount_token'])
  self.receipt('tool_purchase_undone',item=item,purchase_seq=purchase['seq'],credits=purchase['paid_credits'],parts=purchase['paid_parts'])
 @atomic
 def release_redacted(self,evidence_id):
  assert self.phase=='camp' and 'mo' in self.plans and self.healthy('mo') and evidence_id in self.evidence
  assert not any(r['kind']=='public_record_release' and r.get('evidence_id')==evidence_id and r.get('privacy')=='redacted' for r in self.records)
  self.claim_project(['mo'])
  self.receipt('public_record_release',privacy='redacted',evidence_id=evidence_id,source='explicit_camp_review',actor='mo',scope='verified_technical_facts_only_no_identity_fields')
"""
if ' def undo_tool_purchase(' not in s:s=s.replace(needle,patch+needle)
p.write_text(s)
# All scripts retain authored voice, but do not assume the wrong actor caused a later dispute.
p=F/'character_scripts.json';scripts=json.loads(p.read_text());names={x['id']:x['name'] for x in json.loads((ROOT/'game/data/characters.json').read_text())}
for n in scripts['personal']:
 actor=n['actor'];name=names[actor]
 n['later_breach_self']=name+'：记录里的这件事由我负责。之前做到过的还在，但不能拿它抵掉这一次。'
 n['later_breach_other']=name+'：这件事影响到了我，但责任不能因为我在场就算到我头上。请按我们实际知道的记录说清。'
 n['later_breach_unknown']=name+'：结果我们看到了，原因还没查清。先别替任何人认责，也别拿以前的合作盖过去。'
 n['later_breach']=n['later_breach_unknown']
 n['injured_opening']=['休养处。相关记录由值班人放在床边；不播放现场搬运、拆装或值岗动作。']+[t for t in n['opening'] if '：' in t]
 if not n['injured_opening'][1:]:n['injured_opening'].append(name+'：我现在需要休养，工作的安排先按已经确认的记录谈。')
scripts['version']=V;scripts['fact_selection']='later_breach按当事人已知的真实归责选择self/other/unknown；还要附事件摘要。不能因为出现冲突一律让角色自责。临时重伤使用injured_opening，永久离队只读来信。'
write(p,scripts)
p=F/'stories.json';st=json.loads(p.read_text());st['version']=V
for n in st['personal_nodes']:
 if n['id']=='P_mo_2':
  n['publication_followthrough']='选择redact只创建计划。此后由玩家在营地另安排一次脱敏核验发布（1项目、莫遥可工作、已有核实资料、同资料不可重复），或在M22实际完成privacy目标。不能在许诺时自动签发发布凭据。'
 st['audit_rules']['first_choice']='第1段记录玩家实际选项；不默认覆盖为第一个选项。'
st['audit_rules']['injury_and_responsibility']='临时重伤使用受伤开场；后续冲突按已知责任读文本；没有确证不能自动写自责或指责。'
write(p,st)
p=F/'combat.json';d=json.loads(p.read_text());d['version']=V;d['blocked_objectives']='前置目标在完成前永久丧失，所有依赖它且尚未完成的目标同步标记本任务不可达，记录具体前置原因。只失去任务机会，不虚构物品物理毁坏或居民死亡；完成过的里程碑不被追溯删除。玩家可做其他目标或撤离，不必等倒计时结束。';d['transport_credit']='许舟携带抛索和江朔远距交接按实际货物位移写transport_path，与步行共用回环消除和目标唯一ID；重复交接不能刷贡献。';write(p,d)
p=ROOT/'game/data/campaign_economy_contract.json';d=json.loads(p.read_text());d['version']=V;d['purchase_undo']='非初始永久工具在购买后尚未参加任何新任务时，可撤销误购。只退实际已付资金/零件，恢复该笔占用的工坊折扣；撤销已发凭据不可重复。出勤后不回购，消耗品、设施与已执行培养不按此规则退款。';write(p,d)
p=F/'player_ready_contract.json';d=json.loads(p.read_text());d['version']=V;d['guidance']['blocked_chain']='前置永久失败时，一次合并提示依赖链与仍可保住的成果，提供继续/撤离/查看原因；不反复弹窗，不锁住基础行动。';d['preview']+=['持续保全目标即使已完成施工也保持受威胁图标，显示下一次已知伤害与剩余HP；不与已交付永久成果混淆','支线明示开放到次日；今天人手不足可保留明日入口，过期才记错失','训练同时预览下一次计划出勤的疲劳，不把经验跨级当成唯一推荐依据','新购工具尚未出勤可撤销；退回实际支付，购买界面不推荐无近期用途的装备'];d['preview']=list(dict.fromkeys(d['preview']));write(p,d)
m=F/'design_manifest.json';d=json.loads(m.read_text());d['version']=V;d['domains']['ordinary_play_review']='ordinary_player_contract.json';write(m,d)
write(F/'ordinary_player_contract.json',dict(version=V,formal_development=False,coverage='All108authored goal/optional-intention combinations;46goalbranches; all date-legal trios tested on separate axis. Not all action sequences.',behavioral_evidence='Fixed ahead-of-time policies, local map/path decisions, no hindsight result ranking. Cases are not measured human success probabilities.',resolved=['lost-prerequisite propagation','actual first-stage choice saved','Mo plan versus publication','responsibility-aware breach dialogue','injured opening','specialty transport credit','unused tool purchase undo'],authority='Other domains remain as0.15 unless explicitly revised here. Economy incomes retained pending non-optimal campaign findings.'))
print('Applied0.16 fixes')
p=F/'character_scripts.json';scripts=json.loads(p.read_text())
for n in scripts['personal']:
 name=names[n['actor']]
 n['later_breach_shared']=name+'：其中属于我的责任，我会承担；其他部分按证据分别说清，不能合成某一个人的全部过错。'
 n['injured_choices']={key:[t.replace('今天这一班我会做完','当前班次先按我的伤势交接').replace('我继续做调度','恢复后我继续做调度') for t in lines if '：' in t]+['本次只记录意愿和安排；现场职责由可出勤者接替，恢复日期仍按伤势结算。'] for key,lines in n['choices'].items()}
write(p,scripts)
