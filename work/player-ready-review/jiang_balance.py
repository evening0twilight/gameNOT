from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design'
p=ROOT/'work/growth-identity-review/model.py';s=p.read_text()
a=s.index("   if h['level']>=5 and key=='jiang_1':");b=s.index('   try:result=',a)
s=s[:a]+"""   if h['level']>=3 and key=='jiang_1':
    y=self.h[target];d=distance(h['p'],y['p']);reach=3 if h['level']>=5 else 2
    assert d<=reach
    if d>1:
     assert h['p'][0]==y['p'][0] or h['p'][1]==y['p'][1]
     dx=0 if h['p'][0]==y['p'][0] else 1 if y['p'][0]>h['p'][0] else -1
     dy=0 if h['p'][1]==y['p'][1] else 1 if y['p'][1]>h['p'][1] else -1
     cells=[(h['p'][0]+dx*i,h['p'][1]+dy*i) for i in range(1,d)]
     assert all(self.passable(mid) and self.rows[mid[1]][mid[0]]=='.' and not self.occupied(mid) for mid in cells)
    ABILITIES[key]['range']=reach
"""+s[b:]
s=s.replace("if self.skills_enabled and h['level']>=5 and h['carry'] and h['name']=='jiang'", "if self.skills_enabled and h['level']>=3 and h['carry'] and h['name']=='jiang'")
s=s.replace("distance(h['p'],y['p'])==2 and d(y)<d(h)", "2<=distance(h['p'],y['p'])<=(3 if h['level']>=5 else 2) and d(y)<d(h)")
p.write_text(s)
p=F/'abilities.json';a=json.loads(p.read_text())
for x in a:
 if x['id']=='jiang_1':x['level3_effect']='3级交接距离1→2，直线中间格必须为空干地。';x['level5_effect']='5级交接距离2→3，所有中间格必须是无人、无机器、无墙、无深水的可通行干地。原AP、任务2次、空手自愿接收及关系条件不变。'
p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
p=F/'growth_identity_contract.json';g=json.loads(p.read_text());g['level3_modifiers']={'jiang_1':next(x['level3_effect'] for x in a if x['id']=='jiang_1')};g['level5']['jiang_1']=next(x['level5_effect'] for x in a if x['id']=='jiang_1');g['balance_policy']+=' 江朔较晚加入，将2格交接提前到3级（加入时已具备），5级为3格；仍不穿越障碍。';p.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
print('Jiang range progression 1/2/3')
