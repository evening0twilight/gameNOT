from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design'
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'work/growth-identity-review/model.py';s=p.read_text()
s=s.replace("elif key=='he_1':self.barriers[tuple(destination)]['expires']=999", "elif key=='he_1':self.barriers[tuple(destination)].update(expires=999,hp=5)")
s=s.replace("distance(h['p'],e['p'])==1\n  e['output_isolated']", "distance(h['p'],e['p'])<=(2 if h['level']>=5 else 1)\n  e['output_isolated']")
s=s.replace("if distance(h['p'],target['p'])==1 and h['ap']>=2:self.cast(h,'ye_1',target['id'])", "if distance(h['p'],target['p'])<=(2 if h['level']>=5 else 1) and h['ap']>=2:self.cast(h,'ye_1',target['id'])")
needle="  e['output_isolated']=True"
geometry="""  if distance(h['p'],e['p'])==2:
   assert h['p'][0]==e['p'][0] or h['p'][1]==e['p'][1]
   mid=((h['p'][0]+e['p'][0])//2,(h['p'][1]+e['p'][1])//2)
   assert self.passable(mid) and not self.occupied(mid) and mid not in self.barriers
"""
if "if distance(h['p'],e['p'])==2:" not in s:s=s.replace(needle,geometry+needle)
p.write_text(s)
p=F/'abilities.json';a=json.loads(p.read_text())
for x in a:
 if x['id']=='he_1':x['level5_effect']='5级：屏障持续本任务、HP3→5，仍花1AP、每任务2次，不阻止爆炸/水火，也不能回收刷满。普通可购盾板仍为替代方案。'
 if x['id']=='ye_1':x['level5_effect']='5级：危险输出隔离距离1→2；两格必须直线，中间为无人、无墙/机器/屏障的可通行格。仍花2AP、每任务1次；保留供电、已有火焰与增援不消失。不是远程完成任务。'
put(p,a)
p=F/'growth_identity_contract.json';d=json.loads(p.read_text());d['version']='0.16-ordinary-player'
for x in a:
 if x.get('production_status')=='active' and x.get('level5_effect'):d['level5'][x['id']]=x['level5_effect']
d['training']['recommendation']='默认自然出勤成长。仅在玩家已计划的下一任务之前能取得具体专长用途、且训练后不会因此失去计划出勤资格时，显示一次可选训练建议；任务未公开或用途不明时直接写“不确定本次额外训练收益”。不以总经验最大化催促每天训练。显示不训练/训练各自到达等级的日期区间、1物资/1项目/+8疲劳和替代休息。'
d['ordinary_growth_findings']='30条真实培养对照显示额外训练并不普遍划算；不把自然出勤成长价值与额外付费训练价值混为一谈。贺鸣五级屏障增加到5HP，叶禾五级隔离扩到2格；其余职业价值按具体任务条件提示，不全员普涨数值。'
put(p,d)
p=F/'player_ready_contract.json';d=json.loads(p.read_text());d['guidance']['specialty_examples']='角色首次有明确可用目标时，技能卡展开一个条件实例：叶禾“隔离危险输出但保电，2AP”，贺鸣“这面屏障能承受哪些已知射线”，莫遥“远程处理已知开关”，江朔“交接空位与接收者AP”。遵守每关提示总额度，不另叠8套弹窗；只是展示，玩家可继续普通解法。';d['preview']=list(dict.fromkeys(d['preview']));put(p,d)
print('RefinedHe/YeL5 andtrainingrecommendations')
