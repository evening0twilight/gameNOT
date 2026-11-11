"""Finish observed design/referee boundary fixes; no game runtime edits."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];F=R/'game/data/final_design'
p=R/'outputs/ordinary-player-opportunities.json';old=R/'outputs/ordinary-player-before-opportunities.json'
if not old.exists():old.write_bytes(p.read_bytes())
p=R/'work/ordinary-player-review/opportunities.py';s=p.read_text().replace('  if self.spec:\n','  if self.spec and not self.service_done and not self.service_failed and self.rnd<=self.spec[\'deadline\']:\n');p.write_text(s)
p=R/'work/growth-identity-review/model.py';s=p.read_text();old="if h['name']=='ye' and self.role_policy=='isolation' and self.used.get((h['id'],'ye_1'),0)<1:"
new="if h['name']=='ye' and self.role_policy=='isolation' and self.used.get((h['id'],'ye_1'),0)<1 and any(not o['done'] and not o['secured'] and not o['lost'] for k,o in self.objects.items() if k in self.wanted):"
s=s.replace(old,new);p.write_text(s)
p=R/'work/growth-identity-review/relationships.py';s=p.read_text();needle=' def medical_pack_limit(self):'
patch=""" @atomic_identity
 def craft(self,item,n):
  assert item=='med_dose','retired consumable'
  return super().craft(item,n)
 @atomic_identity
 def buy_tool(self,item):
  assert next(e for e in json.loads((ROOT/'game/data/final_design/equipment.json').read_text())['items'] if e['id']==item).get('production_status','active')=='active','retired tool'
  return super().buy_tool(item)
"""
if "'retired consumable'" not in s:s=s.replace(needle,patch+needle)
s=s.replace(' def deploy(self,mid,party,support=None,pack=None):\n  chosen='," def deploy(self,mid,party,support=None,pack=None):\n  assert set(pack or {})<={'med_dose'},'retired packed consumable'\n  chosen=");p.write_text(s)
for file in ['player_ready_contract.json','ordinary_player_contract.json']:
 p=F/file;d=json.loads(p.read_text());d['version']='0.16-ordinary-player'
 d['hint_lifetime']='提示绑定具体目标和当前可用动作。目标完成、不可达、时限过期或玩家切换目标时立即撤下；不因技能尚未使用而继续建议。首次提示仍占该关原有提示额度。'
 d['retired_inventory']='当前出勤物品只接受已启用工具与med_dose；历史消耗品和已删工具不能从制作、购买或装包接口重新进入当前方案。'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print('Closed stale guidance and retired inventory paths')
