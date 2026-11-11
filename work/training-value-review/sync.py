from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];F=ROOT/'game/data/final_design';O=ROOT/'outputs'
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=F/'training_value_contract.json';d=json.loads(p.read_text());d.update(review_status='Current finite offline review; not human playtest',fatigue_preview='显示当前疲劳、训练+6、已知夜间恢复、下次计划任务消耗；如果本可专门恢复，还显示放弃的-12。换人/改项目后重新计算，不承诺未知事件后的状态。',injury_and_save='普通重伤保留经验与已用阶段，休养恢复后可继续；最高难度永久离队不把培养转移给其他人。已完成训练不单独返现；完整读档须恢复XP/阶段/资源/回执的一致时间点。',investment_scope='课程不强制买满；即时学习本人高阶能力只是可用机会，不保证每种路线都有战术增益。未计划启用或已自然及时跨级者可以完整保留阶段。',mentor_recommendation='只有实际增益高于普通训练才提供；并列展示普通/带教实际跨级及导师当晚代价，不以最大经验数字默认选带教。');put(p,d)
p=F/'ordinary_player_contract.json';d=json.loads(p.read_text());d['training_reference']='训练已由0.17 training_value_contract替换；0.16的3经验/8疲劳结果仅作历史对照。';put(p,d)
p=ROOT/'work/final-design/build_report.py';s=p.read_text().replace("'0.15','0.16'","'0.15','0.16','0.17'").replace('训练每人1物资/+8疲劳/+3经验','阶段训练每人1物资/+6疲劳/+12经验；每章开放1阶段、未用保留，带教与普通训练共用学员阶段');p.write_text(s)
for name in ['training-campaigns.json','training-general-campaigns.json']:
 p=O/name;d=json.loads(p.read_text());d['version']='0.17';put(p,d)
print('Syncedcurrenttrainingauthority')
